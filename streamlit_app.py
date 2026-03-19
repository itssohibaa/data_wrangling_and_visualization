import streamlit as st
import time

st.set_page_config(page_title="Data Wrangler & Visualizer", layout="wide")

# ===============================
# 🔹 SESSION INIT
# ===============================
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# ===============================
# 🔹 FULLSCREEN + DATA-THEMED STYLE
# ===============================
st.markdown("""
<style>
.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at 20% 20%, #1f4037, #0f2027, #000000);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    z-index: 999999;
    text-align: center;
    color: white;
    animation: fadeIn 1.2s ease-in-out;
}

/* subtle glow effect */
.title {
    font-size: 60px;
    font-weight: 700;
    text-shadow: 0 0 15px rgba(0,255,200,0.6);
}

.subtitle {
    font-size: 20px;
    opacity: 0.85;
    margin-top: 10px;
}

.footer {
    margin-top: 30px;
    font-size: 16px;
    opacity: 0.7;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
</style>
""", unsafe_allow_html=True)

# ===============================
# 🔹 INTRO SCREEN (5s)
# ===============================
if not st.session_state.intro_done:

    st.markdown("""
    <div class="fullscreen">
        <div class="title">📊 Welcome to Data Wrangler & Visualizer</div>
        <div class="subtitle">Transforming raw data into meaningful insights</div>
        <div class="subtitle">🚀 Initializing analytical environment...</div>
        
        <div class="footer">
            Developed by:<br>
            <b>00017592 & 00018555</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🎉 visual effect (not winter, more neutral celebration)
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
