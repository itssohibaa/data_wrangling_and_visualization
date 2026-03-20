import streamlit as st
import pandas as pd
import numpy as np

# ===============================
# 🔹 CACHING (ADDED)
# ===============================
@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

@st.cache_data
def load_json(file):
    return pd.read_json(file)

# --- SESSION INIT ---
if "df" not in st.session_state:
    st.session_state.df = None
if "log" not in st.session_state:
    st.session_state.log = []
if "history" not in st.session_state:
    st.session_state.history = []

st.title("📂 Upload & Data Profiling")

# ===============================
# 🔹 GOOGLE SHEETS (ADDED)
# ===============================
st.markdown("### 🌐 Load from Google Sheets (Optional)")
sheet_url = st.text_input("Paste Google Sheets link")

if sheet_url:
    try:
        sheet_url = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
        df = pd.read_csv(sheet_url)

        st.session_state.df = df
        st.session_state.log.append("Loaded from Google Sheets")
        st.session_state.history.append(df.copy())

        st.success("✅ Google Sheets loaded successfully!")

    except:
        st.error("Invalid Google Sheets link")

file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"])

# --- FILE LOAD ---
if file is not None:
    try:
        if file.name.endswith(".csv"):
            df = load_csv(file)

        elif file.name.endswith(".xlsx"):
            df = load_excel(file)

        elif file.name.endswith(".json"):
            df = load_json(file)

        else:
            st.error("Unsupported file type")
            st.stop()

        st.session_state.df = df
        st.session_state.history.append(df.copy())

        st.success("✅ File uploaded successfully!")
        st.session_state.log.append("Dataset uploaded")

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        st.stop()

# --- DISPLAY DATA ---
if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Duplicates", df.duplicated().sum())

    st.write("### Column Types")
    st.dataframe(df.dtypes)

    st.write("### Missing Values (%)")
    missing = (df.isnull().sum() / len(df)) * 100
    st.dataframe(missing)

    st.write("### Preview")
    st.dataframe(df.head())

    if st.button("Reset Session"):
        st.session_state.log.append("Session reset")
        st.session_state.df = None
        st.session_state.log = []
        st.session_state.history = []
        st.rerun()
