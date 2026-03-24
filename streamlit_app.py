import streamlit as st
import time

st.set_page_config(
    page_title="DataWrangler Pro",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "history" not in st.session_state:
    st.session_state.history = []

from utils import apply_theme
st.session_state["_page_key"] = "home"
apply_theme()

if not st.session_state.intro_done:
    tc = "#e2e8f0" if st.session_state.dark_mode else "#0f172a"
    sc = "#94a3b8" if st.session_state.dark_mode else "#64748b"
    sb = "rgba(30,41,59,0.8)" if st.session_state.dark_mode else "rgba(255,255,255,0.75)"
    st.markdown(f"""
    <style>
    @keyframes fadeIn {{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:translateY(0)}}}}
    .iw{{text-align:center;padding:5rem 2rem 3rem;animation:fadeIn 0.8s ease forwards}}
    .ii{{font-size:72px;margin-bottom:1.25rem;filter:drop-shadow(0 4px 16px rgba(99,102,241,0.4))}}
    .it{{font-size:2.8rem;font-weight:700;color:{tc};margin-bottom:0.4rem;letter-spacing:-0.02em}}
    .is{{font-size:1rem;color:{sc};margin-bottom:2rem}}
    .ist{{display:flex;justify-content:center;gap:1rem;flex-wrap:wrap}}
    .isp{{font-size:.85rem;color:{sc};background:{sb};padding:7px 18px;border-radius:24px;border:1px solid #334155;font-weight:500}}
    </style>
    <div class="iw"><div class="ii">🔬</div>
    <div class="it">DataWrangler Pro</div>
    <div class="is">AI-powered data preparation &amp; visualization workspace</div>
    <div class="ist">
      <span class="isp">📂 Upload</span><span class="isp">🧹 Clean</span>
      <span class="isp">📊 Visualize</span><span class="isp">📤 Export</span>
      <span class="isp">🤖 AI Assistant</span>
    </div></div>""", unsafe_allow_html=True)
    bar = st.progress(0, text="Initialising workspace…")
    for pct, label in [(20,"Loading modules…"),(50,"Preparing components…"),(80,"Almost ready…"),(100,"✓ Ready")]:
        time.sleep(0.4)
        bar.progress(pct, text=label)
    time.sleep(0.2)
    bar.empty()
    st.session_state.intro_done = True
    st.rerun()

tc = "#e2e8f0" if st.session_state.dark_mode else "#0f172a"
sc = "#94a3b8" if st.session_state.dark_mode else "#64748b"

st.markdown(f"""<div style="padding:1.2rem 0 0.6rem">
  <h1 style="font-size:2rem;font-weight:700;margin-bottom:0.2rem;color:{tc};letter-spacing:-0.02em">
    🔬 DataWrangler Pro</h1>
  <p style="color:{sc};font-size:1rem;margin:0">
    AI-powered data preparation &amp; visualization — Upload → Clean → Visualize → Export</p>
</div>""", unsafe_allow_html=True)

st.markdown("---")

if st.session_state.dark_mode:
    cards = [
        ("#1e3a5f33","#93c5fd","#60a5fa","📂","Upload & Profile","CSV · Excel · JSON · Sheets"),
        ("#14532d33","#86efac","#4ade80","🧹","Clean & Prepare","Missing · Dupes · Outliers · Scale"),
        ("#3b076433","#d8b4fe","#c084fc","📊","Visualize","10 charts · 3D · AI picks · Download"),
        ("#43140733","#fdba74","#fb923c","📤","Export & Report","CSV · Excel · JSON · Recipe"),
        ("#0c4a6e33","#7dd3fc","#38bdf8","🤖","AI Assistant","Claude-powered · Clean & Chart advice"),
    ]
else:
    cards = [
        ("#eff6ff","#1e40af","#3b82f6","📂","Upload & Profile","CSV · Excel · JSON · Sheets"),
        ("#f0fdf4","#166534","#16a34a","🧹","Clean & Prepare","Missing · Dupes · Outliers · Scale"),
        ("#fdf4ff","#6b21a8","#9333ea","📊","Visualize","10 charts · 3D · AI picks · Download"),
        ("#fff7ed","#9a3412","#ea580c","📤","Export & Report","CSV · Excel · JSON · Recipe"),
        ("#f0f9ff","#075985","#0284c7","🤖","AI Assistant","Claude-powered · Clean & Chart advice"),
    ]

cols = st.columns(5)
for col, (bg,tc2,sc2,icon,title,sub) in zip(cols, cards):
    with col:
        st.markdown(f"""<div style="background:{bg};border-radius:14px;padding:1.3rem;
            border:1px solid {sc2}55;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
          <div style="font-size:28px">{icon}</div>
          <div style="font-weight:700;margin-top:8px;color:{tc2};font-size:.9rem">{title}</div>
          <div style="font-size:12px;color:{sc2};margin-top:4px;line-height:1.5">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Use the sidebar to navigate. Start with **Upload & Profile** to load your dataset.")
st.markdown("---")
st.caption("DataWrangler Pro · Data Wrangling & Visualization Coursework · IDs: 00017592 & 00018555")
