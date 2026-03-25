import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_theme
st.session_state["_page_key"] = "5_AI_Assistant"
apply_theme()

import pandas as pd
import numpy as np
import json


for k, v in [("df", None), ("log", []), ("history", []), ("ai_messages", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

st.title("🤖 AI Assistant")
st.caption("Powered by Claude — get smart suggestions on cleaning and visualization.")

if st.session_state.df is None:
    st.warning("Please upload a dataset first."); st.stop()

df  = st.session_state.df.copy()

# ── DATASET PROFILE FOR AI CONTEXT ───────────────────────────────────────────
def build_profile(df):
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
    missing  = df.isnull().sum()
    missing_info = {c: int(missing[c]) for c in df.columns if missing[c] > 0}

    profile = {
        "shape": {"rows": df.shape[0], "cols": df.shape[1]},
        "numeric_columns": num_cols,
        "categorical_columns": cat_cols,
        "missing_values": missing_info,
        "duplicate_rows": int(df.duplicated().sum()),
        "sample_values": {c: df[c].dropna().head(3).tolist() for c in df.columns[:8]}
    }
    return profile

profile = build_profile(df)
profile_str = json.dumps(profile, indent=2, default=str)

SYSTEM_PROMPT = f"""You are a data science expert assistant built into a data wrangling app called DataWrangler Pro.
The user has uploaded a dataset with the following profile:

{profile_str}

Your job is to:
1. Suggest specific, actionable cleaning steps (missing values, duplicates, outliers, type conversions, standardization).
2. Recommend the best visualization types for their data and explain WHY — mention which columns to use on which axes.
3. Answer general data science questions clearly and concisely.
4. Always be specific — reference actual column names from the profile.
5. Keep responses concise and practical. Use bullet points where helpful.
6. If asked about a chart, suggest which columns to put on X and Y axes.

The app has these pages: Upload, Cleaning, Visualization (histogram, bar, scatter, line, box, heatmap, 3D scatter, pie), Export.
When suggesting cleaning or visualization, guide the user to the right page."""

# ── AI MODES ──────────────────────────────────────────────────────────────────
mode = st.radio("What do you need help with?", [
    "💬 Free chat",
    "🧹 Suggest cleaning steps",
    "📊 Recommend visualizations",
    "🔍 Analyze my dataset"
], horizontal=True, key="ai_mode")

st.markdown("---")

# ── QUICK ACTIONS ─────────────────────────────────────────────────────────────
if mode == "🧹 Suggest cleaning steps":
    if st.button("✨ Generate cleaning recommendations"):
        st.session_state.ai_messages = [{
            "role": "user",
            "content": "Based on my dataset profile, what are the most important cleaning steps I should take? Be specific about which columns need attention and what method to use."
        }]
        st.rerun()

elif mode == "📊 Recommend visualizations":
    if st.button("✨ Recommend charts for my data"):
        st.session_state.ai_messages = [{
            "role": "user",
            "content": "What are the best visualizations for my dataset? For each chart, tell me which columns to use on X and Y axes, and what insight I can expect to find."
        }]
        st.rerun()

elif mode == "🔍 Analyze my dataset":
    if st.button("✨ Get full dataset analysis"):
        st.session_state.ai_messages = [{
            "role": "user",
            "content": "Give me a comprehensive analysis of my dataset: data quality issues, interesting patterns to explore, potential correlations, and what questions this data could answer."
        }]
        st.rerun()

# ── CHAT INTERFACE ────────────────────────────────────────────────────────────
# Display existing messages
for msg in st.session_state.ai_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Call Claude API if last message is from user
if st.session_state.ai_messages and st.session_state.ai_messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                import requests
                api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
                response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 1000,
                        "system": SYSTEM_PROMPT,
                        "messages": st.session_state.ai_messages
                    },
                    timeout=30
                )
                data = response.json()
                if "content" in data:
                    reply = "".join(b["text"] for b in data["content"] if b.get("type") == "text")
                elif "error" in data:
                    reply = f"API error: {data['error'].get('message', 'Unknown error')}"
                else:
                    reply = "Unexpected response from API."

                st.markdown(reply)
                st.session_state.ai_messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                error_msg = f"Could not connect to AI: {e}"
                st.warning(error_msg)
                # Fallback: rule-based suggestions
                st.markdown("**Here are automatic suggestions based on your dataset profile:**")
                missing_info = profile.get("missing_values", {})
                if missing_info:
                    st.markdown("**Missing Values:**")
                    for col, count in list(missing_info.items())[:5]:
                        col_type = "numeric" if col in profile.get("numeric_columns", []) else "categorical"
                        method   = "mean or median" if col_type == "numeric" else "mode or 'Unknown'"
                        st.markdown(f"- `{col}`: {count} missing → fill with **{method}**")
                if profile.get("duplicate_rows", 0) > 0:
                    st.markdown(f"**Duplicates:** {profile['duplicate_rows']} duplicate rows detected → remove on Cleaning page")
                num_cols = profile.get("numeric_columns", [])
                cat_cols = profile.get("categorical_columns", [])
                if len(num_cols) >= 2:
                    st.markdown(f"**Suggested charts:** Scatter plot (`{num_cols[0]}` vs `{num_cols[1]}`), Correlation heatmap (all numeric columns)")
                if cat_cols and num_cols:
                    st.markdown(f"**Suggested charts:** Bar chart (`{cat_cols[0]}` on X, `{num_cols[0]}` on Y)")
                st.session_state.ai_messages.append({"role": "assistant", "content": error_msg})

# Chat input for free-form questions
if mode == "💬 Free chat":
    user_input = st.chat_input("Ask anything about your data...")
    if user_input:
        st.session_state.ai_messages.append({"role": "user", "content": user_input})
        st.rerun()

# Clear chat
if st.session_state.ai_messages:
    if st.button("🗑️ Clear conversation", key="clear_chat"):
        st.session_state.ai_messages = []
        st.rerun()

# ── DATASET PROFILE SUMMARY ───────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Dataset Profile (sent to AI)", expanded=False):
    st.json(profile)

# ── RULE-BASED QUICK SUGGESTIONS (always visible) ─────────────────────────────
st.markdown("---")
st.subheader("⚡ Quick Automatic Suggestions")

tab1, tab2 = st.tabs(["🧹 Cleaning", "📊 Visualization"])

with tab1:
    missing_info = profile.get("missing_values", {})
    if not missing_info:
        st.success("No missing values detected!")
    else:
        for col, count in missing_info.items():
            pct      = round(count / df.shape[0] * 100, 1)
            col_type = "numeric" if col in profile.get("numeric_columns", []) else "categorical"
            if pct > 30:
                st.warning(f"**`{col}`** — {count} missing ({pct}%) — consider **dropping this column** (>30% missing)")
            elif col_type == "numeric":
                st.info(f"**`{col}`** — {count} missing ({pct}%) — fill with **mean** or **median**")
            else:
                st.info(f"**`{col}`** — {count} missing ({pct}%) — fill with **mode** (most frequent value)")

    dupes = profile.get("duplicate_rows", 0)
    if dupes > 0:
        st.warning(f"**{dupes} duplicate rows** detected — remove on the Cleaning page (keep first recommended)")

with tab2:
    num_cols = profile.get("numeric_columns", [])
    cat_cols = profile.get("categorical_columns", [])

    if num_cols:
        st.success(f"**Histogram** — explore distribution of `{num_cols[0]}`")
    if len(num_cols) >= 2:
        st.success(f"**Scatter plot** — look for relationship between `{num_cols[0]}` (X) and `{num_cols[1]}` (Y)")
    if len(num_cols) >= 2:
        st.success(f"**Correlation heatmap** — identify which numeric columns are correlated")
    if cat_cols and num_cols:
        st.success(f"**Bar chart** — compare average `{num_cols[0]}` across `{cat_cols[0]}` categories")
    if len(num_cols) >= 3:
        st.success(f"**3D Scatter** — visualize three variables at once: `{num_cols[0]}`, `{num_cols[1]}`, `{num_cols[2]}`")
    if cat_cols:
        st.success(f"**Pie chart** — see proportions of `{cat_cols[0]}`")
