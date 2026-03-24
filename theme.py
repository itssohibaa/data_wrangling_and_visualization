import streamlit as st

# ── PALETTE ───────────────────────────────────────────────────────────────────
PLOTLY_COLORS_LIGHT = [
    "#6366f1","#f59e0b","#10b981","#ef4444","#3b82f6",
    "#8b5cf6","#ec4899","#06b6d4","#84cc16","#f97316"
]
PLOTLY_COLORS_DARK = [
    "#818cf8","#fbbf24","#34d399","#f87171","#60a5fa",
    "#a78bfa","#f472b6","#22d3ee","#a3e635","#fb923c"
]

def theme_colors():
    return PLOTLY_COLORS_DARK if st.session_state.get("dark_mode") else PLOTLY_COLORS_LIGHT

def plotly_layout(dark: bool) -> dict:
    if dark:
        return dict(
            font_family="'Space Grotesk', 'Inter', sans-serif",
            font_color="#e2e8f0",
            title_font_color="#f1f5f9",
            title_font_size=15,
            paper_bgcolor="rgba(15,23,42,0)",
            plot_bgcolor="rgba(30,41,59,0.9)",
            margin=dict(t=52, b=42, l=44, r=22),
            legend=dict(bgcolor="rgba(15,23,42,0.85)", bordercolor="#334155", borderwidth=1, font_color="#cbd5e1"),
        )
    return dict(
        font_family="'Space Grotesk', 'Inter', sans-serif",
        font_color="#1e293b",
        title_font_color="#0f172a",
        title_font_size=15,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,1)",
        margin=dict(t=52, b=42, l=44, r=22),
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#e2e8f0", borderwidth=1),
    )

# ── CSS ───────────────────────────────────────────────────────────────────────
LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*, body, p, span, div, label { font-family: 'Space Grotesk', sans-serif !important; }
code, pre, .stCode * { font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 40%, #eef2ff 70%, #e8f4f8 100%);
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(circle, #c7d7f7 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: 0.22;
    pointer-events: none;
    z-index: 0;
}
[data-testid="stMain"] { background: transparent; }
[data-testid="stMetric"] { background: rgba(255,255,255,0.75); border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 14px 18px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06); backdrop-filter: blur(8px); }
[data-testid="stMetricLabel"] { font-size: 11px !important; color: #64748b !important; letter-spacing: 0.04em; text-transform: uppercase; }
[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; color: #0f172a !important; }
[data-testid="stExpander"] { border: 1px solid #e2e8f0 !important; border-radius: 12px !important;
    background: rgba(255,255,255,0.6) !important; backdrop-filter: blur(8px); }
.stButton > button { border-radius: 10px; font-weight: 600; transition: all 0.18s; letter-spacing: 0.01em;
    border: 1px solid #e2e8f0; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
.stDownloadButton > button { background: #0f172a !important; color: white !important;
    border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stSidebarNav"] a { border-radius: 8px; margin: 2px 0; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,0.08) !important; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #94a3b8 !important; font-size: 14px !important; font-weight: 500 !important;
    padding: 6px 12px !important; height: auto !important; min-height: unset !important;
    width: auto !important; border-radius: 8px !important; margin-top: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.07) !important; color: #e2e8f0 !important;
    transform: none !important; box-shadow: none !important;
}
.stDataFrame { border-radius: 10px; overflow: hidden; }
[data-testid="stContainer"] { border-radius: 12px; }
</style>
"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*, body, p, span, div, label { font-family: 'Space Grotesk', sans-serif !important; }
code, pre, .stCode * { font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #020617 0%, #0a0f1e 40%, #0f172a 80%, #0d1526 100%) !important;
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(circle, #1e3a5f 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: 0.30;
    pointer-events: none;
    z-index: 0;
}
[data-testid="stMain"] { background: transparent !important; }
h1, h2, h3, h4, h5, p { color: #e2e8f0 !important; }
[data-testid="stMetric"] { background: rgba(30,41,59,0.85) !important; border: 1px solid #334155 !important;
    border-radius: 12px; padding: 14px 18px !important; backdrop-filter: blur(8px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
[data-testid="stMetricLabel"] { font-size: 11px !important; color: #94a3b8 !important; letter-spacing: 0.04em; text-transform: uppercase; }
[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; color: #f1f5f9 !important; }
[data-testid="stExpander"] { border: 1px solid #334155 !important; border-radius: 12px !important;
    background: rgba(30,41,59,0.7) !important; backdrop-filter: blur(8px); }
.stButton > button { border-radius: 10px; font-weight: 600; transition: all 0.18s;
    letter-spacing: 0.01em; }
.stButton > button:hover { transform: translateY(-2px); }
.stDownloadButton > button { background: #3b82f6 !important; color: white !important;
    border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #020617 0%, #0a0f1e 100%) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; font-family: 'Space Grotesk', sans-serif !important; }
[data-testid="stSidebarNav"] a { border-radius: 8px; margin: 2px 0; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,0.08) !important; }
[data-testid="stAlert"] { background: rgba(30,58,95,0.8) !important; border-radius: 10px; }
.stMarkdown, .stCaption { color: #94a3b8 !important; }
[data-testid="stDataFrame"] { background: rgba(30,41,59,0.7) !important; border-radius: 10px; }
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: #94a3b8 !important; font-size: 14px !important; font-weight: 500 !important;
    padding: 6px 12px !important; height: auto !important; min-height: unset !important;
    width: auto !important; border-radius: 8px !important; margin-top: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.07) !important; color: #e2e8f0 !important;
    transform: none !important; box-shadow: none !important;
}
.stSelectbox label, .stMultiSelect label, .stSlider label,
.stRadio label, .stCheckbox label, .stTextInput label, .stNumberInput label {
    color: #cbd5e1 !important;
}
input, textarea, select { color: #e2e8f0 !important; background: #1e293b !important; }
[data-testid="stContainer"] { border-radius: 12px; }
</style>
"""


def apply_theme():
    """Call at the top of every page to apply dark/light mode + sidebar toggle."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    st.markdown(DARK_CSS if st.session_state.dark_mode else LIGHT_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
        st.markdown("---")
        dm_label = "☀️ Light mode" if st.session_state.dark_mode else "🌙 Dark mode"
        if st.button(dm_label, key=f"dm_{st.session_state.get('_page_key', 'default')}"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
