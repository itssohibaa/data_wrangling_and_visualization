import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_theme

st.session_state["_page_key"] = "2_Cleaning"
apply_theme()

import pandas as pd
import numpy as np

for k, v in [("df", None), ("log", []), ("history", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

st.title("🧹 Cleaning & Preparation Studio")

if st.session_state.df is None:
    st.warning("Please upload a dataset first.")
    st.stop()

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
        st.success("✅ No missing values!")
    else:
        st.dataframe(mv_f, use_container_width=True)
        col = st.selectbox("Column to fix", mv_f.index.tolist(), key="mv_col")
        ctype = df[col].dtype
        st.info(f"`{col}` — type: `{ctype}` — {int(df[col].isnull().sum())} missing")

        opts = ["Drop rows", "Mode (most frequent)", "Constant value", "Forward Fill", "Backward Fill"]
        if ctype != object:
            opts = ["Drop rows", "Mean", "Median", "Mode (most frequent)",
                    "Constant value", "Forward Fill", "Backward Fill"]
        method = st.selectbox("Fill method", opts, key="mv_method")
        const_val = st.text_input("Constant value", key="mv_const") if method == "Constant value" else ""

        # Before / after preview
        before_count = int(df[col].isnull().sum())
        st.caption(f"**Before:** {before_count} missing in `{col}`")

        if st.button("Apply Missing Value Fix", key="mv_apply"):
            st.session_state.history.append(df.copy())
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
                after = int(df[col].isnull().sum()) if col in df.columns else 0
                st.session_state.df = df
                st.session_state.log.append(f"Missing values in '{col}' handled with {method}")
                st.success(f"✅ Fixed {before_count - after} missing values (was {before_count}, now {after})")
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

    keep_opt = st.radio("Keep", ["first", "last"], horizontal=True, key="dup_keep")

    if subset or dup_mode == "Full row":
        mask = df.duplicated(subset=subset if subset else None, keep=False)
        n_dups = int(mask.sum())
        if n_dups > 0:
            st.warning(f"{n_dups} duplicate rows found.")
            with st.expander("Show duplicate groups"):
                st.dataframe(df[mask].head(50), use_container_width=True)
        else:
            st.success("No duplicates found with current selection.")

    if st.button("Remove Duplicates", key="dup_apply"):
        st.session_state.history.append(df.copy())
        before = len(df)
        df = df.drop_duplicates(subset=subset if subset else None, keep=keep_opt)
        removed = before - len(df)
        st.session_state.df = df
        st.session_state.log.append(f"Removed {removed} duplicate rows (keep={keep_opt}, subset={subset})")
        st.success(f"✅ Removed {removed} duplicates. {len(df):,} rows remaining.")
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. DATA TYPES & PARSING
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔄 3. Data Types & Parsing", expanded=False):
    col3 = st.selectbox("Column", df.columns.tolist(), key="dt_col")
    cur_type = str(df[col3].dtype)
    st.info(f"Current type: `{cur_type}`")
    target_type = st.selectbox("Convert to", ["numeric", "string / categorical", "datetime"], key="dt_type")
    dt_fmt = st.text_input("Datetime format (leave blank for auto)", key="dt_fmt",
                           placeholder="%Y-%m-%d") if target_type == "datetime" else ""
    clean_num = st.checkbox("Clean dirty numerics (remove $, commas, spaces)", key="dt_clean") \
                if target_type == "numeric" else False

    if st.button("Convert Type", key="dt_apply"):
        st.session_state.history.append(df.copy())
        try:
            if target_type == "numeric":
                if clean_num:
                    df[col3] = df[col3].astype(str).str.replace(r"[\$,\s]", "", regex=True)
                df[col3] = pd.to_numeric(df[col3], errors="coerce")
            elif target_type == "string / categorical":
                df[col3] = df[col3].astype(str)
            elif target_type == "datetime":
                if dt_fmt:
                    df[col3] = pd.to_datetime(df[col3], format=dt_fmt, errors="coerce")
                else:
                    df[col3] = pd.to_datetime(df[col3], infer_datetime_format=True, errors="coerce")
            st.session_state.df = df
            st.session_state.log.append(f"Converted '{col3}' to {target_type}")
            st.success(f"✅ `{col3}` converted to {target_type}")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. CATEGORICAL DATA TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🏷️ 4. Categorical Data Tools", expanded=False):
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    if not cat_cols:
        st.info("No categorical columns detected.")
    else:
        cat_col = st.selectbox("Column", cat_cols, key="cat_col")
        st.caption(f"Unique values: {df[cat_col].nunique()} | Sample: {df[cat_col].dropna().unique()[:6].tolist()}")

        cat_op = st.radio("Operation", [
            "Trim whitespace & fix case",
            "Replace / map values",
            "Group rare categories → Other",
            "One-hot encode"
        ], key="cat_op")

        if cat_op == "Trim whitespace & fix case":
            case_opt = st.selectbox("Case", ["lower","upper","title","no change"], key="cat_case")
            if st.button("Apply", key="cat_clean_apply"):
                st.session_state.history.append(df.copy())
                df[cat_col] = df[cat_col].astype(str).str.strip()
                if case_opt == "lower":  df[cat_col] = df[cat_col].str.lower()
                elif case_opt == "upper": df[cat_col] = df[cat_col].str.upper()
                elif case_opt == "title": df[cat_col] = df[cat_col].str.title()
                st.session_state.df = df
                st.session_state.log.append(f"Standardised '{cat_col}' (trim + {case_opt} case)")
                st.success(f"✅ Standardised `{cat_col}`")
                st.rerun()

        elif cat_op == "Replace / map values":
            st.caption("Enter old→new pairs (one per line, format: old_value=new_value)")
            mapping_txt = st.text_area("Mapping (old=new)", key="cat_map",
                                       placeholder="Male=M\nFemale=F\nUnknown=Other")
            unmatched = st.checkbox("Set unmatched to 'Other'", key="cat_unmatched")
            if st.button("Apply Mapping", key="cat_map_apply") and mapping_txt:
                st.session_state.history.append(df.copy())
                try:
                    mapping = {}
                    for line in mapping_txt.strip().split("\n"):
                        if "=" in line:
                            k, v = line.split("=", 1)
                            mapping[k.strip()] = v.strip()
                    df[cat_col] = df[cat_col].map(lambda x: mapping.get(str(x), "Other" if unmatched else x))
                    st.session_state.df = df
                    st.session_state.log.append(f"Mapped values in '{cat_col}': {mapping}")
                    st.success(f"✅ Applied {len(mapping)} mappings to `{cat_col}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        elif cat_op == "Group rare categories → Other":
            threshold = st.slider("Min frequency threshold (%)", 1, 20, 5, key="cat_rare_thr")
            freq = df[cat_col].value_counts(normalize=True) * 100
            rare = freq[freq < threshold].index.tolist()
            st.info(f"Categories below {threshold}%: {rare[:10]}")
            if st.button("Group Rare → Other", key="cat_rare_apply"):
                st.session_state.history.append(df.copy())
                df[cat_col] = df[cat_col].apply(lambda x: x if x not in rare else "Other")
                st.session_state.df = df
                st.session_state.log.append(f"Grouped {len(rare)} rare categories in '{cat_col}' → Other")
                st.success(f"✅ Grouped {len(rare)} rare categories into 'Other'")
                st.rerun()

        elif cat_op == "One-hot encode":
            st.info(f"Will create {df[cat_col].nunique()} new binary columns and drop `{cat_col}`")
            if st.button("Apply One-Hot Encoding", key="cat_ohe_apply"):
                st.session_state.history.append(df.copy())
                dummies = pd.get_dummies(df[cat_col], prefix=cat_col, drop_first=False)
                df = pd.concat([df.drop(columns=[cat_col]), dummies], axis=1)
                st.session_state.df = df
                st.session_state.log.append(f"One-hot encoded '{cat_col}' → {dummies.shape[1]} columns")
                st.success(f"✅ One-hot encoded `{cat_col}` into {dummies.shape[1]} columns")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 5. NUMERIC CLEANING (Outliers)
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📐 5. Numeric Cleaning & Outliers", expanded=False):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not num_cols:
        st.info("No numeric columns.")
    else:
        nc = st.selectbox("Column", num_cols, key="nc_col")
        method_out = st.radio("Detection method", ["IQR (1.5×)", "Z-score (threshold)"],
                              horizontal=True, key="nc_method")
        s = df[nc].dropna()
        if method_out == "IQR (1.5×)":
            Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
            IQR = Q3 - Q1
            mask_out = (s < Q1 - 1.5*IQR) | (s > Q3 + 1.5*IQR)
        else:
            z_thr = st.slider("Z-score threshold", 2.0, 4.0, 3.0, 0.1, key="nc_zthr")
            z = np.abs((s - s.mean()) / s.std())
            mask_out = z > z_thr

        n_out = int(mask_out.sum())
        st.metric("Outliers detected", n_out)
        if n_out > 0:
            st.dataframe(df.loc[mask_out.index[mask_out], [nc]].describe().T, use_container_width=True)

        action_out = st.radio("Action", ["Do nothing", "Remove outlier rows", "Cap / Winsorize"],
                              horizontal=True, key="nc_action")

        if action_out == "Cap / Winsorize":
            lo_q = st.slider("Lower quantile cap", 0.0, 0.1, 0.01, 0.005, key="nc_loq")
            hi_q = st.slider("Upper quantile cap", 0.9, 1.0, 0.99, 0.005, key="nc_hiq")

        if action_out != "Do nothing" and st.button("Apply Outlier Action", key="nc_apply"):
            st.session_state.history.append(df.copy())
            before = len(df)
            if action_out == "Remove outlier rows":
                full_mask = (df[nc] < (Q1 - 1.5*IQR)) | (df[nc] > (Q3 + 1.5*IQR)) if method_out == "IQR (1.5×)" else (np.abs((df[nc] - df[nc].mean()) / df[nc].std()) > z_thr)
                df = df[~full_mask]
                removed = before - len(df)
                st.session_state.log.append(f"Removed {removed} outlier rows from '{nc}'")
                st.success(f"✅ Removed {removed} rows with outliers in `{nc}`")
            elif action_out == "Cap / Winsorize":
                lo_val = df[nc].quantile(lo_q)
                hi_val = df[nc].quantile(hi_q)
                df[nc] = df[nc].clip(lower=lo_val, upper=hi_val)
                st.session_state.log.append(f"Winsorized '{nc}' at [{lo_q:.3f}, {hi_q:.3f}] quantiles")
                st.success(f"✅ Capped `{nc}` at [{lo_val:.3g}, {hi_val:.3g}]")
            st.session_state.df = df
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 6. NORMALIZATION / SCALING
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("📏 6. Normalization & Scaling", expanded=False):
    num_cols_sc = df.select_dtypes(include=np.number).columns.tolist()
    if not num_cols_sc:
        st.info("No numeric columns.")
    else:
        sc_cols = st.multiselect("Columns to scale", num_cols_sc,
                                  default=num_cols_sc[:min(3,len(num_cols_sc))], key="sc_cols")
        sc_method = st.radio("Method", ["Min-Max (0–1)", "Z-score (mean=0, std=1)"],
                             horizontal=True, key="sc_method")

        if sc_cols:
            before_stats = df[sc_cols].describe().T[["mean","std","min","max"]]
            st.write("**Before:**")
            st.dataframe(before_stats, use_container_width=True)

        if sc_cols and st.button("Apply Scaling", key="sc_apply"):
            st.session_state.history.append(df.copy())
            for c in sc_cols:
                if sc_method == "Min-Max (0–1)":
                    mn, mx = df[c].min(), df[c].max()
                    if mx != mn: df[c] = (df[c] - mn) / (mx - mn)
                else:
                    mu, sig = df[c].mean(), df[c].std()
                    if sig != 0: df[c] = (df[c] - mu) / sig
            after_stats = df[sc_cols].describe().T[["mean","std","min","max"]]
            st.write("**After:**")
            st.dataframe(after_stats, use_container_width=True)
            st.session_state.df = df
            st.session_state.log.append(f"Scaled columns {sc_cols} using {sc_method}")
            st.success(f"✅ Scaled {len(sc_cols)} columns using {sc_method}")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 7. COLUMN OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("⚙️ 7. Column Operations", expanded=False):
    col_op = st.radio("Operation", ["Rename column", "Drop columns",
                                     "Create new column (formula)", "Bin numeric column"],
                       key="colop")

    if col_op == "Rename column":
        old_name = st.selectbox("Column to rename", df.columns.tolist(), key="ren_col")
        new_name = st.text_input("New name", key="ren_new")
        if st.button("Rename", key="ren_apply") and new_name:
            st.session_state.history.append(df.copy())
            df = df.rename(columns={old_name: new_name})
            st.session_state.df = df
            st.session_state.log.append(f"Renamed '{old_name}' → '{new_name}'")
            st.success(f"✅ Renamed `{old_name}` → `{new_name}`")
            st.rerun()

    elif col_op == "Drop columns":
        drop_cols = st.multiselect("Columns to drop", df.columns.tolist(), key="drop_cols")
        if drop_cols and st.button("Drop Selected Columns", key="drop_apply"):
            st.session_state.history.append(df.copy())
            df = df.drop(columns=drop_cols)
            st.session_state.df = df
            st.session_state.log.append(f"Dropped columns: {drop_cols}")
            st.success(f"✅ Dropped {len(drop_cols)} column(s)")
            st.rerun()

    elif col_op == "Create new column (formula)":
        new_col_name = st.text_input("New column name", key="newcol_name")
        st.caption("Available column names: " + ", ".join([f"`{c}`" for c in df.columns[:10]]))
        formula = st.text_input("Formula (use df['colname'] syntax)",
                                placeholder="df['price'] / df['quantity']", key="newcol_formula")
        if st.button("Create Column", key="newcol_apply") and new_col_name and formula:
            st.session_state.history.append(df.copy())
            try:
                import math
                df[new_col_name] = eval(formula, {"df": df, "np": np, "pd": pd, "math": math})
                st.session_state.df = df
                st.session_state.log.append(f"Created column '{new_col_name}' = {formula}")
                st.success(f"✅ Created column `{new_col_name}`")
                st.rerun()
            except Exception as e:
                st.error(f"Formula error: {e}")

    elif col_op == "Bin numeric column":
        num_cols_bin = df.select_dtypes(include=np.number).columns.tolist()
        if num_cols_bin:
            bin_col  = st.selectbox("Column to bin", num_cols_bin, key="bin_col")
            bin_n    = st.slider("Number of bins", 2, 20, 5, key="bin_n")
            bin_meth = st.radio("Binning method", ["Equal-width", "Quantile (equal-frequency)"],
                                horizontal=True, key="bin_meth")
            bin_name = st.text_input("New column name", value=f"{bin_col}_bin", key="bin_name")
            if st.button("Create Bins", key="bin_apply"):
                st.session_state.history.append(df.copy())
                if bin_meth == "Equal-width":
                    df[bin_name] = pd.cut(df[bin_col], bins=bin_n, labels=False).astype("Int64").astype(str)
                else:
                    df[bin_name] = pd.qcut(df[bin_col], q=bin_n, labels=False, duplicates="drop").astype("Int64").astype(str)
                st.session_state.df = df
                st.session_state.log.append(f"Binned '{bin_col}' into {bin_n} {bin_meth} bins → '{bin_name}'")
                st.success(f"✅ Created `{bin_name}` with {bin_n} bins")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# 8. DATA VALIDATION RULES
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("✅ 8. Data Validation Rules", expanded=False):
    val_col = st.selectbox("Column to validate", df.columns.tolist(), key="val_col")
    val_type = st.radio("Rule type", [
        "Numeric range check",
        "Allowed categories list",
        "Non-null constraint"
    ], key="val_type", horizontal=True)

    violations = pd.DataFrame()

    if val_type == "Numeric range check":
        num_cols_v = df.select_dtypes(include=np.number).columns.tolist()
        if val_col not in num_cols_v:
            st.warning("Select a numeric column.")
        else:
            min_val = st.number_input("Min allowed", value=float(df[val_col].min()), key="val_min")
            max_val = st.number_input("Max allowed", value=float(df[val_col].max()), key="val_max")
            mask = (df[val_col] < min_val) | (df[val_col] > max_val)
            violations = df[mask]

    elif val_type == "Allowed categories list":
        allowed_txt = st.text_input("Allowed values (comma-separated)", key="val_cats",
                                     placeholder="Yes,No,Maybe")
        if allowed_txt:
            allowed = [v.strip() for v in allowed_txt.split(",")]
            violations = df[~df[val_col].astype(str).isin(allowed)]

    elif val_type == "Non-null constraint":
        violations = df[df[val_col].isnull()]

    if not violations.empty:
        st.error(f"⚠️ {len(violations)} violation(s) found:")
        st.dataframe(violations.head(50), use_container_width=True)
        vio_csv = violations.to_csv(index=False).encode()
        st.download_button("⬇️ Export violations CSV", vio_csv,
                           "violations.csv", mime="text/csv", key="val_export")
    elif val_type in ["Numeric range check","Allowed categories list","Non-null constraint"]:
        st.success("✅ No violations found!")

# ── TRANSFORMATION LOG ────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Transformation Log", expanded=False):
    if st.session_state.log:
        for i, step in enumerate(st.session_state.log, 1):
            st.write(f"{i}. {step}")
    else:
        st.info("No transformations applied yet.")
