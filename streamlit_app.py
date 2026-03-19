import streamlit as st
import time

st.set_page_config(page_title="Data Wrangler & Visualizer", layout="wide")

# ===============================
# 🔹 SESSION INIT
# ===============================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# ===============================
# 🔹 SIMPLE FULLSCREEN STYLE
# ===============================
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

# ===============================
# 🔹 INTRO SCREEN (5s)
# ===============================
if not st.session_state.intro_done:

    st.markdown("""
    <div class="fullscreen">
        <h1>Welcome to Data Wrangler & Visualizer</h1>
        <h3>Made by</h3>
        <h2>00017592 & 00018555</h2>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()
    time.sleep(5)

    st.session_state.intro_done = True
    st.rerun()

# ===============================
# 🔹 MAIN LANDING PAGE
# ===============================
st.title("AI-Assisted Data Wrangler & Visualizer")

st.markdown("""
### 📊 Project Overview

This application provides an interactive environment for data preparation, transformation, and visualization.  
It is designed to support users in exploring datasets efficiently and generating meaningful insights.

### ⚙️ Key Features

- Upload datasets (CSV, Excel, JSON)
- Perform data cleaning and preprocessing
- Handle missing values, duplicates, and outliers
- Transform and scale data
- Build interactive visualizations
- Export cleaned datasets and transformation reports

### 🎯 Objective

The goal of this application is to simulate a real-world data preparation workflow,  
combining usability, flexibility, and analytical capability in a single interface.

👉 Use the sidebar to navigate through the application.
""")

st.markdown("---")

st.info("Coursework Project – Data Wrangling & Visualization Module")
st.caption("Developed by Student IDs: 00017592 & 00018555")
