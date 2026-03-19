import streamlit as st
import pandas as pd
import numpy as np

# --- SESSION INIT ---
if "df" not in st.session_state:
    st.session_state.df = None
if "log" not in st.session_state:
    st.session_state.log = []

st.title("🧹 Data Cleaning")

if st.session_state.df is None:
    st.warning("Please upload data first")
    st.stop()

df = st.session_state.df.copy()

# ===============================
# 🔹 PREVIEW
# ===============================
st.subheader("Dataset Preview")
st.dataframe(df.head())

# ===============================
# 🔹 MISSING VALUES
# ===============================
st.subheader("Missing Values Handling")

col = st.selectbox("Select column", df.columns)
col_type = df[col].dtype

st.info(f"Column type: {col_type}")

if col_type == "object":
    method = st.selectbox("Method", ["Drop rows", "Mode", "Constant"])
else:
    method = st.selectbox("Method", ["Drop rows", "Mean", "Median", "Mode"])

if method == "Constant":
    const_value = st.text_input("Enter constant value")

if st.button("Apply Missing Handling"):

    before = df[col].isnull().sum()

    try:
        if method == "Drop rows":
            df = df.dropna(subset=[col])

        elif method == "Mean":
            df[col] = df[col].fillna(df[col].mean())

        elif method == "Median":
            df[col] = df[col].fillna(df[col].median())

        elif method == "Mode":
            df[col] = df[col].fillna(df[col].mode()[0])

        elif method == "Constant":
            df[col] = df[col].fillna(const_value)

        after = df[col].isnull().sum()

        st.session_state.df = df
        st.session_state.log.append(
            f"Handled missing in '{col}' using {method} (filled {before - after} values)"
        )

        st.success(f"{before - after} missing values handled")

    except Exception as e:
        st.error(f"Error: {e}")

# ===============================
# 🔹 DUPLICATES
# ===============================
st.subheader("Duplicate Handling")

dup_count = df.duplicated().sum()
st.write(f"Duplicate rows: {dup_count}")

if st.button("Remove duplicates"):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)

    st.session_state.df = df
    st.session_state.log.append(f"Removed {removed} duplicate rows")

    st.success(f"Removed {removed} duplicate rows")

# ===============================
# 🔹 TYPE CONVERSION (SAFE)
# ===============================
st.subheader("Type Conversion (Safe)")

col_convert = st.selectbox("Column to convert", df.columns, key="convert")

st.write("Unique sample values:")
st.write(df[col_convert].dropna().unique()[:10])

new_type = st.selectbox("Convert to", ["int", "float", "string"])

if st.button("Apply conversion"):
    try:
        if new_type == "int":
            df[col_convert] = pd.to_numeric(df[col_convert], errors="coerce").astype("Int64")

        elif new_type == "float":
            df[col_convert] = pd.to_numeric(df[col_convert], errors="coerce")

        elif new_type == "string":
            df[col_convert] = df[col_convert].astype(str)

        st.session_state.df = df
        st.session_state.log.append(f"Converted '{col_convert}' to {new_type}")

        st.success("Conversion successful (invalid values converted to NaN)")

    except Exception as e:
        st.error(f"Error: {e}")

# ===============================
# 🔹 DATETIME PROCESSING
# ===============================
st.subheader("Datetime Processing")

col_date = st.selectbox("Select column for datetime conversion", df.columns, key="date")

if st.button("Convert to datetime"):
    try:
        df[col_date] = pd.to_datetime(df[col_date], errors="coerce")

        st.session_state.df = df
        st.session_state.log.append(f"Converted '{col_date}' to datetime")

        st.success("Converted to datetime")

    except Exception as e:
        st.error(f"Error: {e}")

if df[col_date].dtype == "datetime64[ns]":
    if st.button("Extract Year/Month/Day"):
        df[f"{col_date}_year"] = df[col_date].dt.year
        df[f"{col_date}_month"] = df[col_date].dt.month
        df[f"{col_date}_day"] = df[col_date].dt.day

        st.session_state.df = df
        st.session_state.log.append(f"Extracted date parts from '{col_date}'")

        st.success("Date components created")

# ===============================
# 🔹 OUTLIER REMOVAL
# ===============================
st.subheader("Outlier Removal (IQR)")

num_cols = df.select_dtypes(include=np.number).columns

if len(num_cols) > 0:
    col_outlier = st.selectbox("Numeric column", num_cols)

    if st.button("Remove outliers"):
        Q1 = df[col_outlier].quantile(0.25)
        Q3 = df[col_outlier].quantile(0.75)
        IQR = Q3 - Q1

        before = len(df)

        df = df[(df[col_outlier] >= Q1 - 1.5 * IQR) &
                (df[col_outlier] <= Q3 + 1.5 * IQR)]

        removed = before - len(df)

        st.session_state.df = df
        st.session_state.log.append(f"Removed {removed} outliers from '{col_outlier}'")

        st.success(f"Removed {removed} outliers")

else:
    st.info("No numeric columns available")

# ===============================
# 🔹 FINAL PREVIEW
# ===============================
st.subheader("Updated Dataset")
st.dataframe(st.session_state.df.head())
