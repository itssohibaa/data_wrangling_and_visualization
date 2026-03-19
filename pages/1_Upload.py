import streamlit as st
import pandas as pd
import numpy as np   # ← KEPT (even if not used)

# --- SESSION INIT ---
if "df" not in st.session_state:
    st.session_state.df = None
if "log" not in st.session_state:
    st.session_state.log = []

st.title("📂 Upload & Data Profiling")

file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv", "xlsx", "json"])

# --- FILE LOAD ---
if file is not None:
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)

        elif file.name.endswith(".json"):
            df = pd.read_json(file)

        else:
            st.error("Unsupported file type")
            st.stop()

        # SAVE TO SESSION
        st.session_state.df = df
        st.success("✅ File uploaded successfully!")

        # ✅ LOGGING (ADDED ONLY)
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

    # RESET BUTTON
    if st.button("Reset Session"):
        # ✅ LOGGING (ADDED ONLY)
        st.session_state.log.append("Session reset")

        st.session_state.df = None
        st.session_state.log = []
        st.rerun()
