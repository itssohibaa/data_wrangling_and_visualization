import streamlit as st
import plotly.express as px

if "df" not in st.session_state:
    st.session_state.df = None

st.title("📊 Advanced Visualization Builder")

if st.session_state.df is None:
    st.warning("Upload data first")
    st.stop()

df = st.session_state.df.copy()

# 🔥 FILTERS
st.subheader("Filters")

filter_col = st.selectbox("Filter column", df.columns)
unique_vals = df[filter_col].astype(str).unique()

selected_vals = st.multiselect("Select values", unique_vals)

if selected_vals:
    df = df[df[filter_col].astype(str).isin(selected_vals)]

# 🔥 CHART SETTINGS
chart = st.selectbox("Chart Type",
["Histogram","Scatter","Box","Line","Bar","Heatmap"])

num = df.select_dtypes("number").columns

# 🔥 AGGREGATION
agg = st.selectbox("Aggregation", ["None","Mean","Sum","Count"])

# --- CHARTS ---
if chart == "Bar":
    x = st.selectbox("Category", df.columns)
    y = st.selectbox("Value", num)

    top_n = st.slider("Top N", 5, 50, 10)

    grouped = df.groupby(x)[y]

    if agg == "Mean":
        grouped = grouped.mean()
    elif agg == "Sum":
        grouped = grouped.sum()
    elif agg == "Count":
        grouped = grouped.count()
    else:
        grouped = grouped.mean()

    grouped = grouped.nlargest(top_n).reset_index()

    fig = px.bar(grouped, x=x, y=y, title=f"{y} by {x}")
    st.plotly_chart(fig)

elif chart == "Scatter":
    x = st.selectbox("X", num)
    y = st.selectbox("Y", num)
    color = st.selectbox("Color (optional)", [None] + list(df.columns))

    fig = px.scatter(df, x=x, y=y, color=color,
                     title=f"{y} vs {x}")
    st.plotly_chart(fig)

elif chart == "Histogram":
    col = st.selectbox("Column", num)
    fig = px.histogram(df, x=col, title=f"{col} Distribution")
    st.plotly_chart(fig)

elif chart == "Box":
    col = st.selectbox("Column", num)
    fig = px.box(df, y=col, title=f"{col} Boxplot")
    st.plotly_chart(fig)

elif chart == "Line":
    x = st.selectbox("X", df.columns)
    y = st.selectbox("Y", num)
    fig = px.line(df, x=x, y=y, title=f"{y} over {x}")
    st.plotly_chart(fig)

elif chart == "Heatmap":

    # Select ONLY numeric columns
    num_df = df.select_dtypes(include="number")

    if num_df.shape[1] < 2:
        st.warning("Not enough numeric columns for correlation heatmap")
        st.stop()

    corr = num_df.corr()

    fig = px.imshow(corr, title="Correlation Matrix")
    st.plotly_chart(fig)
