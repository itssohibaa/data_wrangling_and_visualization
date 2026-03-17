import streamlit as st
import json
from datetime import datetime

if "df" not in st.session_state:
    st.session_state.df = None
if "log" not in st.session_state:
    st.session_state.log = []

st.title("📤 Export & Transformation Report")

if st.session_state.df is None:
    st.warning("No dataset")
    st.stop()

df = st.session_state.df

st.subheader("Preview")
st.dataframe(df.head())

# CSV EXPORT
csv = df.to_csv(index=False).encode()
st.download_button("Download Cleaned Dataset", csv, "cleaned_data.csv")

# 🔥 TRANSFORMATION REPORT
report = {
    "timestamp": str(datetime.now()),
    "steps": st.session_state.log
}

st.subheader("Transformation Log")
st.write(st.session_state.log)

st.download_button(
    "Download Transformation Report (JSON)",
    json.dumps(report, indent=2),
    "report.json"
)
