import streamlit as st
import sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)
from utils import apply_theme

st.session_state["_page_key"] = "5_AI_Assistant"
apply_theme()

import pandas as pd, numpy as np, json, requests

for k,v in [("df",None),("log",[]),("history",[]),("ai_messages",[])]:
    if k not in st.session_state: st.session_state[k] = v

st.title("🤖 AI Assistant")
st.caption("Powered by Claude — intelligent suggestions on cleaning and visualization.")

ai_enabled = st.toggle("Enable AI Assistant (Claude API)", value=True, key="ai_enabled")

if st.session_state.df is None:
    st.warning("Please upload a dataset first."); st.stop()

df = st.session_state.df.copy()

def build_profile(df):
    num_cols=df.select_dtypes(include=np.number).columns.tolist()
    cat_cols=df.select_dtypes(include=["object","category"]).columns.tolist()
    missing=df.isnull().sum()
    return {"shape":{"rows":df.shape[0],"cols":df.shape[1]},
            "numeric_columns":num_cols,"categorical_columns":cat_cols,
            "missing_values":{c:int(missing[c]) for c in df.columns if missing[c]>0},
            "duplicate_rows":int(df.duplicated().sum()),
            "sample_values":{c:df[c].dropna().head(3).tolist() for c in df.columns[:10]}}

profile=build_profile(df)
profile_str=json.dumps(profile,indent=2,default=str)

SYSTEM_PROMPT=f"""You are a data science expert in DataWrangler Pro.
Dataset profile: {profile_str}
Tasks: suggest cleaning steps, recommend visualizations (specify chart type + X/Y/color columns + expected insight), answer data science questions.
Be specific — use actual column names. Keep responses concise with bullet points.
App pages: Upload, Cleaning (missing/dupes/types/categories/outliers/scaling/column ops/validation), Visualization (histogram/bar/grouped bar/scatter/line/box/violin/heatmap/3D scatter/pie/area/bubble), Export.
Outputs may be imperfect — encourage users to verify."""

mode=st.radio("Mode",["💬 Free chat","🧹 Suggest cleaning","📊 Recommend charts","🔍 Full analysis"],horizontal=True,key="ai_mode")
st.markdown("---")

if mode=="🧹 Suggest cleaning":
    if st.button("✨ Generate cleaning recommendations"):
        st.session_state.ai_messages=[{"role":"user","content":"What are the most important cleaning steps? Be specific about columns and methods."}]; st.rerun()
elif mode=="📊 Recommend charts":
    if st.button("✨ Recommend charts"):
        st.session_state.ai_messages=[{"role":"user","content":"Recommend visualizations: for each give chart type, X-axis, Y-axis, color-by (if any), and expected insight."}]; st.rerun()
elif mode=="🔍 Full analysis":
    if st.button("✨ Full dataset analysis"):
        st.session_state.ai_messages=[{"role":"user","content":"Give a comprehensive analysis: data quality issues, interesting patterns, potential correlations, questions this data could answer."}]; st.rerun()

for msg in st.session_state.ai_messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if ai_enabled and st.session_state.ai_messages and st.session_state.ai_messages[-1]["role"]=="user":
    with st.chat_message("assistant"):
        with st.spinner("Claude is thinking…"):
            try:
                resp=requests.post("https://api.anthropic.com/v1/messages",
                    headers={"Content-Type":"application/json","anthropic-version":"2023-06-01"},
                    json={"model":"claude-sonnet-4-20250514","max_tokens":1000,
                          "system":SYSTEM_PROMPT,"messages":st.session_state.ai_messages},timeout=30)
                data=resp.json()
                if "content" in data: reply="".join(b["text"] for b in data["content"] if b.get("type")=="text")
                elif "error" in data: reply=f"⚠️ API error: {data['error'].get('message','Unknown')}"
                else: reply="Unexpected API response."
                st.markdown(reply)
                st.session_state.ai_messages.append({"role":"assistant","content":reply})
            except Exception as e:
                st.warning(f"Could not connect to Claude API: {e}")
                st.session_state.ai_messages.append({"role":"assistant","content":f"[API unavailable: {e}]"})

if mode=="💬 Free chat":
    user_input=st.chat_input("Ask anything about your data…")
    if user_input:
        st.session_state.ai_messages.append({"role":"user","content":user_input}); st.rerun()

if st.session_state.ai_messages:
    if st.button("🗑️ Clear conversation",key="clear_chat"):
        st.session_state.ai_messages=[]; st.rerun()

st.markdown("---")
with st.expander("📋 Dataset Profile (sent to AI)",expanded=False): st.json(profile)

st.markdown("---")
st.subheader("⚡ Quick Automatic Suggestions")
st.caption("Rule-based — always available, no API key required.")
tab1,tab2=st.tabs(["🧹 Cleaning","📊 Visualization"])

with tab1:
    mv=profile.get("missing_values",{})
    if not mv: st.success("✅ No missing values!")
    else:
        for col,count in mv.items():
            pct=round(count/df.shape[0]*100,1)
            col_type="numeric" if col in profile.get("numeric_columns",[]) else "categorical"
            if pct>30: st.warning(f"**`{col}`** — {pct}% missing → consider **dropping column**")
            elif col_type=="numeric": st.info(f"**`{col}`** — {pct}% missing → fill with **mean or median**")
            else: st.info(f"**`{col}`** — {pct}% missing → fill with **mode**")
    if profile.get("duplicate_rows",0)>0:
        st.warning(f"**{profile['duplicate_rows']} duplicate rows** → remove on Cleaning page")

with tab2:
    nc=profile.get("numeric_columns",[]); cc=profile.get("categorical_columns",[])
    if nc: st.success(f"📊 **Histogram** — distribution of `{nc[0]}`")
    if len(nc)>=2: st.success(f"🔵 **Scatter** — `{nc[0]}` (X) vs `{nc[1]}` (Y)")
    if len(nc)>=2: st.success(f"🌡️ **Heatmap** — correlations between all numeric columns")
    if cc and nc: st.success(f"📊 **Bar chart** — mean `{nc[0]}` by `{cc[0]}`")
    if len(nc)>=3: st.success(f"🌐 **3D Scatter** — `{nc[0]}` × `{nc[1]}` × `{nc[2]}`")
    if cc: st.success(f"🥧 **Pie chart** — proportions of `{cc[0]}`")
    if nc: st.success(f"📦 **Box plot** — outliers in `{nc[0]}`")
