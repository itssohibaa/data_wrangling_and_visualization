import streamlit as st
import pandas as pd
import json
from datetime import datetime

df = st.session_state.df

st.title("📤 Export")

filename = st.text_input("Filename","data")

# CSV
st.download_button("Download CSV",
                   df.to_csv(index=False),
                   f"{filename}.csv")

# REPORT
report = {
    "timestamp": str(datetime.now()),
    "steps": st.session_state.log
}

st.download_button("Download Report",
                   json.dumps(report, indent=2),
                   f"{filename}_report.json")

# RECIPE (IMPORTANT FOR MARKS)
recipe = "\n".join(st.session_state.log)

st.download_button("Download Recipe (Pipeline)",
                   recipe,
                   f"{filename}_recipe.txt")
