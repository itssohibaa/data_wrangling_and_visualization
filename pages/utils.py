"""
utils.py — shared theme helpers for DataWrangler Pro.
Import with:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils import apply_theme, theme_colors, plotly_layout
"""
import streamlit as st

PLOTLY_COLORS_LIGHT = ["#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6",
                        "#8b5cf6","#ec4899","#06b6d4","#84cc16","#f97316"]
PLOTLY_COLORS_DARK  = ["#818cf8","#fbbf24","#34d399","#f87171","#60a5fa",
                        "#a78bfa","#f472b6","#22d3ee","#a3e635","#fb923c"]

def theme_colors():
    return PLOTLY_COLORS_DARK if st.session_state.get("dark_mode") else PLOTLY_COLORS_LIGHT

def plotly_layout(dark: bool) -> dict:
    if dark:
        return dict(font_family="'Space Grotesk',sans-serif", font_color="#e2e8f0",
                    title_font_color="#f1f5f9", title_font_size=15,
                    paper_bgcolor="rgba(15,23,42,0)", plot_bgcolor="rgba(30,41,59,0.9)",
                    margin=dict(t=52,b=42,l=44,r=22),
                    legend=dict(bgcolor="rgba(15,23,42,0.85)",bordercolor="#334155",borderwidth=1,font_color="#cbd5e1"))
    return dict(font_family="'Space Grotesk',sans-serif", font_color="#1e293b",
                title_font_color="#0f172a", title_font_size=15,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,250,252,1)",
                margin=dict(t=52,b=42,l=44,r=22),
                legend=dict(bgcolor="rgba(255,255,255,0.85)",bordercolor="#e2e8f0",borderwidth=1))

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*, body { font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg,#e8f0fe 0%,#f0f4ff 40%,#eef2ff 70%,#e8f4f8 100%);
    background-attachment: fixed; }
[data-testid="stMain"] { background: transparent; }
[data-testid="stMetric"] { background:rgba(255,255,255,0.75); border:1px solid #e2e8f0;
    border-radius:12px; padding:14px 18px !important; box-shadow:0 1px 4px rgba(0,0,0,0.06); }
[data-testid="stMetricLabel"] { font-size:11px !important; color:#64748b !important; text-transform:uppercase; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stMetricValue"] { font-size:24px !important; font-weight:700 !important; color:#0f172a !important; }
[data-testid="stExpander"] { border:1px solid #e2e8f0 !important; border-radius:12px !important; background:rgba(255,255,255,0.6) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0f172a 0%,#1e293b 100%); }
[data-testid="stSidebar"] * { color:#e2e8f0 !important; font-family:'Space Grotesk',sans-serif !important; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background:transparent !important; border:none !important; box-shadow:none !important;
    color:#94a3b8 !important; font-size:14px !important; padding:6px 12px !important;
    height:auto !important; min-height:unset !important; border-radius:8px !important; }
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background:rgba(255,255,255,0.07) !important; color:#e2e8f0 !important;
    transform:none !important; box-shadow:none !important; }
.stButton > button { border-radius:10px; font-weight:600; transition:all 0.18s; }
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 6px 16px rgba(0,0,0,0.12); }
.stDownloadButton > button { background:#0f172a !important; color:white !important;
    border:none !important; border-radius:10px !important; font-weight:600 !important; }
</style>"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*, body { font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg,#020617 0%,#0a0f1e 40%,#0f172a 80%,#0d1526 100%) !important;
    background-attachment: fixed; }
[data-testid="stMain"] { background: transparent !important; }
h1,h2,h3,h4,h5,p { color:#e2e8f0 !important; }
[data-testid="stMetric"] { background:rgba(30,41,59,0.85) !important; border:1px solid #334155 !important;
    border-radius:12px; padding:14px 18px !important; }
[data-testid="stMetricLabel"] { font-size:11px !important; color:#94a3b8 !important; text-transform:uppercase; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stMetricValue"] { font-size:24px !important; font-weight:700 !important; color:#f1f5f9 !important; }
[data-testid="stExpander"] { border:1px solid #334155 !important; border-radius:12px !important; background:rgba(30,41,59,0.7) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#020617 0%,#0a0f1e 100%) !important; }
[data-testid="stSidebar"] * { color:#e2e8f0 !important; font-family:'Space Grotesk',sans-serif !important; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background:transparent !important; border:none !important; box-shadow:none !important;
    color:#94a3b8 !important; font-size:14px !important; padding:6px 12px !important;
    height:auto !important; min-height:unset !important; border-radius:8px !important; }
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background:rgba(255,255,255,0.07) !important; color:#e2e8f0 !important;
    transform:none !important; box-shadow:none !important; }
[data-testid="stAlert"] { background:rgba(30,58,95,0.8) !important; border-radius:10px; }
.stMarkdown,.stCaption { color:#94a3b8 !important; }
.stDownloadButton > button { background:#3b82f6 !important; color:white !important;
    border:none !important; border-radius:10px !important; font-weight:600 !important; }
.stButton > button { border-radius:10px; font-weight:600; transition:all 0.18s; }
</style>"""

def apply_theme():
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    st.markdown(DARK_CSS if st.session_state.dark_mode else LIGHT_CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("---")
        dm_label = "☀️ Light mode" if st.session_state.dark_mode else "🌙 Dark mode"
        if st.button(dm_label, key=f"dm_{st.session_state.get('_page_key','x')}"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
