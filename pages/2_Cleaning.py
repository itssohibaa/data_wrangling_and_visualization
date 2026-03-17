import streamlit as st
import pandas as pd

# --- SESSION FIX ---
if "df" not in st.session_state:
    st.session_state.df = None
if "log" not in st.session_state:
    st.session_state.log = []

st.title("📂 Upload & Data Profiling")

file = st.file_uploader("Upload CSV / Excel / JSON", type=["csv","xlsx","json"])

if file:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_json(file)

    st.session_state.df = df

if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("Dataset Overview")

    col1,col2,col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Duplicates", df.duplicated().sum())

    st.write("### Column Types")
    st.dataframe(df.dtypes)

    st.write("### Missing Values (%)")
    missing = (df.isnull().sum()/len(df))*100
    st.dataframe(missing)

    st.write("### Preview")
    st.dataframe(df.head())

    if st.button("Reset Session"):
        st.session_state.df = None
        st.session_state.log = []
        st.rerun()
