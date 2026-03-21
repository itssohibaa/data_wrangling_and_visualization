import streamlit as st
import pandas as pd
import json
from datetime import datetime
from io import BytesIO

# ===============================
# 🔹 SESSION
# ===============================
for key, default in [("df", None), ("log", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("📤 Export & Report")

if st.session_state.df is None:
    st.warning("⚠️ No dataset available. Please upload data first.")
    st.stop()

df = st.session_state.df

# ===============================
# 🔹 SUMMARY
# ===============================
st.subheader("📊 Final Dataset Summary")

total_missing = int(df.isnull().sum().sum())
duplicates = int(df.duplicated().sum())

m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows", f"{df.shape[0]:,}")
m2.metric("Columns", df.shape[1])
m3.metric("Missing Cells", f"{total_missing:,}")
m4.metric("Duplicate Rows", f"{duplicates:,}")

st.dataframe(df.head(), use_container_width=True)

st.markdown("---")

# ===============================
# 🔹 DOWNLOAD DATASET
# ===============================
st.subheader("💾 Download Cleaned Dataset")

filename = st.text_input("File name (without extension)", "cleaned_data")

col1, col2, col3 = st.columns(3)

with col1:
    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Download CSV", csv, f"{filename}.csv", mime="text/csv")

with col2:
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            "⬇️ Download Excel", buffer.getvalue(),
            f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception:
        st.warning("Excel export not available.")

with col3:
    json_data = df.to_json(orient="records", indent=2)
    st.download_button("⬇️ Download JSON", json_data, f"{filename}.json", mime="application/json")

st.markdown("---")

# ===============================
# 🔹 TRANSFORMATION LOG
# ===============================
st.subheader("📝 Transformation Log")

if st.session_state.log:
    for i, step in enumerate(st.session_state.log, 1):
        st.write(f"{i}. {step}")
else:
    st.info("No transformations applied yet.")

st.markdown("---")

# ===============================
# 🔹 TRANSFORMATION REPORT (FIX #10)
# Human-readable log: what happened, when, with what params
# Good for: sharing with teammates, graders, documentation
# ===============================
st.subheader("📄 Transformation Report")
st.caption("A **human-readable** record of all steps applied — who, what, when. Good for documentation and sharing.")

report = {
    "generated_at": str(datetime.now()),
    "dataset_summary": {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_cells": total_missing,
        "duplicate_rows": duplicates
    },
    "transformation_steps": [
        {"step": i + 1, "description": step}
        for i, step in enumerate(st.session_state.log)
    ]
}

st.json(report, expanded=False)

st.download_button(
    "⬇️ Download Transformation Report (.json)",
    json.dumps(report, indent=2),
    f"{filename}_transformation_report.json",
    mime="application/json"
)

st.markdown("---")

# ===============================
# 🔹 TRANSFORMATION RECIPE (FIX #10)
# Machine-readable reproducible pipeline
# Good for: replaying the exact same steps on a new dataset
# ===============================
st.subheader("⚙️ Transformation Recipe")
st.caption("A **machine-readable** JSON recipe that captures the exact pipeline — so you can replay it on a different dataset or automate it.")

recipe = {
    "recipe_version": "1.0",
    "created_at": str(datetime.now()),
    "steps": [
        {"order": i + 1, "operation": step}
        for i, step in enumerate(st.session_state.log)
    ]
}

st.json(recipe, expanded=False)

st.download_button(
    "⬇️ Download Transformation Recipe (.json)",
    json.dumps(recipe, indent=2),
    f"{filename}_recipe.json",
    mime="application/json"
)

# ===============================
# 🔹 REPORT VS RECIPE EXPLAINER (FIX #10)
# ===============================
with st.expander("❓ What's the difference between Report and Recipe?"):
    st.markdown("""
    | | **Transformation Report** | **Transformation Recipe** |
    |---|---|---|
    | **Purpose** | Documentation for humans | Reproducibility for machines |
    | **Audience** | Teammates, graders, stakeholders | Developers, pipelines, automation |
    | **Contains** | Steps + timestamp + dataset summary | Steps in structured format for replaying |
    | **Use case** | "What did we do to this data?" | "Replay the exact same steps on a new dataset" |
    | **Format** | Human-readable JSON with context | Structured JSON pipeline |
    """)
