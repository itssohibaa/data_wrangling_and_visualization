import streamlit as st
import pandas as pd
import numpy as np

for k, v in [("df", None), ("log", []), ("history", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

st.title("🧹 Cleaning & Preparation Studio")

if st.session_state.df is None:
    st.warning("Please upload a dataset first."); st.stop()

df = st.session_state.df.copy()

# ── UNDO + STATUS BAR ─────────────────────────────────────────────────────────
c1, c2 = st.columns([1, 4])
with c1:
    if st.button("↩️ Undo Last Step"):
        if len(st.session_state.history) > 1:
            st.session_state.history.pop()
            st.session_state.df = st.session_state.history[-1].copy()
            st.rerun()
        else:
            st.warning("Nothing to undo.")
with c2:
    st.caption(f"Steps logged: {len(st.session_state.log)}  |  "
               f"Rows: {df.shape[0]:,}  |  Cols: {df.shape[1]}  |  "
               f"Missing: {int(df.isnull().sum().sum()):,}  |  "
               f"Duplicates: {int(df.duplicated().sum()):,}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. MISSING VALUES
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔍 1. Missing Values", expanded=True):
    mv = pd.DataFrame({
        "Missing Count": df.isnull().sum(),
        "Missing %": (df.isnull().sum() / len(df) * 100).round(2)
    })
    mv_f = mv[mv["Missing Count"] > 0]
    if mv_f.empty:
        st.success("No missing values!")
    else:
        st.dataframe(
    mv_f.style.background_gradient(cmap="Reds", subset=["Missing %"])
              .format({"Missing Count": "{:,.0f}", "Missing %": "{:.2f}%"}),
    use_container_width=True
)
        col = st.selectbox("Column to fix", mv_f.index.tolist(), key="mv_col")
        ctype = df[col].dtype
        st.info(f"`{col}` — type: `{ctype}` — {int(df[col].isnull().sum())} missing")

        opts = ["Drop rows", "Mode (most frequent)", "Constant value", "Forward Fill", "Backward Fill"]
        if ctype != object:
            opts = ["Drop rows", "Mean", "Median", "Mode (most frequent)",
                    "Constant value", "Forward Fill", "Backward Fill"]
        method = st.selectbox("Fill method", opts, key="mv_method")
        const_val = st.text_input("Constant value", key="mv_const") if method == "Constant value" else ""

        if st.button("Apply Missing Value Fix", key="mv_apply"):
            st.session_state.history.append(df.copy())
            before = int(df[col].isnull().sum())
            try:
                if method == "Drop rows":              df = df.dropna(subset=[col])
                elif method == "Mean":                 df[col] = df[col].fillna(df[col].mean())
                elif method == "Median":               df[col] = df[col].fillna(df[col].median())
                elif method == "Mode (most frequent)": df[col] = df[col].fillna(df[col].mode()[0])
                elif method == "Constant value":
                    try:    fill = float(const_val) if df[col].dtype != object else const_val
                    except: fill = const_val
                    df[col] = df[col].fillna(fill)
                elif method == "Forward Fill":  df[col] = df[col].ffill()
                elif method == "Backward Fill": df[col] = df[col].bfill()
                after = int(df[col].isnull().sum())
                st.session_state.df = df
                st.session_state.log.append(f"Missing values in '{col}' handled with {method}")
                st.success(f"Fixed {before - after} missing values (was {before}, now {after})")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. DUPLICATES
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔁 2. Duplicate Detection & Treatment", expanded=False):
    total_d = int(df.duplicated().sum())
    st.metric("Full-row duplicates", total_d)

    dup_mode = st.radio("Detect by", ["Full row", "Subset of columns"], horizontal=True, key="dup_mode")
    subset = None
    if dup_mode == "Subset of columns":
        subset = st.multiselect("Key columns", df.columns.tolist(), key="dup_subset")

    check_subset = subset if (dup_mode == "Subset of columns" and subset) else None
    n_d = int(df.duplicated(subset=check_subset).sum())
    st.info(f"Found **{n_d}** duplicate(s) with current selection.")

    action = st.selectbox("Action", [
        "Show duplicate groups",
        "Remove duplicates (keep first)",
        "Remove duplicates (keep last)"
    ], key="dup_action")

    if st.button("Apply", key="dup_apply"):
        st.session_state.history.append(df.copy())
        try:
            if action == "Show duplicate groups":
                mask = df.duplicated(subset=check_subset, keep=False)
                g = df[mask]
                st.write(f"{len(g)} rows involved:"); st.dataframe(g.head(100), use_container_width=True)
            else:
                keep = "first" if "first" in action else "last"
                before = len(df)
                df = df.drop_duplicates(subset=check_subset, keep=keep)
                st.session_state.df = df
                st.session_state.log.append(f"Removed duplicates ({keep}) — subset: {check_subset or 'all'}")
                st.success(f"Removed {before - len(df)} rows. Now {len(df):,} rows.")
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. CATEGORICAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🏷️ 3. Categorical Tools", expanded=False):
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        st.info("No categorical columns found.")
    else:
        cat_op = st.selectbox("Operation", [
            "Standardize casing / trim whitespace",
            "Map / replace values",
            "Group rare categories into 'Other'",
            "One-hot encoding"
        ], key="cat_op")
        cat_col = st.selectbox("Column", cat_cols, key="cat_col")

        if cat_op == "Standardize casing / trim whitespace":
            casing = st.selectbox("Apply", ["Trim whitespace only", "lowercase", "UPPERCASE", "Title Case"], key="cat_case")
            if st.button("Apply Standardization", key="cat_std"):
                st.session_state.history.append(df.copy())
                df[cat_col] = df[cat_col].astype(str).str.strip()
                if casing == "lowercase":     df[cat_col] = df[cat_col].str.lower()
                elif casing == "UPPERCASE":   df[cat_col] = df[cat_col].str.upper()
                elif casing == "Title Case":  df[cat_col] = df[cat_col].str.title()
                st.session_state.df = df
                st.session_state.log.append(f"Standardized casing of '{cat_col}': {casing}")
                st.success("Done!"); st.rerun()

        elif cat_op == "Map / replace values":
            unique_vals = df[cat_col].dropna().unique().tolist()
            st.caption(f"Unique values in `{cat_col}`: {unique_vals[:20]}")
            from_val = st.selectbox("Replace this value", unique_vals, key="map_from")
            to_val   = st.text_input("With this value", key="map_to")
            if st.button("Apply Mapping", key="cat_map") and to_val:
                st.session_state.history.append(df.copy())
                df[cat_col] = df[cat_col].replace({from_val: to_val})
                st.session_state.df = df
                st.session_state.log.append(f"Mapped '{from_val}' → '{to_val}' in '{cat_col}'")
                st.success("Done!"); st.rerun()

        elif cat_op == "Group rare categories into 'Other'":
            freq_thresh = st.slider("Group categories appearing less than N times", 1, 100, 10, key="rare_thresh")
            counts = df[cat_col].value_counts()
            rare = counts[counts < freq_thresh].index.tolist()
            st.info(f"{len(rare)} rare categories will be grouped: {rare[:10]}")
            if st.button("Apply Rare Grouping", key="cat_rare"):
                st.session_state.history.append(df.copy())
                df[cat_col] = df[cat_col].apply(lambda x: "Other" if x in rare else x)
                st.session_state.df = df
                st.session_state.log.append(f"Grouped {len(rare)} rare categories in '{cat_col}' into 'Other'")
                st.success("Done!"); st.rerun()

        elif cat_op == "One-hot encoding":
            st.info(f"Will create binary columns for each unique value in `{cat_col}`.")
            drop_orig = st.checkbox("Drop original column after encoding", value=True, key="ohe_drop")
            if st.button("Apply One-Hot Encoding", key="cat_ohe"):
                st.session_state.history.append(df.copy())
                dummies = pd.get_dummies(df[cat_col], prefix=cat_col, dtype=int)
                df = pd.concat([df, dummies], axis=1)
                if drop_orig: df = df.drop(columns=[cat_col])
                st.session_state.df = df
                st.session_state.log.append(f"One-hot encoded '{cat_col}' — {len(dummies.columns)} new columns")
                st.success(f"Created {len(dummies.columns)} new columns!"); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 4. OUTLIER DETECTION & TREATMENT
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📦 4. Outlier Detection & Treatment", expanded=False):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not num_cols:
        st.info("No numeric columns.")
    else:
        out_col    = st.selectbox("Column", num_cols, key="out_col")
        out_method = st.radio("Detection method", ["IQR (1.5×)", "Z-score (threshold 3)"], horizontal=True, key="out_method")
        series     = df[out_col].dropna()

        if out_method == "IQR (1.5×)":
            Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
            IQR = Q3 - Q1
            mask = (df[out_col] < Q1 - 1.5*IQR) | (df[out_col] > Q3 + 1.5*IQR)
            lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
        else:
            z = (df[out_col] - series.mean()) / series.std()
            mask = z.abs() > 3
            lower, upper = series.mean() - 3*series.std(), series.mean() + 3*series.std()

        n_out = int(mask.sum())
        st.metric("Outliers detected", n_out)
        st.caption(f"Valid range: {lower:.2f} → {upper:.2f}")

        action = st.selectbox("Action", [
            "Do nothing (just view)",
            "Remove outlier rows",
            "Cap (winsorize) to boundary values"
        ], key="out_action")

        if st.button("Apply Outlier Action", key="out_apply"):
            st.session_state.history.append(df.copy())
            if action == "Remove outlier rows":
                df = df[~mask]
                st.session_state.df = df
                st.session_state.log.append(f"Removed {n_out} outlier rows from '{out_col}'")
                st.success(f"Removed {n_out} rows."); st.rerun()
            elif action == "Cap (winsorize) to boundary values":
                df[out_col] = df[out_col].clip(lower=lower, upper=upper)
                st.session_state.df = df
                st.session_state.log.append(f"Winsorized '{out_col}' to [{lower:.2f}, {upper:.2f}]")
                st.success(f"Capped {n_out} values."); st.rerun()
            else:
                st.info("No changes made.")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. SCALING / NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📐 5. Scaling & Normalization", expanded=False):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not num_cols:
        st.info("No numeric columns.")
    else:
        scale_cols   = st.multiselect("Columns to scale", num_cols, key="scale_cols")
        scale_method = st.selectbox("Method", ["Min-Max (0–1)", "Z-score standardization"], key="scale_method")

        if scale_cols:
            st.write("**Before:**")
            st.dataframe(df[scale_cols].describe().T[["mean","std","min","max"]], use_container_width=True)

        if st.button("Apply Scaling", key="scale_apply") and scale_cols:
            st.session_state.history.append(df.copy())
            for c in scale_cols:
                if scale_method == "Min-Max (0–1)":
                    mn, mx = df[c].min(), df[c].max()
                    df[c] = (df[c] - mn) / (mx - mn) if mx != mn else 0
                else:
                    df[c] = (df[c] - df[c].mean()) / df[c].std()
            st.session_state.df = df
            st.session_state.log.append(f"Scaled {scale_cols} using {scale_method}")
            st.success("Scaling applied!")
            st.write("**After:**")
            st.dataframe(df[scale_cols].describe().T[["mean","std","min","max"]], use_container_width=True)
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 6. COLUMN OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔧 6. Column Operations", expanded=False):
    col_op = st.selectbox("Operation", [
        "Rename column",
        "Drop column(s)",
        "Change column type",
        "Create new column (formula)",
        "Bin numeric column into categories"
    ], key="col_op")

    if col_op == "Rename column":
        old = st.selectbox("Column to rename", df.columns.tolist(), key="ren_old")
        new = st.text_input("New name", key="ren_new")
        if st.button("Rename", key="ren_apply") and new:
            st.session_state.history.append(df.copy())
            df = df.rename(columns={old: new})
            st.session_state.df = df
            st.session_state.log.append(f"Renamed '{old}' → '{new}'")
            st.success("Done!"); st.rerun()

    elif col_op == "Drop column(s)":
        drop_cols = st.multiselect("Columns to drop", df.columns.tolist(), key="drop_cols")
        if st.button("Drop", key="drop_apply") and drop_cols:
            st.session_state.history.append(df.copy())
            df = df.drop(columns=drop_cols)
            st.session_state.df = df
            st.session_state.log.append(f"Dropped columns: {drop_cols}")
            st.success("Done!"); st.rerun()

    elif col_op == "Change column type":
        type_col  = st.selectbox("Column", df.columns.tolist(), key="type_col")
        tgt_type  = st.selectbox("Convert to", ["numeric", "string", "datetime", "category"], key="tgt_type")
        if st.button("Convert", key="type_apply"):
            st.session_state.history.append(df.copy())
            try:
                if tgt_type == "numeric":  df[type_col] = pd.to_numeric(df[type_col], errors="coerce")
                elif tgt_type == "string": df[type_col] = df[type_col].astype(str)
                elif tgt_type == "datetime": df[type_col] = pd.to_datetime(df[type_col], errors="coerce")
                elif tgt_type == "category": df[type_col] = df[type_col].astype("category")
                st.session_state.df = df
                st.session_state.log.append(f"Converted '{type_col}' to {tgt_type}")
                st.success("Done!"); st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    elif col_op == "Create new column (formula)":
        st.caption("Use column names as variables. Examples: `salary / age`, `log(salary)`, `salary - salary.mean()`")
        new_col_name = st.text_input("New column name", key="new_col_name")
        formula      = st.text_input("Formula (use column names directly)", key="formula")
        if st.button("Create Column", key="new_col_apply") and new_col_name and formula:
            st.session_state.history.append(df.copy())
            try:
                local_vars = {c: df[c] for c in df.columns}
                import math
                local_vars.update({"log": np.log, "sqrt": np.sqrt, "abs": np.abs,
                                   "exp": np.exp, "mean": np.mean})
                df[new_col_name] = eval(formula, {"__builtins__": {}}, local_vars)
                st.session_state.df = df
                st.session_state.log.append(f"Created column '{new_col_name}' = {formula}")
                st.success(f"Column '{new_col_name}' created!"); st.rerun()
            except Exception as e:
                st.error(f"Formula error: {e}")

    elif col_op == "Bin numeric column into categories":
        num_cols_bin = df.select_dtypes(include=np.number).columns.tolist()
        if not num_cols_bin:
            st.info("No numeric columns.")
        else:
            bin_col   = st.selectbox("Column to bin", num_cols_bin, key="bin_col")
            bin_n     = st.slider("Number of bins", 2, 20, 5, key="bin_n")
            bin_strat = st.radio("Strategy", ["Equal-width bins", "Quantile bins (equal-frequency)"],
                                 horizontal=True, key="bin_strat")
            bin_labels = st.text_input("Custom labels (comma-separated, optional)", key="bin_labels")
            new_bin_col = st.text_input("New column name", value=f"{bin_col}_binned", key="bin_new_col")

            if st.button("Apply Binning", key="bin_apply"):
                st.session_state.history.append(df.copy())
                try:
                    labels = [l.strip() for l in bin_labels.split(",")] if bin_labels else None
                    if labels and len(labels) != bin_n:
                        st.error(f"Need exactly {bin_n} labels, got {len(labels)}.")
                    else:
                        if bin_strat == "Equal-width bins":
                            df[new_bin_col] = pd.cut(df[bin_col], bins=bin_n, labels=labels)
                        else:
                            df[new_bin_col] = pd.qcut(df[bin_col], q=bin_n, labels=labels, duplicates="drop")
                        st.session_state.df = df
                        st.session_state.log.append(f"Binned '{bin_col}' into '{new_bin_col}' ({bin_strat})")
                        st.success("Done!"); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. DATA VALIDATION RULES
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("✅ 7. Data Validation Rules", expanded=False):
    val_type = st.selectbox("Validation type", [
        "Numeric range check (min / max)",
        "Allowed categories list",
        "Non-null constraint"
    ], key="val_type")

    if val_type == "Numeric range check (min / max)":
        num_cols_v = df.select_dtypes(include=np.number).columns.tolist()
        if not num_cols_v:
            st.info("No numeric columns.")
        else:
            val_col  = st.selectbox("Column", num_cols_v, key="val_num_col")
            val_min  = st.number_input("Minimum allowed value", value=float(df[val_col].min()), key="val_min")
            val_max  = st.number_input("Maximum allowed value", value=float(df[val_col].max()), key="val_max")
            if st.button("Run Validation", key="val_num_run"):
                violations = df[(df[val_col] < val_min) | (df[val_col] > val_max)]
                st.metric("Violations found", len(violations))
                if not violations.empty:
                    st.dataframe(violations, use_container_width=True)
                    viol_csv = violations.to_csv(index=False).encode()
                    st.download_button("⬇️ Download violations", viol_csv, "violations.csv", mime="text/csv")
                else:
                    st.success("All values within range!")

    elif val_type == "Allowed categories list":
        cat_cols_v = df.select_dtypes(include=["object","category"]).columns.tolist()
        if not cat_cols_v:
            st.info("No categorical columns.")
        else:
            val_col   = st.selectbox("Column", cat_cols_v, key="val_cat_col")
            unique_v  = df[val_col].dropna().unique().tolist()
            allowed   = st.multiselect("Allowed values", unique_v, default=unique_v, key="val_allowed")
            if st.button("Run Validation", key="val_cat_run"):
                violations = df[~df[val_col].isin(allowed) & df[val_col].notna()]
                st.metric("Violations found", len(violations))
                if not violations.empty:
                    st.dataframe(violations, use_container_width=True)
                else:
                    st.success("All values are in the allowed list!")

    elif val_type == "Non-null constraint":
        nn_cols = st.multiselect("Columns that must not be null", df.columns.tolist(), key="val_nn_cols")
        if st.button("Run Validation", key="val_nn_run") and nn_cols:
            results = {c: int(df[c].isnull().sum()) for c in nn_cols}
            total_viol = sum(results.values())
            st.metric("Total null violations", total_viol)
            for c, n in results.items():
                if n > 0:
                    st.warning(f"`{c}`: {n} null values")
                else:
                    st.success(f"`{c}`: OK")

st.markdown("---")
st.subheader("✅ Current Dataset")
st.dataframe(st.session_state.df.head(10), use_container_width=True)

if st.session_state.log:
    with st.expander("📝 Transformation Log"):
        for i, s in enumerate(st.session_state.log, 1):
            st.write(f"{i}. {s}")
