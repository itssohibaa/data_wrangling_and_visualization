import streamlit as st
import pandas as pd
import numpy as np

# --- SESSION INIT ---
for key, default in [("df", None), ("log", []), ("history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("🧹 Data Cleaning & Preparation Studio")

if st.session_state.df is None:
    st.warning("⚠️ Please upload a dataset first on the Upload page.")
    st.stop()

df = st.session_state.df.copy()

# ===============================
# 🔹 UNDO
# ===============================
col_undo, col_info = st.columns([1, 4])
with col_undo:
    if st.button("↩️ Undo Last Step"):
        if len(st.session_state.history) > 1:
            st.session_state.history.pop()
            st.session_state.df = st.session_state.history[-1].copy()
            st.session_state.log.append("↩️ Undid last step")
            st.rerun()
        else:
            st.warning("Nothing to undo.")
with col_info:
    st.caption(f"📝 Transformation steps logged: {len(st.session_state.log)}")

st.markdown("---")

# ===============================
# 🔹 DATASET PREVIEW
# ===============================
st.subheader("📋 Current Dataset")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{df.shape[0]:,}")
c2.metric("Columns", df.shape[1])
c3.metric("Missing Cells", int(df.isnull().sum().sum()))
c4.metric("Duplicates", int(df.duplicated().sum()))
st.dataframe(df.head(), use_container_width=True)

st.markdown("---")

# ===============================
# 🔹 SECTION 1: MISSING VALUES
# ===============================
with st.expander("🔍 Missing Values Handling", expanded=True):
    missing_summary = pd.DataFrame({
        "Missing Count": df.isnull().sum(),
        "Missing %": (df.isnull().sum() / len(df) * 100).round(2)
    })
    missing_cols = missing_summary[missing_summary["Missing Count"] > 0]

    if missing_cols.empty:
        st.success("✅ No missing values in this dataset!")
    else:
        st.write("**Columns with missing values:**")
        st.dataframe(missing_cols, use_container_width=True)

        col = st.selectbox("Select column to handle", missing_cols.index.tolist(), key="mv_col")
        col_type = df[col].dtype

        st.info(f"Column `{col}` — type: `{col_type}` — {int(df[col].isnull().sum())} missing values")

        if col_type == "object" or str(col_type) == "category":
            method = st.selectbox("Fill method", ["Drop rows", "Mode (most frequent)", "Constant value",
                                                   "Forward Fill", "Backward Fill"], key="mv_method_cat")
        else:
            method = st.selectbox("Fill method", ["Drop rows", "Mean", "Median", "Mode (most frequent)",
                                                   "Constant value", "Forward Fill", "Backward Fill"], key="mv_method_num")

        const_value = ""
        if method == "Constant value":
            const_value = st.text_input("Enter constant value", key="mv_const")

        if st.button("✅ Apply Missing Value Handling", key="mv_apply"):
            st.session_state.history.append(df.copy())
            before = int(df[col].isnull().sum())
            try:
                if method == "Drop rows":
                    df = df.dropna(subset=[col])
                elif method == "Mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif method == "Median":
                    df[col] = df[col].fillna(df[col].median())
                elif method == "Mode (most frequent)":
                    df[col] = df[col].fillna(df[col].mode()[0])
                elif method == "Constant value":
                    try:
                        fill_val = float(const_value) if df[col].dtype != object else const_value
                    except ValueError:
                        fill_val = const_value
                    df[col] = df[col].fillna(fill_val)
                elif method == "Forward Fill":
                    df[col] = df[col].ffill()
                elif method == "Backward Fill":
                    df[col] = df[col].bfill()

                after = int(df[col].isnull().sum())
                st.session_state.df = df
                st.session_state.log.append(f"Missing values in '{col}' handled with: {method}")
                st.success(f"✅ Fixed {before - after} missing values in '{col}' (was {before}, now {after})")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ===============================
# 🔹 SECTION 2: DUPLICATES (FIX #5)
# ===============================
with st.expander("🔁 Duplicate Detection & Treatment", expanded=True):
    total_dupes = int(df.duplicated().sum())
    st.metric("Total duplicate rows (full match)", total_dupes)

    dup_mode = st.radio("Detect duplicates by:", ["Full row", "Subset of columns"], key="dup_mode", horizontal=True)

    subset_cols = None
    if dup_mode == "Subset of columns":
        subset_cols = st.multiselect("Select key columns for duplicate check", df.columns.tolist(), key="dup_subset")

    if subset_cols is not None and len(subset_cols) == 0 and dup_mode == "Subset of columns":
        st.warning("Please select at least one column.")
    else:
        check_subset = subset_cols if (dup_mode == "Subset of columns" and subset_cols) else None
        n_dupes = int(df.duplicated(subset=check_subset).sum())
        st.info(f"Found **{n_dupes}** duplicate row(s) with current selection.")

        action = st.selectbox("Action", ["Show duplicate groups", "Remove duplicates (keep first)",
                                          "Remove duplicates (keep last)"], key="dup_action")

        if st.button("✅ Apply Duplicate Action", key="dup_apply"):
            st.session_state.history.append(df.copy())
            try:
                if action == "Show duplicate groups":
                    mask = df.duplicated(subset=check_subset, keep=False)
                    dup_groups = df[mask]
                    if dup_groups.empty:
                        st.success("No duplicates found!")
                    else:
                        st.write(f"**{len(dup_groups)} rows involved in duplicates:**")
                        st.dataframe(dup_groups.sort_values(by=df.columns[0]).head(100), use_container_width=True)
                elif action == "Remove duplicates (keep first)":
                    before = len(df)
                    df = df.drop_duplicates(subset=check_subset, keep="first")
                    st.session_state.df = df
                    st.session_state.log.append(f"Removed duplicates (keep first) — subset: {check_subset or 'all columns'}")
                    st.success(f"✅ Removed {before - len(df)} duplicate rows. Dataset now has {len(df):,} rows.")
                    st.rerun()
                elif action == "Remove duplicates (keep last)":
                    before = len(df)
                    df = df.drop_duplicates(subset=check_subset, keep="last")
                    st.session_state.df = df
                    st.session_state.log.append(f"Removed duplicates (keep last) — subset: {check_subset or 'all columns'}")
                    st.success(f"✅ Removed {before - len(df)} duplicate rows. Dataset now has {len(df):,} rows.")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ===============================
# 🔹 SECTION 3: SCALING
# ===============================
with st.expander("📐 Scaling & Normalization"):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()

    if not num_cols:
        st.warning("No numeric columns found.")
    else:
        scale_cols = st.multiselect("Columns to scale", num_cols, key="scale_cols")
        method_scale = st.selectbox("Scaling method", ["Min-Max (0–1)", "Z-score standardization"], key="scale_method")

        if scale_cols:
            st.write("**Before scaling:**")
            st.dataframe(df[scale_cols].describe().T[["mean", "std", "min", "max"]], use_container_width=True)

        if st.button("✅ Apply Scaling", key="scale_apply") and scale_cols:
            st.session_state.history.append(df.copy())
            try:
                for c in scale_cols:
                    if method_scale == "Min-Max (0–1)":
                        mn, mx = df[c].min(), df[c].max()
                        df[c] = (df[c] - mn) / (mx - mn) if mx != mn else 0
                    else:
                        df[c] = (df[c] - df[c].mean()) / df[c].std()

                st.session_state.df = df
                st.session_state.log.append(f"Scaled {scale_cols} using {method_scale}")
                st.success(f"✅ Scaling applied to: {', '.join(scale_cols)}")
                st.write("**After scaling:**")
                st.dataframe(df[scale_cols].describe().T[["mean", "std", "min", "max"]], use_container_width=True)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ===============================
# 🔹 SECTION 4: COLUMN OPERATIONS
# ===============================
with st.expander("🔧 Column Operations"):
    op = st.selectbox("Operation", ["Rename column", "Drop column(s)", "Change column type"], key="col_op")

    if op == "Rename column":
        old_name = st.selectbox("Column to rename", df.columns.tolist(), key="rename_col")
        new_name = st.text_input("New name", key="rename_new")
        if st.button("✅ Rename", key="rename_apply") and new_name:
            st.session_state.history.append(df.copy())
            df = df.rename(columns={old_name: new_name})
            st.session_state.df = df
            st.session_state.log.append(f"Renamed '{old_name}' → '{new_name}'")
            st.success(f"✅ Renamed '{old_name}' to '{new_name}'")
            st.rerun()

    elif op == "Drop column(s)":
        drop_cols = st.multiselect("Columns to drop", df.columns.tolist(), key="drop_cols")
        if st.button("✅ Drop", key="drop_apply") and drop_cols:
            st.session_state.history.append(df.copy())
            df = df.drop(columns=drop_cols)
            st.session_state.df = df
            st.session_state.log.append(f"Dropped columns: {drop_cols}")
            st.success(f"✅ Dropped: {', '.join(drop_cols)}")
            st.rerun()

    elif op == "Change column type":
        type_col = st.selectbox("Column", df.columns.tolist(), key="type_col")
        target_type = st.selectbox("Convert to", ["numeric", "string/text", "datetime", "category"], key="target_type")
        if st.button("✅ Convert", key="type_apply"):
            st.session_state.history.append(df.copy())
            try:
                if target_type == "numeric":
                    df[type_col] = pd.to_numeric(df[type_col], errors="coerce")
                elif target_type == "string/text":
                    df[type_col] = df[type_col].astype(str)
                elif target_type == "datetime":
                    df[type_col] = pd.to_datetime(df[type_col], errors="coerce")
                elif target_type == "category":
                    df[type_col] = df[type_col].astype("category")
                st.session_state.df = df
                st.session_state.log.append(f"Converted '{type_col}' to {target_type}")
                st.success(f"✅ '{type_col}' converted to {target_type}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# ===============================
# 🔹 FINAL PREVIEW
# ===============================
st.subheader("✅ Updated Dataset")
st.dataframe(st.session_state.df.head(10), use_container_width=True)

# ===============================
# 🔹 TRANSFORMATION LOG
# ===============================
if st.session_state.log:
    with st.expander("📝 Transformation Log"):
        for i, step in enumerate(st.session_state.log, 1):
            st.write(f"{i}. {step}")
