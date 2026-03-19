import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

# ===============================
# 🔹 SESSION
# ===============================
if "df" not in st.session_state:
    st.session_state.df = None
if "log" not in st.session_state:
    st.session_state.log = []

st.title("📤 Export & Transformation Report")

if st.session_state.df is None:
    st.warning("No dataset available")
    st.stop()

df = st.session_state.df

# ===============================
# 🔹 PREVIEW
# ===============================
st.subheader("Dataset Preview")
st.dataframe(df.head())

# ===============================
# 🔹 SUMMARY
# ===============================
st.subheader("📊 Dataset Summary")

summary = {
    "Rows": df.shape[0],
    "Columns": df.shape[1],
    "Missing Values": int(df.isnull().sum().sum()),
    "Duplicate Rows": int(df.duplicated().sum())
}

st.write(summary)

# ===============================
# 🔹 FILE NAME
# ===============================
filename = st.text_input("File name", "cleaned_data")

# ===============================
# 🔹 DOWNLOAD BUTTONS (NO SELECTBOX → more stable)
# ===============================
st.subheader("Download Dataset")

col1, col2, col3 = st.columns(3)

# --- CSV ---
with col1:
    csv = df.to_csv(index=False).encode()
    st.download_button(
        "⬇ CSV",
        csv,
        f"{filename}.csv",
        mime="text/csv"
    )

# --- EXCEL (FIXED) ---
with col2:
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        st.download_button(
            "⬇ Excel",
            buffer.getvalue(),
            f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.warning("Excel export not available (missing dependency)")

# --- JSON ---
with col3:
    json_data = df.to_json(orient="records", indent=2)

    st.download_button(
        "⬇ JSON",
        json_data,
        f"{filename}.json",
        mime="application/json"
    )

# ===============================
# 🔹 REPORT
# ===============================
st.markdown("---")
st.subheader("📝 Transformation Report")

report = {
    "timestamp": str(datetime.now()),
    "dataset_summary": summary,
    "steps": st.session_state.log
}

st.write(st.session_state.log if st.session_state.log else "No transformations yet")

st.download_button(
    "⬇ Download Report",
    json.dumps(report, indent=2),
    f"{filename}_report.json",
    mime="application/json"
)
