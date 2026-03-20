import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt   # ✅ ADDED (required by CW)

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

filter_col = st.selectbox("Filter column", df.columns, key="filter_col")

unique_vals = df[filter_col].astype(str).dropna().unique()
selected_vals = st.multiselect("Select values", unique_vals, key="filter_vals")

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
# 🔹 DASHBOARD (4 GRAPHS)
# ===============================
st.subheader("📈 Analytical Dashboard")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# -------------------------------
# GRAPH 1: Distribution
# -------------------------------
with col1:
    if numeric_cols:
        col = st.selectbox("Distribution column", numeric_cols, key="g1_col")

        fig1 = px.histogram(df, x=col, title=f"Distribution of {col}")
        st.plotly_chart(fig1, use_container_width=True, key="g1_chart")

# -------------------------------
# GRAPH 2: Category vs Numeric
# -------------------------------
with col2:
    if categorical_cols and numeric_cols:
        cat = st.selectbox("Category", categorical_cols, key="g2_cat")
        num = st.selectbox("Value", numeric_cols, key="g2_num")

        grouped = df.groupby(cat)[num].mean().reset_index()

        fig2 = px.bar(grouped, x=cat, y=num,
                      title=f"Average {num} by {cat}")
        st.plotly_chart(fig2, use_container_width=True, key="g2_chart")

# -------------------------------
# GRAPH 3: Scatter
# -------------------------------
with col3:
    if len(numeric_cols) >= 2:
        x = st.selectbox("X-axis", numeric_cols, key="g3_x")
        y = st.selectbox("Y-axis", numeric_cols, key="g3_y")

        fig3 = px.scatter(df, x=x, y=y,
                          title=f"{y} vs {x}")
        st.plotly_chart(fig3, use_container_width=True, key="g3_chart")

# -------------------------------
# GRAPH 4: Heatmap
# -------------------------------
with col4:
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()

        fig4 = px.imshow(
            corr,
            color_continuous_scale="RdBu_r",
            title="Correlation Heatmap"
        )
        st.plotly_chart(fig4, use_container_width=True, key="g4_chart")

# ===============================
# 🔹 CUSTOM BUILDER
# ===============================
st.markdown("---")
st.subheader("🔧 Custom Visualization")

analysis_type = st.selectbox(
    "What do you want to analyze?",
    ["Distribution", "Relationship", "Comparison", "Correlation"],
    key="analysis_type"
)

if analysis_type == "Distribution" and numeric_cols:
    col = st.selectbox("Column", numeric_cols, key="custom_dist")

    fig = px.histogram(df, x=col, title=f"Distribution of {col}")
    st.plotly_chart(fig, use_container_width=True, key="custom_dist_chart")

elif analysis_type == "Relationship" and len(numeric_cols) >= 2:
    x = st.selectbox("X", numeric_cols, key="custom_x")
    y = st.selectbox("Y", numeric_cols, key="custom_y")

    fig = px.scatter(df, x=x, y=y, title=f"{y} vs {x}")
    st.plotly_chart(fig, use_container_width=True, key="custom_scatter_chart")

elif analysis_type == "Comparison" and categorical_cols and numeric_cols:
    cat = st.selectbox("Category", categorical_cols, key="custom_cat")
    num = st.selectbox("Value", numeric_cols, key="custom_num")

    grouped = df.groupby(cat)[num].mean().reset_index()

    fig = px.bar(grouped, x=cat, y=num, title=f"{num} by {cat}")
    st.plotly_chart(fig, use_container_width=True, key="custom_bar_chart")

elif analysis_type == "Correlation" and len(numeric_cols) >= 2:
    fig = px.imshow(
        df[numeric_cols].corr(),
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix"
    )
    st.plotly_chart(fig, use_container_width=True, key="custom_heatmap_chart")

# ===============================
# 🔹 SMART INTERPRETATION
# ===============================
st.markdown("---")
st.subheader("📊 Smart Interpretation")

try:
    if numeric_cols:

        col = numeric_cols[0]

        mean = df[col].mean()
        median = df[col].median()
        skew = df[col].skew()

        interpretation = f"For '{col}': "

        if skew > 1:
            interpretation += "distribution is strongly right-skewed. "
        elif skew < -1:
            interpretation += "distribution is strongly left-skewed. "
        else:
            interpretation += "distribution is relatively symmetric. "

        if mean > median:
            interpretation += "Mean is greater than median, indicating possible high-value outliers. "
        elif mean < median:
            interpretation += "Median is greater than mean, suggesting left skew. "

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        outliers = df[(df[col] < Q1 - 1.5 * IQR) |
                      (df[col] > Q3 + 1.5 * IQR)]

        interpretation += f"Detected approximately {len(outliers)} potential outliers."

        st.write(interpretation)

    else:
        st.info("No numeric data available for interpretation")

except Exception as e:
    st.warning("Could not generate interpretation")

# ===============================
# 🔹 MATPLOTLIB (ADDED REQUIRED)
# ===============================
st.markdown("---")
st.subheader("📉 Matplotlib Chart (Required)")

if numeric_cols:
    col_m = st.selectbox("Column for matplotlib chart", numeric_cols, key="mpl_col")

    fig, ax = plt.subplots()
    ax.hist(df[col_m])
    ax.set_title(f"Matplotlib Histogram of {col_m}")

    st.pyplot(fig)
