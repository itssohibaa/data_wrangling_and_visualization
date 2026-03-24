import streamlit as st
import sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)
from utils import apply_theme

st.session_state["_page_key"] = "4_Export"
apply_theme()

import pandas as pd, json
from datetime import datetime
from io import BytesIO

for k,v in [("df",None),("log",[])]:
    if k not in st.session_state: st.session_state[k] = v

st.title("📤 Export & Report")
if st.session_state.df is None:
    st.warning("No dataset. Please upload data first."); st.stop()

df=st.session_state.df; log=st.session_state.log
total_missing=int(df.isnull().sum().sum()); dupes=int(df.duplicated().sum())

m1,m2,m3,m4=st.columns(4)
m1.metric("Rows",f"{df.shape[0]:,}"); m2.metric("Columns",df.shape[1])
m3.metric("Missing Cells",f"{total_missing:,}"); m4.metric("Duplicate Rows",f"{dupes:,}")
st.dataframe(df.head(), use_container_width=True)
st.markdown("---")

st.subheader("💾 Download Cleaned Dataset")
filename=st.text_input("File name (no extension)","cleaned_data")
c1,c2,c3=st.columns(3)
with c1: st.download_button("⬇️ CSV",df.to_csv(index=False).encode(),f"{filename}.csv","text/csv")
with c2:
    try:
        buf=BytesIO()
        with pd.ExcelWriter(buf,engine="openpyxl") as w: df.to_excel(w,index=False)
        st.download_button("⬇️ Excel (.xlsx)",buf.getvalue(),f"{filename}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except: st.warning("Excel export unavailable.")
with c3: st.download_button("⬇️ JSON",df.to_json(orient="records",indent=2),f"{filename}.json","application/json")

st.markdown("---")
st.subheader("📝 Transformation Log")
if log:
    for i,s in enumerate(log,1): st.write(f"{i}. {s}")
else: st.info("No transformations applied yet.")

st.markdown("---")
st.subheader("📄 Transformation Report")
report={"generated_at":str(datetime.now()),
        "dataset_summary":{"rows":df.shape[0],"columns":df.shape[1],"missing_cells":total_missing,"duplicate_rows":dupes},
        "transformation_steps":[{"step":i+1,"description":s} for i,s in enumerate(log)]}
st.json(report,expanded=False)
st.download_button("⬇️ Download Report (.json)",json.dumps(report,indent=2),f"{filename}_report.json","application/json")

st.markdown("---")
st.subheader("⚙️ Transformation Recipe")
recipe={"recipe_version":"1.0","created_at":str(datetime.now()),
        "steps":[{"order":i+1,"operation":s} for i,s in enumerate(log)]}
st.json(recipe,expanded=False)
st.download_button("⬇️ Download Recipe (.json)",json.dumps(recipe,indent=2),f"{filename}_recipe.json","application/json")
