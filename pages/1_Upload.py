import streamlit as st
import pandas as pd
import numpy as np
import io

# ===============================
# 🔹 CACHING
# ===============================
@st.cache_data
def load_csv(file_bytes, file_name):
    return pd.read_csv(io.BytesIO(file_bytes))

@st.cache_data
def load_excel(file_bytes, file_name):
    return pd.read_excel(io.BytesIO(file_bytes))

@st.cache_data
def load_json(file_bytes, file_name):
    return pd.read_json(io.BytesIO(file_bytes))

@st.cache_data
def load_google_sheets(url):
    return pd.read_csv(url)

# --- SESSION INIT ---
for key, default in [("df", None), ("log", []), ("history", []), ("last_file", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("📂 Upload & Data Profiling")

# ===============================
# 🔹 RESET SESSION (FIX #2)
# Reset clears ALL state + cache so missing values
# and everything refreshes properly on next upload
# ===============================
if st.button("🔄 Reset Session", type="secondary"):
    keys_to_clear = list(st.session_state.keys())
    for key in keys_to_clear:
        del st.session_state[key]
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# ===============================
# 🔹 GOOGLE SHEETS (FIX #1)
# Converts share URL → CSV export URL automatically
# ===============================
st.markdown("### 🌐 Load from Google Sheets (Optional)")
st.caption("ℹ️ Sheet must be shared as 'Anyone with the link can view'")

sheet_url = st.text_input("Paste Google Sheets share link")

if sheet_url and st.button("Load Google Sheets"):
    try:
        if "/edit" in sheet_url:
            if "gid=" in sheet_url:
                gid = sheet_url.split("gid=")[-1].split("&")[0].split("#")[0]
                base = sheet_url.split("/edit")[0]
                csv_url = f"{base}/export?format=csv&gid={gid}"
            else:
                base = sheet_url.split("/edit")[0]
                csv_url = f"{base}/export?format=csv"
        elif "/pub" in sheet_url:
            csv_url = sheet_url.replace("pubhtml", "pub?output=csv")
        else:
            csv_url = sheet_url

        df = load_google_sheets(csv_url)
        st.session_state.df = df
        st.session_state.log.append("Loaded from Google Sheets")
        st.session_state.history.append(df.copy())
        st.session_state.last_file = "google_sheets"
        st.success("✅ Google Sheets loaded successfully!")
    except Exception as e:
        st.error(f"❌ Could not load sheet. Make sure it's publicly accessible. Error: {e}")

st.markdown("---")

# ===============================
# 🔹 FILE UPLOAD
# ===============================
file = st.file_uploader("📁 Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"])

if file is not None:
    try:
        file_bytes = file.read()
        if file.name.endswith(".csv"):
            df = load_csv(file_bytes, file.name)
        elif file.name.endswith(".xlsx"):
            df = load_excel(file_bytes, file.name)
        elif file.name.endswith(".json"):
            df = load_json(file_bytes, file.name)
        else:
            st.error("Unsupported file type")
            st.stop()

        # Always update df (FIX #3: new file = fresh data, no stale cache issue)
        if st.session_state.last_file != file.name or st.session_state.df is None:
            st.session_state.df = df
            st.session_state.history = [df.copy()]
            st.session_state.last_file = file.name
            st.session_state.log.append(f"Dataset uploaded: {file.name}")

        st.success(f"✅ '{file.name}' loaded — {df.shape[0]:,} rows × {df.shape[1]} columns")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

# ===============================
# 🔹 DATASET OVERVIEW
# FIX #3: Missing values always computed from current df
# FIX #4: Missing values count added to overview metrics
# ===============================
if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("📊 Dataset Overview")

    total_missing = int(df.isnull().sum().sum())
    total_cells = df.shape[0] * df.shape[1]
    missing_pct = round(total_missing / total_cells * 100, 1) if total_cells > 0 else 0
    duplicates = int(df.duplicated().sum())

    # 5 metric cards
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("🗂 Rows", f"{df.shape[0]:,}")
    m2.metric("📋 Columns", df.shape[1])
    m3.metric("🔁 Duplicate Rows", f"{duplicates:,}")
    m4.metric("❓ Missing Cells", f"{total_missing:,}")
    m5.metric("📉 Missing %", f"{missing_pct}%")

    st.markdown("---")

    # ---- Missing Values Detail ----
    st.write("### 🔍 Missing Values by Column")
    missing_series = df.isnull().sum()
    missing_df = pd.DataFrame({
        "Missing Count": missing_series,
        "Missing %": (missing_series / len(df) * 100).round(2)
    })
    missing_with_data = missing_df[missing_df["Missing Count"] > 0]

    if missing_with_data.empty:
        st.success("✅ No missing values found in this dataset!")
    else:
        st.dataframe(missing_with_data.style.background_gradient(cmap="Reds", subset=["Missing %"]),
                     use_container_width=True)

    st.markdown("---")

    # ---- Column Info ----
    st.write("### 🏷️ Column Types & Info")
    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.values.astype(str),
        "Non-Null Count": df.notnull().sum().values,
        "Unique Values": [df[c].nunique() for c in df.columns],
        "Sample Value": [str(df[c].dropna().iloc[0]) if not df[c].dropna().empty else "N/A" for c in df.columns]
    }).reset_index(drop=True)
    st.dataframe(dtype_df, use_container_width=True)

    st.markdown("---")

    # ---- Summary Stats ----
    st.write("### 📈 Summary Statistics")
    st.dataframe(df.describe(include="all").T, use_container_width=True)

    st.markdown("---")

    # ---- Preview ----
    st.write("### 👁️ Data Preview (first 10 rows)")
    st.dataframe(df.head(10), use_container_width=True)
