import streamlit as st
import pandas as pd

# --- SESSION STATE INIT ---
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
st.subheader("Missing Values")

col = st.selectbox("Select column", df.columns)
col_type = df[col].dtype

st.info(f"Column type: {col_type}")

# SMART METHOD OPTIONS
if col_type == "object":
    method = st.selectbox("Method", ["Drop", "Mode", "Constant"])
else:
    method = st.selectbox("Method", ["Drop", "Mean", "Median", "Mode"])

if method == "Constant":
    const_value = st.text_input("Enter constant value")

if st.button("Apply Missing Handling"):

    # VALIDATION
    if method in ["Mean", "Median"] and col_type == "object":
        st.error("Cannot apply numeric method to text column")
        st.stop()

    try:
        if method == "Drop":
            df = df.dropna(subset=[col])

        elif method == "Mean":
            df[col].fillna(df[col].mean(), inplace=True)

        elif method == "Median":
            df[col].fillna(df[col].median(), inplace=True)

        elif method == "Mode":
            df[col].fillna(df[col].mode()[0], inplace=True)

        elif method == "Constant":
            df[col].fillna(const_value, inplace=True)

        st.session_state.df = df
        st.session_state.log.append(f"Missing values handled in '{col}' using {method}")

        st.success("Missing values handled successfully")

    except Exception as e:
        st.error(f"Error: {e}")

# ===============================
# 🔹 REMOVE DUPLICATES
# ===============================
st.subheader("Remove Duplicates")

if st.button("Remove duplicates"):
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)

    st.session_state.df = df
    st.session_state.log.append(f"Removed duplicates: {before - after} rows")

    st.success(f"Removed {before - after} duplicate rows")

# ===============================
# 🔹 TYPE CONVERSION
# ===============================
st.subheader("Type Conversion")

col_convert = st.selectbox("Column to convert", df.columns, key="convert")

new_type = st.selectbox("Convert to", ["int", "float", "str"])

if st.button("Apply conversion"):
    try:
        if new_type == "int":
            df[col_convert] = pd.to_numeric(df[col_convert], errors="coerce").astype("Int64")

        elif new_type == "float":
            df[col_convert] = pd.to_numeric(df[col_convert], errors="coerce")

        elif new_type == "str":
            df[col_convert] = df[col_convert].astype(str)

        st.session_state.df = df
        st.session_state.log.append(f"Converted '{col_convert}' to {new_type}")

        st.success("Conversion successful")

    except Exception as e:
        st.error(f"Error: {e}")

# ===============================
# 🔹 OUTLIER REMOVAL (IQR)
# ===============================
st.subheader("Outlier Removal (IQR Method)")

num_cols = df.select_dtypes(include="number").columns

if len(num_cols) > 0:
    col_outlier = st.selectbox("Numeric column", num_cols)

    if st.button("Remove outliers"):
        try:
            Q1 = df[col_outlier].quantile(0.25)
            Q3 = df[col_outlier].quantile(0.75)
            IQR = Q3 - Q1

            before = len(df)

            df = df[(df[col_outlier] >= Q1 - 1.5 * IQR) &
                    (df[col_outlier] <= Q3 + 1.5 * IQR)]

            after = len(df)

            st.session_state.df = df
            st.session_state.log.append(f"Removed outliers from '{col_outlier}'")

            st.success(f"Removed {before - after} outliers")

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("No numeric columns available for outlier detection")

# ===============================
# 🔹 FINAL PREVIEW
# ===============================
st.subheader("Updated Dataset")
st.dataframe(st.session_state.df.head())
