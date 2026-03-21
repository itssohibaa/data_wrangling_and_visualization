import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# 🔹 SESSION
# ===============================
if "df" not in st.session_state:
    st.session_state.df = None

st.title("📊 Visualization Studio")

if st.session_state.df is None:
    st.warning("⚠️ Upload data first on the Upload page.")
    st.stop()

df = st.session_state.df.copy()

# ===============================
# 🔹 COLUMN TYPE HELPERS
# ===============================
categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
all_cols = df.columns.tolist()

# ===============================
# 🔹 GLOBAL FILTERS
# ===============================
with st.expander("🔎 Filters (apply before all charts)", expanded=False):
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        if categorical_cols:
            filter_col = st.selectbox("Filter by category column", ["(none)"] + categorical_cols, key="f_cat_col")
            if filter_col != "(none)":
                vals = df[filter_col].astype(str).dropna().unique().tolist()
                selected = st.multiselect("Select values to keep", vals, default=vals, key="f_cat_vals")
                if selected:
                    df = df[df[filter_col].astype(str).isin(selected)]
    with fcol2:
        if numeric_cols:
            range_col = st.selectbox("Filter by numeric range", ["(none)"] + numeric_cols, key="f_num_col")
            if range_col != "(none)":
                mn = float(df[range_col].min())
                mx = float(df[range_col].max())
                rng = st.slider("Range", mn, mx, (mn, mx), key="f_num_range")
                df = df[df[range_col].between(rng[0], rng[1])]

if df.empty:
    st.warning("No data remaining after filters.")
    st.stop()

st.caption(f"📦 {len(df):,} rows after filtering")

st.markdown("---")

# ====================================================
# 🔹 ANALYTICAL DASHBOARD (FIX #6 — aligned, bordered)
# ====================================================
st.subheader("📈 Analytical Dashboard")

# CSS for bordered chart cards — fixes alignment & boundaries
st.markdown("""
<style>
[data-testid="stVerticalBlock"] > [data-testid="element-container"] > div.chart-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 12px;
    background: #fafafa;
}
/* Force all plotly charts in dashboard to same height */
.dashboard-chart .js-plotly-plot {
    height: 320px !important;
}
</style>
""", unsafe_allow_html=True)

def chart_container(title):
    """Returns a styled container for a dashboard chart."""
    return st.container(border=True)

# Row 1: Distribution + Category vs Numeric
row1_col1, row1_col2 = st.columns(2, gap="medium")

with row1_col1:
    with st.container(border=True):
        st.markdown("**📊 Distribution**")
        if numeric_cols:
            g1_col = st.selectbox("Column", numeric_cols, key="g1_col")
            fig1 = px.histogram(df, x=g1_col, title=f"Distribution of {g1_col}",
                                height=300, color_discrete_sequence=["#636EFA"])
            fig1.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig1, use_container_width=True, key="g1_chart")
        else:
            st.info("No numeric columns available.")

with row1_col2:
    with st.container(border=True):
        st.markdown("**📊 Category vs Numeric (Bar)**")
        if categorical_cols and numeric_cols:
            g2_cat = st.selectbox("Category column", categorical_cols, key="g2_cat")
            g2_num = st.selectbox("Numeric column", numeric_cols, key="g2_num")
            # FIX #7: renamed "limit" → "Top N categories"
            g2_topn = st.slider("Top N categories to show", 3, 30, 10, key="g2_topn")
            grouped = df.groupby(g2_cat)[g2_num].mean().reset_index()
            grouped = grouped.nlargest(g2_topn, g2_num)
            fig2 = px.bar(grouped, x=g2_cat, y=g2_num,
                          title=f"Avg {g2_num} by {g2_cat} (Top {g2_topn})",
                          height=300, color_discrete_sequence=["#EF553B"])
            fig2.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig2, use_container_width=True, key="g2_chart")
        else:
            st.info("Need both categorical and numeric columns.")

# Row 2: Scatter + Heatmap
row2_col1, row2_col2 = st.columns(2, gap="medium")

with row2_col1:
    with st.container(border=True):
        st.markdown("**📊 Scatter Plot**")
        if len(numeric_cols) >= 2:
            # FIX #9: explicit X/Y axis selectors in dashboard
            g3_x = st.selectbox("X-axis", numeric_cols, key="g3_x")
            g3_y = st.selectbox("Y-axis", numeric_cols,
                                 index=min(1, len(numeric_cols)-1), key="g3_y")
            g3_color = st.selectbox("Color by (optional)", ["(none)"] + categorical_cols, key="g3_color")
            color_arg = g3_color if g3_color != "(none)" else None
            fig3 = px.scatter(df, x=g3_x, y=g3_y, color=color_arg,
                              title=f"{g3_y} vs {g3_x}", height=300)
            fig3.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig3, use_container_width=True, key="g3_chart")
        else:
            st.info("Need at least 2 numeric columns for scatter.")

with row2_col2:
    with st.container(border=True):
        st.markdown("**📊 Correlation Heatmap**")
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig4 = px.imshow(corr, color_continuous_scale="RdBu_r",
                             title="Correlation Heatmap", height=300,
                             text_auto=".2f")
            fig4.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig4, use_container_width=True, key="g4_chart")
        else:
            st.info("Need at least 2 numeric columns for heatmap.")

# Row 3 (extra charts to form a real dashboard — FIX #6)
row3_col1, row3_col2 = st.columns(2, gap="medium")

with row3_col1:
    with st.container(border=True):
        st.markdown("**📊 Box Plot**")
        if numeric_cols:
            g5_num = st.selectbox("Numeric column", numeric_cols, key="g5_num")
            g5_cat = st.selectbox("Group by (optional)", ["(none)"] + categorical_cols, key="g5_cat")
            box_x = g5_cat if g5_cat != "(none)" else None
            fig5 = px.box(df, x=box_x, y=g5_num,
                          title=f"Box Plot: {g5_num}" + (f" by {g5_cat}" if box_x else ""),
                          height=300, color_discrete_sequence=["#00CC96"])
            fig5.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig5, use_container_width=True, key="g5_chart")
        else:
            st.info("No numeric columns available.")

with row3_col2:
    with st.container(border=True):
        st.markdown("**📊 Line Chart**")
        if numeric_cols:
            g6_x = st.selectbox("X-axis (time/index)", all_cols, key="g6_x")
            g6_y = st.selectbox("Y-axis (value)", numeric_cols, key="g6_y")
            g6_color = st.selectbox("Color by (optional)", ["(none)"] + categorical_cols, key="g6_color")
            color_arg6 = g6_color if g6_color != "(none)" else None
            plot_df = df[[g6_x, g6_y] + ([g6_color] if color_arg6 else [])].dropna().sort_values(g6_x)
            fig6 = px.line(plot_df, x=g6_x, y=g6_y, color=color_arg6,
                           title=f"{g6_y} over {g6_x}", height=300)
            fig6.update_layout(margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig6, use_container_width=True, key="g6_chart")
        else:
            st.info("No numeric columns available.")

st.markdown("---")

# ===============================
# 🔹 CUSTOM VISUALIZATION BUILDER
# FIX #7: renamed "Limit" → "Top N categories"
# FIX #8: Relationship now has variable selectors
# FIX #9: all chart types have explicit X/Y selectors
# ===============================
st.subheader("🔧 Custom Visualization Builder")

analysis_type = st.selectbox(
    "What do you want to analyze?",
    ["Distribution", "Relationship (Scatter)", "Comparison (Bar)", "Correlation (Heatmap)",
     "Box Plot", "Line Chart"],
    key="custom_analysis_type"
)

# ---- Distribution ----
if analysis_type == "Distribution":
    if not numeric_cols:
        st.warning("No numeric columns available.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            col = st.selectbox("Column", numeric_cols, key="custom_dist_col")
            nbins = st.slider("Number of bins", 5, 100, 20, key="custom_dist_bins")
        with c2:
            color_by = st.selectbox("Color by (optional)", ["(none)"] + categorical_cols, key="custom_dist_color")
        color_arg = color_by if color_by != "(none)" else None
        fig = px.histogram(df, x=col, nbins=nbins, color=color_arg,
                           title=f"Distribution of {col}")
        st.plotly_chart(fig, use_container_width=True, key="custom_dist_chart")

# ---- Relationship / Scatter — FIX #8 ----
elif analysis_type == "Relationship (Scatter)":
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for a relationship chart.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            # FIX #8: variable selectors now always shown
            x_col = st.selectbox("X-axis variable", numeric_cols, key="custom_rel_x")
        with c2:
            y_col = st.selectbox("Y-axis variable", numeric_cols,
                                 index=min(1, len(numeric_cols)-1), key="custom_rel_y")
        with c3:
            color_col = st.selectbox("Color by (optional)", ["(none)"] + categorical_cols, key="custom_rel_color")
        color_arg = color_col if color_col != "(none)" else None
        fig = px.scatter(df, x=x_col, y=y_col, color=color_arg,
                         title=f"Relationship: {y_col} vs {x_col}",
                         trendline="ols" if color_arg is None else None)
        st.plotly_chart(fig, use_container_width=True, key="custom_scatter_chart")

# ---- Comparison / Bar ----
elif analysis_type == "Comparison (Bar)":
    if not categorical_cols or not numeric_cols:
        st.warning("Need at least one categorical and one numeric column.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            cat = st.selectbox("Category (X-axis)", categorical_cols, key="custom_bar_cat")
        with c2:
            num = st.selectbox("Value (Y-axis)", numeric_cols, key="custom_bar_num")
        with c3:
            # FIX #7: "limit" → clearly labelled "Top N categories"
            topn = st.slider("Top N categories", 3, 50, 10, key="custom_bar_topn",
                             help="Show only the top N categories by average value")
        agg = st.selectbox("Aggregation", ["mean", "sum", "count", "median"], key="custom_bar_agg")
        grouped = df.groupby(cat)[num].agg(agg).reset_index()
        grouped = grouped.nlargest(topn, num)
        fig = px.bar(grouped, x=cat, y=num,
                     title=f"{agg.capitalize()} of {num} by {cat} (Top {topn})")
        st.plotly_chart(fig, use_container_width=True, key="custom_bar_chart")

# ---- Correlation Heatmap ----
elif analysis_type == "Correlation (Heatmap)":
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns.")
    else:
        selected_num = st.multiselect("Select numeric columns", numeric_cols,
                                       default=numeric_cols[:min(8, len(numeric_cols))],
                                       key="custom_heatmap_cols")
        if len(selected_num) >= 2:
            corr = df[selected_num].corr()
            fig = px.imshow(corr, color_continuous_scale="RdBu_r",
                            title="Correlation Matrix", text_auto=".2f")
            st.plotly_chart(fig, use_container_width=True, key="custom_heatmap_chart")
        else:
            st.warning("Select at least 2 columns.")

# ---- Box Plot ----
elif analysis_type == "Box Plot":
    if not numeric_cols:
        st.warning("No numeric columns available.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            y_col = st.selectbox("Value column (Y-axis)", numeric_cols, key="custom_box_y")
        with c2:
            x_col = st.selectbox("Group by (X-axis, optional)", ["(none)"] + categorical_cols, key="custom_box_x")
        x_arg = x_col if x_col != "(none)" else None
        fig = px.box(df, x=x_arg, y=y_col,
                     title=f"Box Plot: {y_col}" + (f" by {x_col}" if x_arg else ""))
        st.plotly_chart(fig, use_container_width=True, key="custom_box_chart")

# ---- Line Chart ----
elif analysis_type == "Line Chart":
    if not numeric_cols:
        st.warning("No numeric columns available.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("X-axis (time or index)", all_cols, key="custom_line_x")
        with c2:
            y_col = st.selectbox("Y-axis (value)", numeric_cols, key="custom_line_y")
        color_col = st.selectbox("Color / group by (optional)", ["(none)"] + categorical_cols, key="custom_line_color")
        color_arg = color_col if color_col != "(none)" else None
        plot_df = df.dropna(subset=[x_col, y_col]).sort_values(x_col)
        fig = px.line(plot_df, x=x_col, y=y_col, color=color_arg,
                      title=f"{y_col} over {x_col}")
        st.plotly_chart(fig, use_container_width=True, key="custom_line_chart")

st.markdown("---")

# ===============================
# 🔹 MATPLOTLIB CHART
# ===============================
st.subheader("📉 Matplotlib Chart")
if numeric_cols:
    mpl_col = st.selectbox("Column", numeric_cols, key="mpl_col")
    clean_data = df[mpl_col].dropna()

    if clean_data.empty:
        st.warning("No valid data to plot.")
    else:
        fig_mpl, ax = plt.subplots(figsize=(10, 4))
        ax.hist(clean_data, bins=30, color="#636EFA", edgecolor="white")
        ax.set_title(f"Histogram of {mpl_col}", fontsize=14)
        ax.set_xlabel(mpl_col)
        ax.set_ylabel("Count")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        st.pyplot(fig_mpl)

st.markdown("---")

# ===============================
# 🔹 SMART INTERPRETATION
# ===============================
st.subheader("🧠 Smart Interpretation")
if numeric_cols:
    interp_col = st.selectbox("Select column to interpret", numeric_cols, key="interp_col")
    series = df[interp_col].dropna()
    if not series.empty:
        mean_val = series.mean()
        median_val = series.median()
        skew_val = series.skew()
        Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
        IQR = Q3 - Q1
        n_outliers = int(((series < Q1 - 1.5*IQR) | (series > Q3 + 1.5*IQR)).sum())

        parts = [f"**`{interp_col}`**: "]
        if skew_val > 1:
            parts.append("Distribution is **strongly right-skewed** (long tail on the right). ")
        elif skew_val < -1:
            parts.append("Distribution is **strongly left-skewed** (long tail on the left). ")
        else:
            parts.append("Distribution is **roughly symmetric**. ")

        if mean_val > median_val:
            parts.append("Mean > Median — possible high-value outliers pulling the average up. ")
        elif mean_val < median_val:
            parts.append("Median > Mean — possible low-value outliers pulling the average down. ")

        parts.append(f"Detected **{n_outliers} potential outliers** using IQR method.")
        st.info("".join(parts))
else:
    st.info("No numeric columns available for interpretation.")
