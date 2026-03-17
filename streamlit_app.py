import streamlit as st
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Data Wrangler", layout="wide")

# --- SESSION INIT ---
if "intro_time" not in st.session_state:
    st.session_state.intro_time = time.time()

# --- INTRO SCREEN (5 seconds) ---
if time.time() - st.session_state.intro_time < 5:
    st.markdown("""
    <div style="
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: black;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        z-index: 9999;
        color: white;
        text-align: center;
    ">
        <h1 style="font-size:70px;">🎉 Made by Violetta & Sohiba 🎉</h1>
        <h2>(Hope it is 90+ 😄)</h2>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()
    st.stop()

# --- MAIN APP ---
st.title("AI-Assisted Data Wrangler & Visualizer")

st.markdown("""
### 📌 About this application

This is an interactive data preparation studio that allows users to:

- Upload datasets (CSV, Excel, JSON)
- Clean and transform data dynamically
- Handle missing values, duplicates, and outliers
- Apply scaling and categorical transformations
- Build dynamic visualizations
- Export cleaned data and transformation reports

👉 Use the sidebar to begin.
""")

st.success("Created by Violetta & Sohiba")
