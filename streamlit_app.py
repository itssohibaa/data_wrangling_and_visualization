import streamlit as st
import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================
st.set_page_config(
    page_title="DataWrangler Pro",
    page_icon="✨",
    layout="wide"
)

# =============================================================================
# SESSION STATE
# =============================================================================
if "df" not in st.session_state:
    st.session_state.df = None

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# =============================================================================
# THEME
# =============================================================================
def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            color: white;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .card {
            background: white;
            border: 1px solid #e2e8f0;
            color: #0f172a;
            border-radius: 20px;
            padding: 20px;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("## ✨ DataWrangler Pro")

    if st.button("🌙 Toggle Theme"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Upload", "Cleaning", "Visualization", "Export", "AI Assistant"],
        format_func=lambda x: {
            "Upload": "📂 Upload",
            "Cleaning": "🧹 Cleaning",
            "Visualization": "📊 Visualization",
            "Export": "📤 Export",
            "AI Assistant": "🤖 AI Assistant"
        }[x]
    )

# =============================================================================
# CARD COMPONENT
# =============================================================================
def card(icon, title, desc):
    st.markdown(f"""
    <div class="card">
        <div style="font-size:50px">{icon}</div>
        <div style="font-weight:600; margin-top:10px">{title}</div>
        <div style="font-size:12px; opacity:0.7">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGES
# =============================================================================

# -------------------- UPLOAD --------------------
if page == "Upload":
    st.title("DataWrangler Pro")
    st.caption("AI-powered data preparation & visualization workspace")

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        card("📂", "Upload", "CSV · Excel · JSON")
    with col2:
        card("🧹", "Clean", "Missing · Duplicates")
    with col3:
        card("📊", "Visualize", "Charts")
    with col4:
        card("📤", "Export", "Reports")
    st.markdown("---")

    # Uploader ONLY here
    file = st.file_uploader("Upload dataset", type=["csv", "xlsx", "json"])
    if file:
        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            elif file.name.endswith(".json"):
                df = pd.read_json(file)
            else:
                st.error("Unsupported file type")
                df = None
    if df is not None:
                st.session_state.df = df
                st.success("File uploaded successfully")
                st.write("Shape:", df.shape)
                st.write("Columns:", list(df.columns))
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"Error loading file: {e}")

# -------------------- CLEANING --------------------
elif page == "Cleaning":
    st.title("🧹 Cleaning Studio")

    if st.session_state.df is None:
        st.warning("Upload data first")
    else:
        df = st.session_state.df
        if st.button("Remove duplicates"):
            df = df.drop_duplicates()
            st.session_state.df = df
            st.success("Duplicates removed")
        st.dataframe(df.head())

# -------------------- VISUALIZATION --------------------
elif page == "Visualization":
    st.title("📊 Visualization")

    if st.session_state.df is None:
        st.warning("Upload data first")
    else:
        df = st.session_state.df
        col = st.selectbox("Select column", df.columns)
        st.bar_chart(df[col])

# -------------------- EXPORT --------------------
elif page == "Export":
    st.title("📤 Export")

    if st.session_state.df is None:
        st.warning("Upload data first")
    else:
        st.download_button(
            "Download CSV",
            st.session_state.df.to_csv(index=False),
            "data.csv"
        )

# -------------------- AI ASSISTANT --------------------
elif page == "AI Assistant":
    st.title("🤖 AI Assistant")

    if st.session_state.df is None:
        st.warning("Upload data first")
    else:
        st.write("Dataset overview:")
        st.write(st.session_state.df.describe())
        question = st.text_input("Ask something about your data")
        if st.button("Analyze"):
            st.info("Correlation matrix:")
            st.write(st.session_state.df.corr(numeric_only=True))
