import streamlit as st
import time

st.set_page_config(
    page_title="DataWrangler Pro",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL THEME CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Main background — soft blue-grey gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 40%, #eef2ff 70%, #e8f4f8 100%);
    background-attachment: fixed;
}
[data-testid="stMain"] {
    background: transparent;
}

/* Subtle dot pattern overlay for texture */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(circle, #c7d7f7 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: 0.25;
    pointer-events: none;
    z-index: 0;
}

/* Sidebar branding */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; }
[data-testid="stSidebarNav"] a { border-radius: 8px; margin: 2px 0; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,0.08) !important; }

/* Metric cards */
[data-testid="stMetric"] { background: #f8fafc; border: 0.5px solid #e2e8f0;
    border-radius: 10px; padding: 12px 16px !important; }
[data-testid="stMetricLabel"] { font-size: 12px !important; color: #64748b !important; }
[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 600 !important; }

/* Buttons */
.stButton > button { border-radius: 8px; font-weight: 500; transition: all 0.15s; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

/* Expanders */
[data-testid="stExpander"] { border: 0.5px solid #e2e8f0 !important; border-radius: 10px !important; }

/* Download buttons */
.stDownloadButton > button { background: #0f172a !important; color: white !important;
    border: none !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── INTRO (once per session) ──────────────────────────────────────────────────
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False
if "history" not in st.session_state:
    st.session_state.history = []

if not st.session_state.intro_done:
    st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .intro-wrap  { text-align:center; padding:5rem 2rem 3rem; animation:fadeIn 0.8s ease forwards; }
    .intro-icon  { font-size:64px; margin-bottom:1.25rem; }
    .intro-title { font-size:2.6rem; font-weight:700; color:#0f172a; margin-bottom:0.4rem; }
    .intro-sub   { font-size:1.05rem; color:#64748b; margin-bottom:2.5rem; }
    .intro-steps { display:flex; justify-content:center; gap:1.5rem; flex-wrap:wrap; margin-bottom:2rem; }
    .intro-step  { font-size:0.9rem; color:#475569; background:rgba(255,255,255,0.75);
                   padding:8px 18px; border-radius:20px; border:0.5px solid #cbd5e1; }
    </style>
    <div class="intro-wrap">
      <div class="intro-icon">🔬</div>
      <div class="intro-title">DataWrangler Pro</div>
      <div class="intro-sub">Your AI-powered data preparation workspace</div>
      <div class="intro-steps">
        <span class="intro-step">📂 Upload</span>
        <span class="intro-step">🧹 Clean</span>
        <span class="intro-step">📊 Visualize</span>
        <span class="intro-step">📤 Export</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    bar = st.progress(0, text="Initialising workspace…")
    for pct, label in [(20, "Loading modules…"), (50, "Preparing components…"),
                       (80, "Almost ready…"), (100, "✓ Ready")]:
        time.sleep(0.5)
        bar.progress(pct, text=label)
    time.sleep(0.3)
    bar.empty()
    st.session_state.intro_done = True
    st.rerun()

# ── LANDING ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 1rem 0 0.5rem;">
  <h1 style="font-size:2rem; font-weight:700; margin-bottom:0.25rem;">🔬 DataWrangler Pro</h1>
  <p style="color:#64748b; font-size:1rem; margin:0;">
    Your AI-powered data preparation & visualization workspace
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div style="background:#eff6ff;border-radius:12px;padding:1.25rem;border:0.5px solid #bfdbfe;">
    <div style="font-size:28px">📂</div>
    <div style="font-weight:600;margin-top:8px;color:#1e40af">Upload & Profile</div>
    <div style="font-size:13px;color:#3b82f6;margin-top:4px">CSV · Excel · JSON · Sheets</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div style="background:#f0fdf4;border-radius:12px;padding:1.25rem;border:0.5px solid #bbf7d0;">
    <div style="font-size:28px">🧹</div>
    <div style="font-weight:600;margin-top:8px;color:#166534">Clean & Prepare</div>
    <div style="font-size:13px;color:#16a34a;margin-top:4px">Missing · Duplicates · Scale</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div style="background:#fdf4ff;border-radius:12px;padding:1.25rem;border:0.5px solid #e9d5ff;">
    <div style="font-size:28px">📊</div>
    <div style="font-weight:600;margin-top:8px;color:#6b21a8">Visualize</div>
    <div style="font-size:13px;color:#9333ea;margin-top:4px">8 chart types · 3D · Download</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div style="background:#fff7ed;border-radius:12px;padding:1.25rem;border:0.5px solid #fed7aa;">
    <div style="font-size:28px">📤</div>
    <div style="font-weight:600;margin-top:8px;color:#9a3412">Export</div>
    <div style="font-size:13px;color:#ea580c;margin-top:4px">CSV · Excel · Report · Recipe</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.info("👈 Use the sidebar to navigate. Start with **Upload & Profile** to load your dataset.")
st.markdown("---")
st.caption("DataWrangler Pro · Coursework Project — Data Wrangling & Visualization · IDs: 00017592 & 00018555")
