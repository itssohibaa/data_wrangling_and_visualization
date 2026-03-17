import streamlit as st
import time

st.set_page_config(page_title="AI Data Wrangler", layout="wide")

# --- SESSION INIT ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# --- FULLSCREEN STYLE ---
st.markdown("""
<style>
.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: black;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    z-index: 999999;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- INTRO SCREEN ---
if not st.session_state.intro_done:

    st.markdown("""
    <div class="fullscreen">
        <h1 style="font-size:70px;">🎉 Made by Violetta & Sohiba 🎉</h1>
        <h2>(Hope it is 90+ 😄)</h2>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()
    time.sleep(5)   # ✅ ONLY CHANGE (was 1 second)

    st.session_state.intro_done = True
    st.rerun()

# --- MAIN LANDING ---
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
