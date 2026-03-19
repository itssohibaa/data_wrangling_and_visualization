import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# ===============================
# 🔹 SESSION
# ===============================
if "df" not in st.session_state:
    st.session_state.df = None

st.title("📊 Advanced Visualization Studio")

if st.session_state.df is None:
    st.warning("Upload data first")
    st.stop()

df = st.session_state.df.copy()

# ===============================
# 🔹 FILTERS
# ===============================
st.subheader("Filters")

filter_col = st.selectbox("Filter column", df.columns)
unique_vals = df[filter_col].astype(str).dropna().unique()

selected_vals = st.multiselect("Select values", unique_vals)

if selected_vals:
    df = df[df[filter_col].astype(str).isin(selected_vals)]

if df.empty:
    st.warning("No data after filtering")
    st.stop()

# ===============================
# 🔹 COLUMN TYPES
# ===============================
categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# ===============================
# 🔹 MULTI-GRAPH LAYOUT (2x2)
# ===============================
st.subheader("📈 Analytical Dashboard (4 Graphs)")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# -------------------------------
# GRAPH 1: Distribution
# -------------------------------
with col1:
    if numeric_cols:
        col = st.selectbox("Distribution column", numeric_cols, key="g1")
        fig = px.histogram(df, x=col, title=f"Distribution of {col}")
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"This chart shows how values of '{col}' are distributed. Helps detect skewness and outliers.")

# -------------------------------
# GRAPH 2: Category vs Numeric
# -------------------------------
with col2:
    if categorical_cols and numeric_cols:
        cat = st.selectbox("Category", categorical_cols, key="g2_cat")
        num = st.selectbox("Value", numeric_cols, key="g2_num")

        grouped = df.groupby(cat)[num].mean().reset_index()

        fig = px.bar(grouped, x=cat, y=num,
                     title=f"Average {num} by {cat}")
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Compares how '{num}' differs across categories of '{cat}'.")

# -------------------------------
# GRAPH 3: Scatter (Relationship)
# -------------------------------
with col3:
    if len(numeric_cols) >= 2:
        x = st.selectbox("X", numeric_cols, key="g3_x")
        y = st.selectbox("Y", numeric_cols, key="g3_y")

        fig = px.scatter(df, x=x, y=y,
                         title=f"Relationship between {x} and {y}")
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Shows correlation or relationship between '{x}' and '{y}'.")

# -------------------------------
# GRAPH 4: Heatmap
# -------------------------------
with col4:
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()

        fig = px.imshow(
            corr,
            color_continuous_scale="RdBu_r",
            title="Correlation Heatmap"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption("Red = strong positive correlation, Blue = negative correlation.")

# ===============================
# 🔹 CUSTOM BUILDER
# ===============================
st.markdown("---")
st.subheader("🔧 Custom Visualization Builder")

chart = st.selectbox(
    "What do you want to analyze?",
    ["Distribution", "Relationship", "Comparison", "Correlation"]
)

if chart == "Distribution" and numeric_cols:
    col = st.selectbox("Column", numeric_cols)
    fig = px.histogram(df, x=col, title=f"Distribution of {col}")
    st.plotly_chart(fig)

elif chart == "Relationship" and len(numeric_cols) >= 2:
    x = st.selectbox("X", numeric_cols)
    y = st.selectbox("Y", numeric_cols)
    fig = px.scatter(df, x=x, y=y)
    st.plotly_chart(fig)

elif chart == "Comparison" and categorical_cols and numeric_cols:
    cat = st.selectbox("Category", categorical_cols)
    num = st.selectbox("Value", numeric_cols)
    grouped = df.groupby(cat)[num].mean().reset_index()
    fig = px.bar(grouped, x=cat, y=num)
    st.plotly_chart(fig)

elif chart == "Correlation" and len(numeric_cols) >= 2:
    fig = px.imshow(df[numeric_cols].corr(),
                    color_continuous_scale="RdBu_r")
    st.plotly_chart(fig)

# ===============================
# 🔹 AI INTERPRETATION (OPTIONAL)
# ===============================
st.markdown("---")
st.subheader("🤖 AI Insight Assistant")

user_question = st.text_input("Ask about your data")

if user_question:
    try:
        import openai

        openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

        sample = df.head(20).to_string()

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": f"Dataset:\n{sample}\n\nQuestion: {user_question}"}
            ]
        )

        st.write(response["choices"][0]["message"]["content"])

    except Exception:
        st.warning("AI not configured (API key missing)")
