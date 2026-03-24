import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import apply_theme, theme_colors, plotly_layout

st.session_state["_page_key"] = "3_Visualization"
apply_theme()

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import io

if "df" not in st.session_state:
    st.session_state.df = None

st.title("📊 Visualization Studio")

if st.session_state.df is None:
    st.warning("Upload data first on the Upload page.")
    st.stop()

# ── DEDUPLICATE COLUMNS ────────────────────────────────────────────────────────
raw = st.session_state.df.copy()
seen = {}
new_cols = []
for col in raw.columns:
    if col in seen:
        seen[col] += 1
        new_cols.append(f"{col}_{seen[col]}")
    else:
        seen[col] = 0
        new_cols.append(col)
raw.columns = new_cols
df = raw

dark       = st.session_state.get("dark_mode", False)
COLORS     = theme_colors()
LAYOUT     = plotly_layout(dark)
categorical_cols = df.select_dtypes(include=["object","category"]).columns.tolist()
numeric_cols     = df.select_dtypes(include=np.number).columns.tolist()
all_cols         = df.columns.tolist()

# ── HELPERS ────────────────────────────────────────────────────────────────────
def style_fig(fig, title="", xlab="", ylab="", legend_title=""):
    fig.update_layout(
        **LAYOUT,
        title=dict(text=f"<b>{title}</b>", x=0.02, xanchor="left"),
        xaxis_title=f"<b>{xlab}</b>" if xlab else "",
        yaxis_title=f"<b>{ylab}</b>" if ylab else "",
    )
    gc = "#334155" if dark else "#f1f5f9"
    fig.update_xaxes(showgrid=True, gridcolor=gc, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=gc, zeroline=False)
    if legend_title:
        fig.update_layout(legend_title_text=legend_title)
    return fig

def chart_download_buttons(fig, key):
    """Offer PNG download via kaleido and HTML download as fallback."""
    c1, c2 = st.columns([1,1])
    with c1:
        try:
            import kaleido  # noqa
            png_bytes = fig.to_image(format="png", width=1400, height=700, scale=2)
            st.download_button(
                "⬇️ Download PNG",
                png_bytes,
                file_name=f"chart_{key}.png",
                mime="image/png",
                key=f"dl_png_{key}",
            )
        except Exception:
            # fallback to html
            export_fig = go.Figure(fig)
            export_fig.update_layout(paper_bgcolor="white", plot_bgcolor="#f8fafc",
                                     font_color="#0f172a", title_font_color="#0f172a")
            html_str = export_fig.to_html(
                include_plotlyjs="cdn", full_html=True,
                config={"toImageButtonOptions":{"format":"png","filename":f"chart_{key}","height":700,"width":1400,"scale":2}}
            )
            st.download_button(
                "⬇️ Download chart (HTML → use 📷 icon for PNG)",
                html_str.encode(),
                file_name=f"chart_{key}.html",
                mime="text/html",
                key=f"dl_html_{key}",
            )
    with c2:
        html_str2 = fig.to_html(include_plotlyjs="cdn", full_html=True)
        st.download_button(
            "⬇️ Download HTML (interactive)",
            html_str2.encode(),
            file_name=f"chart_{key}_interactive.html",
            mime="text/html",
            key=f"dl_html2_{key}",
        )

def chart_description(desc_text):
    """Show a styled description box beneath a chart."""
    bg  = "rgba(30,41,59,0.7)" if dark else "rgba(241,245,249,0.9)"
    col = "#94a3b8" if dark else "#475569"
    st.markdown(f"""<div style="background:{bg};border-radius:8px;padding:10px 16px;
        margin-top:4px;font-size:13px;color:{col};line-height:1.6">{desc_text}</div>""",
        unsafe_allow_html=True)

# ── FILTERS ────────────────────────────────────────────────────────────────────
with st.expander("🔎 Global Filters", expanded=False):
    fc1, fc2 = st.columns(2)
    with fc1:
        if categorical_cols:
            fc = st.selectbox("Filter by category column", ["(none)"] + categorical_cols, key="f_cat")
            if fc != "(none)":
                vals = df[fc].astype(str).dropna().unique().tolist()
                sel  = st.multiselect("Keep values", vals, default=vals, key="f_cat_v")
                if sel: df = df[df[fc].astype(str).isin(sel)]
    with fc2:
        if numeric_cols:
            fn = st.selectbox("Filter by numeric range", ["(none)"] + numeric_cols, key="f_num")
            if fn != "(none)":
                mn, mx = float(df[fn].min()), float(df[fn].max())
                if mn < mx:
                    rng = st.slider("Range", mn, mx, (mn, mx), key="f_rng")
                    df  = df[df[fn].between(rng[0], rng[1])]

if df.empty:
    st.warning("No data after filtering.")
    st.stop()
st.caption(f"Working with **{len(df):,}** rows after filtering.")
st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════════
# ANALYTICAL DASHBOARD (6 fixed charts)
# ════════════════════════════════════════════════════════════════════════════════
st.subheader("📈 Analytical Dashboard")

# Row 1
r1c1, r1c2 = st.columns(2, gap="medium")
r2c1, r2c2 = st.columns(2, gap="medium")
r3c1, r3c2 = st.columns(2, gap="medium")

with r1c1:
    with st.container(border=True):
        st.markdown("**📊 Distribution — Histogram**")
        st.caption("Shows frequency distribution of a numeric column. Bins = number of bars.")
        if numeric_cols:
            g1c = st.selectbox("Column", numeric_cols, key="g1c")
            g1b = st.slider("Bins", 5, 80, 20, key="g1b")
            g1col = st.selectbox("Color by", ["(none)"] + categorical_cols, key="g1col")
            ca1 = g1col if g1col != "(none)" else None
            fig = px.histogram(df, x=g1c, nbins=g1b, color=ca1,
                               color_discrete_sequence=COLORS,
                               labels={g1c: g1c.replace("_"," "), "count": "Frequency"})
            fig = style_fig(fig, f"Distribution of {g1c}", g1c.replace("_"," "), "Frequency",
                            legend_title=g1col if ca1 else "")
            st.plotly_chart(fig, use_container_width=True, key="g1")
            chart_description(f"<b>X-axis:</b> {g1c} (numeric values) &nbsp;|&nbsp; <b>Y-axis:</b> Frequency (count of rows) &nbsp;|&nbsp; Each bar spans {g1b} equal bins across the range.")
            chart_download_buttons(fig, "g1")
        else:
            st.info("No numeric columns available.")

with r1c2:
    with st.container(border=True):
        st.markdown("**📊 Comparison — Bar Chart**")
        st.caption("Aggregates a numeric value per category. Great for comparing group means/sums.")
        if categorical_cols and numeric_cols:
            g2cat = st.selectbox("Category (X-axis)", categorical_cols, key="g2cat")
            g2num = st.selectbox("Value (Y-axis)", numeric_cols, key="g2num")
            g2n   = st.slider("Top N", 3, 30, 10, key="g2n")
            g2agg = st.selectbox("Aggregation", ["mean","sum","count","median"], key="g2agg")
            gd    = df.groupby(g2cat)[g2num].agg(g2agg).reset_index().nlargest(g2n, g2num)
            fig   = px.bar(gd, x=g2cat, y=g2num, color=g2cat,
                           color_discrete_sequence=COLORS,
                           labels={g2cat: g2cat.replace("_"," "),
                                   g2num: g2num.replace("_"," ")})
            fig = style_fig(fig, f"{g2agg.capitalize()} of {g2num} by {g2cat} (Top {g2n})",
                            g2cat.replace("_"," "), f"{g2agg.capitalize()} of {g2num}")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="g2")
            chart_description(f"<b>X-axis:</b> {g2cat} categories (top {g2n}) &nbsp;|&nbsp; <b>Y-axis:</b> {g2agg} of {g2num} &nbsp;|&nbsp; Each bar height = {g2agg} value for that group.")
            chart_download_buttons(fig, "g2")
        else:
            st.info("Need at least one categorical and one numeric column.")

with r2c1:
    with st.container(border=True):
        st.markdown("**🔵 Relationship — Scatter Plot**")
        st.caption("Reveals correlations between two numeric variables. Each dot = one row.")
        if len(numeric_cols) >= 2:
            g3x   = st.selectbox("X-axis", numeric_cols, key="g3x")
            g3y   = st.selectbox("Y-axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="g3y")
            g3col = st.selectbox("Color by", ["(none)"] + categorical_cols, key="g3col")
            ca3   = g3col if g3col != "(none)" else None
            fig   = px.scatter(df, x=g3x, y=g3y, color=ca3,
                               color_discrete_sequence=COLORS, opacity=0.72,
                               labels={g3x: g3x.replace("_"," "), g3y: g3y.replace("_"," ")})
            fig = style_fig(fig, f"{g3y} vs {g3x}", g3x.replace("_"," "), g3y.replace("_"," "),
                            legend_title=g3col if ca3 else "")
            st.plotly_chart(fig, use_container_width=True, key="g3")
            chart_description(f"<b>X-axis:</b> {g3x} &nbsp;|&nbsp; <b>Y-axis:</b> {g3y} &nbsp;|&nbsp; Each point is one observation. Clustering indicates correlation.")
            chart_download_buttons(fig, "g3")
        else:
            st.info("Need ≥2 numeric columns.")

with r2c2:
    with st.container(border=True):
        st.markdown("**🌡️ Correlation Heatmap**")
        st.caption("Shows pairwise correlations between all numeric columns. Red = positive, blue = negative.")
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            fig  = px.imshow(corr, color_continuous_scale="RdBu_r", text_auto=".2f",
                             labels=dict(color="Correlation"), aspect="auto")
            fig = style_fig(fig, "Correlation Matrix — Numeric Columns")
            fig.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True, key="g4")
            chart_description("Each cell shows the Pearson correlation coefficient (−1 to +1). Values near ±1 indicate strong linear relationships. Diagonal is always 1.0.")
            chart_download_buttons(fig, "g4")
        else:
            st.info("Need ≥2 numeric columns.")

with r3c1:
    with st.container(border=True):
        st.markdown("**📦 Distribution — Box Plot**")
        st.caption("Shows median, quartiles and outliers. Best for comparing distributions across groups.")
        if numeric_cols:
            g5y = st.selectbox("Value (Y-axis)", numeric_cols, key="g5y")
            g5x = st.selectbox("Group by (X-axis)", ["(none)"] + categorical_cols, key="g5x")
            xa  = g5x if g5x != "(none)" else None
            fig = px.box(df, x=xa, y=g5y, color=xa,
                         color_discrete_sequence=COLORS, points="outliers",
                         labels={g5y: g5y.replace("_"," ")})
            xtitle = g5x.replace("_"," ") if xa else ""
            fig = style_fig(fig, f"Box Plot of {g5y}" + (f" by {g5x}" if xa else ""),
                            xtitle, g5y.replace("_"," "), legend_title=g5x if xa else "")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="g5")
            chart_description(f"<b>Y-axis:</b> {g5y} &nbsp;|&nbsp; Box = IQR (25th–75th percentile) · Line = median · Whiskers = 1.5×IQR · Dots = outliers.")
            chart_download_buttons(fig, "g5")
        else:
            st.info("No numeric columns.")

with r3c2:
    with st.container(border=True):
        st.markdown("**📈 Trend — Line Chart**")
        st.caption("Tracks how a value changes over a sequence or time. Ideal for time-series data.")
        if numeric_cols:
            g6x   = st.selectbox("X-axis", all_cols, key="g6x")
            g6y   = st.selectbox("Y-axis (numeric)", numeric_cols, key="g6y")
            g6col = st.selectbox("Color by", ["(none)"] + categorical_cols, key="g6col")
            ca6   = g6col if g6col != "(none)" else None
            try:
                cols_needed = [g6x, g6y] + ([g6col] if ca6 else [])
                pld = df[cols_needed].dropna().reset_index(drop=True).sort_values(g6x)
                fig = px.line(pld, x=g6x, y=g6y, color=ca6,
                              color_discrete_sequence=COLORS, markers=True,
                              labels={g6x: g6x.replace("_"," "), g6y: g6y.replace("_"," ")})
                fig = style_fig(fig, f"{g6y} over {g6x}", g6x.replace("_"," "), g6y.replace("_"," "),
                                legend_title=g6col if ca6 else "")
                st.plotly_chart(fig, use_container_width=True, key="g6")
                chart_description(f"<b>X-axis:</b> {g6x} (sorted) &nbsp;|&nbsp; <b>Y-axis:</b> {g6y} &nbsp;|&nbsp; Lines connect consecutive data points; markers show individual values.")
                chart_download_buttons(fig, "g6")
            except Exception as e:
                st.warning(f"Could not render line chart: {e}")
        else:
            st.info("No numeric columns.")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════════
# CUSTOM CHART BUILDER (10 chart types)
# ════════════════════════════════════════════════════════════════════════════════
st.subheader("🔧 Custom Chart Builder")
st.caption("Build any chart from scratch — choose type, columns, aggregations and styling options.")

CHART_TYPES = [
    "Histogram", "Bar Chart", "Grouped Bar Chart", "Scatter Plot",
    "Line Chart", "Box Plot", "Violin Plot",
    "Correlation Heatmap", "3D Scatter Plot",
    "Pie / Donut Chart", "Area Chart", "Bubble Chart"
]

chart_type = st.selectbox("Chart type", CHART_TYPES, key="ctype")
fig = None
desc_txt = ""

if chart_type == "Histogram":
    if not numeric_cols: st.warning("No numeric columns."); st.stop()
    c1,c2,c3 = st.columns(3)
    col   = c1.selectbox("Column (X-axis)", numeric_cols, key="h_col")
    nbins = c2.slider("Bins", 5, 100, 20, key="h_bins")
    colby = c3.selectbox("Color by", ["(none)"] + categorical_cols, key="h_col2")
    ca    = colby if colby != "(none)" else None
    fig   = px.histogram(df, x=col, nbins=nbins, color=ca,
                         color_discrete_sequence=COLORS,
                         labels={col: col.replace("_"," "), "count": "Frequency"})
    fig = style_fig(fig, f"Distribution of {col}", col.replace("_"," "), "Frequency",
                    legend_title=colby if ca else "")
    desc_txt = f"<b>X-axis:</b> {col} (numeric) &nbsp;|&nbsp; <b>Y-axis:</b> Frequency &nbsp;|&nbsp; {nbins} equal-width bins."

elif chart_type == "Bar Chart":
    if not (categorical_cols and numeric_cols):
        st.warning("Need categorical + numeric columns."); st.stop()
    c1,c2,c3,c4 = st.columns(4)
    cat  = c1.selectbox("X-axis (category)", categorical_cols, key="b_cat")
    num  = c2.selectbox("Y-axis (value)", numeric_cols, key="b_num")
    agg  = c3.selectbox("Aggregation", ["mean","sum","count","median"], key="b_agg")
    topn = c4.slider("Top N categories", 3, 50, 15, key="b_topn")
    gd   = df.groupby(cat)[num].agg(agg).reset_index().nlargest(topn, num)
    fig  = px.bar(gd, x=cat, y=num, color=cat, color_discrete_sequence=COLORS,
                  labels={cat: cat.replace("_"," "), num: f"{agg} of {num.replace('_',' ')}"})
    fig = style_fig(fig, f"{agg.capitalize()} of {num} by {cat} (Top {topn})",
                    cat.replace("_"," "), f"{agg.capitalize()} of {num.replace('_',' ')}")
    fig.update_layout(showlegend=False)
    desc_txt = f"<b>X-axis:</b> {cat} (top {topn} categories) &nbsp;|&nbsp; <b>Y-axis:</b> {agg} of {num}."

elif chart_type == "Grouped Bar Chart":
    if not (categorical_cols and numeric_cols):
        st.warning("Need categorical + numeric columns."); st.stop()
    c1,c2,c3,c4 = st.columns(4)
    cat   = c1.selectbox("X-axis", categorical_cols, key="gb_cat")
    num   = c2.selectbox("Y-axis", numeric_cols, key="gb_num")
    group = c3.selectbox("Group by (color)", ["(none)"] + categorical_cols, key="gb_grp")
    agg   = c4.selectbox("Aggregation", ["mean","sum","count","median"], key="gb_agg")
    ga    = group if group != "(none)" else None
    if ga:
        gd = df.groupby([cat, ga])[num].agg(agg).reset_index()
        fig = px.bar(gd, x=cat, y=num, color=ga, barmode="group",
                     color_discrete_sequence=COLORS,
                     labels={cat: cat.replace("_"," "), num: f"{agg} of {num.replace('_',' ')}", ga: ga.replace("_"," ")})
        fig = style_fig(fig, f"{agg.capitalize()} of {num} grouped by {ga}",
                        cat.replace("_"," "), f"{agg.capitalize()} of {num.replace('_',' ')}",
                        legend_title=ga.replace("_"," "))
        desc_txt = f"<b>X-axis:</b> {cat} &nbsp;|&nbsp; <b>Y-axis:</b> {agg} of {num} &nbsp;|&nbsp; Bars grouped by {ga} (colour = group)."
    else:
        st.warning("Select a 'Group by' column for grouped bar chart.")

elif chart_type == "Scatter Plot":
    if len(numeric_cols) < 2: st.warning("Need ≥2 numeric columns."); st.stop()
    c1,c2,c3,c4 = st.columns(4)
    xc    = c1.selectbox("X-axis", numeric_cols, key="sc_x")
    yc    = c2.selectbox("Y-axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="sc_y")
    colby = c3.selectbox("Color by", ["(none)"] + categorical_cols, key="sc_col")
    trend = c4.checkbox("Trendline (OLS)", key="sc_trend")
    ca    = colby if colby != "(none)" else None
    fig   = px.scatter(df, x=xc, y=yc, color=ca, color_discrete_sequence=COLORS,
                       trendline="ols" if (trend and not ca) else None, opacity=0.75,
                       labels={xc: xc.replace("_"," "), yc: yc.replace("_"," ")})
    fig = style_fig(fig, f"Relationship: {yc} vs {xc}",
                    xc.replace("_"," "), yc.replace("_"," "), legend_title=colby if ca else "")
    desc_txt = f"<b>X-axis:</b> {xc} &nbsp;|&nbsp; <b>Y-axis:</b> {yc} &nbsp;|&nbsp; Each point = one row." + (" OLS trendline shown." if trend else "")

elif chart_type == "Line Chart":
    if not numeric_cols: st.warning("No numeric columns."); st.stop()
    c1,c2,c3 = st.columns(3)
    xc    = c1.selectbox("X-axis", all_cols, key="ln_x")
    yc    = c2.selectbox("Y-axis", numeric_cols, key="ln_y")
    colby = c3.selectbox("Color by", ["(none)"] + categorical_cols, key="ln_col")
    ca    = colby if colby != "(none)" else None
    try:
        cols_needed = [xc, yc] + ([colby] if ca else [])
        pld = df[cols_needed].dropna().reset_index(drop=True).sort_values(xc)
        fig = px.line(pld, x=xc, y=yc, color=ca, color_discrete_sequence=COLORS, markers=True,
                      labels={xc: xc.replace("_"," "), yc: yc.replace("_"," ")})
        fig = style_fig(fig, f"{yc} over {xc}",
                        xc.replace("_"," "), yc.replace("_"," "), legend_title=colby if ca else "")
        desc_txt = f"<b>X-axis:</b> {xc} (sorted) &nbsp;|&nbsp; <b>Y-axis:</b> {yc}."
    except Exception as e:
        st.warning(f"Could not render line chart: {e}")

elif chart_type == "Box Plot":
    if not numeric_cols: st.warning("No numeric columns."); st.stop()
    c1,c2 = st.columns(2)
    yc  = c1.selectbox("Y-axis (value)", numeric_cols, key="bx_y")
    xc  = c2.selectbox("X-axis / group by", ["(none)"] + categorical_cols, key="bx_x")
    xa  = xc if xc != "(none)" else None
    fig = px.box(df, x=xa, y=yc, color=xa, color_discrete_sequence=COLORS, points="outliers",
                 labels={yc: yc.replace("_"," ")})
    xtitle = xc.replace("_"," ") if xa else ""
    fig = style_fig(fig, f"Box Plot of {yc}" + (f" grouped by {xc}" if xa else ""),
                    xtitle, yc.replace("_"," "), legend_title=xc if xa else "")
    fig.update_layout(showlegend=False)
    desc_txt = f"<b>Y-axis:</b> {yc} &nbsp;|&nbsp; Box = IQR · Median line · Whiskers = 1.5×IQR · Outlier dots shown."

elif chart_type == "Violin Plot":
    if not numeric_cols: st.warning("No numeric columns."); st.stop()
    c1,c2 = st.columns(2)
    yc = c1.selectbox("Y-axis (value)", numeric_cols, key="vl_y")
    xc = c2.selectbox("Group by (X-axis)", ["(none)"] + categorical_cols, key="vl_x")
    xa = xc if xc != "(none)" else None
    fig = px.violin(df, x=xa, y=yc, color=xa, color_discrete_sequence=COLORS,
                    box=True, points="outliers", labels={yc: yc.replace("_"," ")})
    xtitle = xc.replace("_"," ") if xa else ""
    fig = style_fig(fig, f"Violin Plot of {yc}" + (f" by {xc}" if xa else ""),
                    xtitle, yc.replace("_"," "), legend_title=xc if xa else "")
    fig.update_layout(showlegend=False)
    desc_txt = f"<b>Y-axis:</b> {yc} &nbsp;|&nbsp; Width of violin = density of data at that value. Inner box = IQR."

elif chart_type == "Correlation Heatmap":
    if len(numeric_cols) < 2: st.warning("Need ≥2 numeric columns."); st.stop()
    sel_cols = st.multiselect("Columns to include", numeric_cols,
                               default=numeric_cols[:min(12, len(numeric_cols))], key="hm_cols")
    if len(sel_cols) >= 2:
        corr = df[sel_cols].corr()
        fig  = px.imshow(corr, color_continuous_scale="RdBu_r", text_auto=".2f",
                         aspect="auto", labels=dict(color="Correlation"))
        fig = style_fig(fig, "Pearson Correlation Matrix")
        fig.update_layout(xaxis_title="", yaxis_title="")
        desc_txt = "Pearson correlation (−1 to +1). Red = positive correlation, Blue = negative. Diagonal = 1.0 (self-correlation)."

elif chart_type == "3D Scatter Plot":
    if len(numeric_cols) < 3: st.warning("Need ≥3 numeric columns for 3D."); st.stop()
    c1,c2,c3,c4 = st.columns(4)
    xc    = c1.selectbox("X-axis", numeric_cols, key="3d_x")
    yc    = c2.selectbox("Y-axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="3d_y")
    zc    = c3.selectbox("Z-axis", numeric_cols, index=min(2,len(numeric_cols)-1), key="3d_z")
    colby = c4.selectbox("Color by", ["(none)"] + categorical_cols + numeric_cols, key="3d_col")
    ca    = colby if colby != "(none)" else None
    sc_bg = "rgba(15,23,42,0.95)" if dark else "rgba(248,250,252,1)"
    ax_c  = "#94a3b8" if dark else "#475569"
    fig   = px.scatter_3d(df.dropna(subset=[xc,yc,zc]), x=xc, y=yc, z=zc, color=ca,
                          color_discrete_sequence=COLORS, opacity=0.78,
                          labels={xc: xc.replace("_"," "), yc: yc.replace("_"," "), zc: zc.replace("_"," ")})
    fig.update_layout(
        title=dict(text=f"<b>3D Scatter: {xc} × {yc} × {zc}</b>", x=0.02),
        font_family="'Space Grotesk', sans-serif",
        font_color="#e2e8f0" if dark else "#1e293b",
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(title=f"<b>{xc.replace('_',' ')}</b>", color=ax_c, backgroundcolor=sc_bg, gridcolor="#334155" if dark else "#e2e8f0"),
            yaxis=dict(title=f"<b>{yc.replace('_',' ')}</b>", color=ax_c, backgroundcolor=sc_bg, gridcolor="#334155" if dark else "#e2e8f0"),
            zaxis=dict(title=f"<b>{zc.replace('_',' ')}</b>", color=ax_c, backgroundcolor=sc_bg, gridcolor="#334155" if dark else "#e2e8f0"),
            bgcolor=sc_bg,
        ),
        legend_title_text=colby if ca else "",
    )
    desc_txt = f"<b>X:</b> {xc} &nbsp;|&nbsp; <b>Y:</b> {yc} &nbsp;|&nbsp; <b>Z:</b> {zc} &nbsp;|&nbsp; Drag to rotate · Scroll to zoom · Double-click to reset view."

elif chart_type == "Pie / Donut Chart":
    if not categorical_cols: st.warning("No categorical columns."); st.stop()
    c1,c2,c3 = st.columns(3)
    cat   = c1.selectbox("Category", categorical_cols, key="pi_cat")
    topn  = c2.slider("Top N slices", 3, 20, 8, key="pi_topn")
    donut = c3.checkbox("Donut style", value=True, key="pi_donut")
    counts = df[cat].value_counts().reset_index()
    counts.columns = [cat, "count"]
    top   = counts.head(topn)
    other = counts.iloc[topn:]
    if not other.empty:
        top = pd.concat([top, pd.DataFrame([{cat: "Other", "count": other["count"].sum()}])], ignore_index=True)
    fig = px.pie(top, names=cat, values="count",
                 color_discrete_sequence=COLORS, hole=0.42 if donut else 0)
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(title=dict(text=f"<b>Distribution of {cat}</b>", x=0.02),
                      font_family="'Space Grotesk', sans-serif",
                      paper_bgcolor="rgba(0,0,0,0)",
                      font_color="#e2e8f0" if dark else "#1e293b",
                      legend_title=cat.replace("_"," "))
    desc_txt = f"<b>Slices:</b> Top {topn} categories of {cat} + 'Other' &nbsp;|&nbsp; Labels show percentage and category name."

elif chart_type == "Area Chart":
    if not numeric_cols: st.warning("No numeric columns."); st.stop()
    c1,c2,c3 = st.columns(3)
    xc    = c1.selectbox("X-axis", all_cols, key="ar_x")
    yc    = c2.selectbox("Y-axis", numeric_cols, key="ar_y")
    colby = c3.selectbox("Color by", ["(none)"] + categorical_cols, key="ar_col")
    ca    = colby if colby != "(none)" else None
    try:
        cols_needed = [xc, yc] + ([colby] if ca else [])
        pld = df[cols_needed].dropna().reset_index(drop=True).sort_values(xc)
        fig = px.area(pld, x=xc, y=yc, color=ca, color_discrete_sequence=COLORS,
                      labels={xc: xc.replace("_"," "), yc: yc.replace("_"," ")})
        fig = style_fig(fig, f"Area: {yc} over {xc}",
                        xc.replace("_"," "), yc.replace("_"," "), legend_title=colby if ca else "")
        desc_txt = f"<b>X-axis:</b> {xc} (sorted) &nbsp;|&nbsp; <b>Y-axis:</b> {yc} &nbsp;|&nbsp; Filled area highlights cumulative magnitude."
    except Exception as e:
        st.warning(f"Could not render area chart: {e}")

elif chart_type == "Bubble Chart":
    if len(numeric_cols) < 3: st.warning("Need ≥3 numeric columns."); st.stop()
    c1,c2,c3,c4 = st.columns(4)
    xc   = c1.selectbox("X-axis", numeric_cols, key="bb_x")
    yc   = c2.selectbox("Y-axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="bb_y")
    szc  = c3.selectbox("Bubble size", numeric_cols, index=min(2,len(numeric_cols)-1), key="bb_sz")
    colby= c4.selectbox("Color by", ["(none)"] + categorical_cols, key="bb_col")
    ca   = colby if colby != "(none)" else None
    fig  = px.scatter(df.dropna(subset=[xc,yc,szc]), x=xc, y=yc, size=szc, color=ca,
                      color_discrete_sequence=COLORS, opacity=0.72,
                      labels={xc: xc.replace("_"," "), yc: yc.replace("_"," "), szc: szc.replace("_"," ")})
    fig = style_fig(fig, f"Bubble: {xc} × {yc} (size = {szc})",
                    xc.replace("_"," "), yc.replace("_"," "), legend_title=colby if ca else "")
    desc_txt = f"<b>X:</b> {xc} &nbsp;|&nbsp; <b>Y:</b> {yc} &nbsp;|&nbsp; <b>Bubble size:</b> {szc} &nbsp;|&nbsp; Larger bubbles = higher {szc} value."

if fig is not None:
    st.plotly_chart(fig, use_container_width=True, key="custom_chart")
    if desc_txt:
        chart_description(desc_txt)
    chart_download_buttons(fig, "custom")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════════
# SMART INTERPRETATION
# ════════════════════════════════════════════════════════════════════════════════
st.subheader("🧠 Smart Interpretation")
if numeric_cols:
    ic = st.selectbox("Select a numeric column to analyse", numeric_cols, key="interp_col")
    s  = df[ic].dropna()
    if not s.empty:
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        IQR    = Q3 - Q1
        n_out  = int(((s < Q1 - 1.5*IQR) | (s > Q3 + 1.5*IQR)).sum())
        skew   = s.skew()
        parts  = [f"**`{ic}`** — "]
        if   skew > 1:  parts.append("Strongly **right-skewed** (long tail on the right). ")
        elif skew < -1: parts.append("Strongly **left-skewed** (long tail on the left). ")
        else:            parts.append("Roughly **symmetric** distribution. ")
        if   s.mean() > s.median(): parts.append("Mean > Median — possible high-value outliers. ")
        elif s.mean() < s.median(): parts.append("Median > Mean — possible low-value outliers. ")
        parts.append(f"Detected **{n_out} potential outliers** using IQR method. ")
        parts.append(f"Range: **{s.min():.3g}** → **{s.max():.3g}** · Mean: **{s.mean():.3g}** · Std: **{s.std():.3g}**")
        st.info("".join(parts))

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════════
# MATPLOTLIB CHARTS (required by CW)
# ════════════════════════════════════════════════════════════════════════════════
st.subheader("📉 Matplotlib Charts")
st.caption("Static, publication-quality charts rendered with Matplotlib.")

if numeric_cols:
    mc1, mc2 = st.columns(2)
    mpl_col  = mc1.selectbox("Column", numeric_cols, key="mpl_col")
    mpl_type = mc2.radio("Chart type", ["Histogram","KDE (density)","Box Plot","Violin"],
                         horizontal=True, key="mpl_type")
    clean_data = df[mpl_col].dropna()

    if not clean_data.empty:
        mpl_bg   = "#0f172a" if dark else "#ffffff"
        mpl_ax   = "#1e293b" if dark else "#f8fafc"
        mpl_tc   = "#e2e8f0" if dark else "#0f172a"
        mpl_gc   = "#334155" if dark else "#e2e8f0"
        mpl_col_hex = "#818cf8" if dark else "#4f46e5"

        matplotlib.rcParams.update({
            "text.color": mpl_tc, "axes.labelcolor": mpl_tc,
            "xtick.color": mpl_tc, "ytick.color": mpl_tc,
            "axes.edgecolor": "#475569" if dark else "#cbd5e1"
        })

        fig_mpl, ax = plt.subplots(figsize=(10, 4))
        fig_mpl.patch.set_facecolor(mpl_bg)
        ax.set_facecolor(mpl_ax)
        ax.grid(True, color=mpl_gc, linewidth=0.7, alpha=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        if mpl_type == "Histogram":
            ax.hist(clean_data, bins=30, color=mpl_col_hex, edgecolor="white", alpha=0.88)
            ax.set_xlabel(mpl_col.replace("_"," "), fontsize=12, labelpad=8)
            ax.set_ylabel("Frequency", fontsize=12, labelpad=8)
            ax.set_title(f"Histogram of {mpl_col}", fontsize=14, fontweight="bold", pad=12, color=mpl_tc)

        elif mpl_type == "KDE (density)":
            clean_data.plot.density(ax=ax, color=mpl_col_hex, linewidth=2.5)
            ax.set_xlabel(mpl_col.replace("_"," "), fontsize=12, labelpad=8)
            ax.set_ylabel("Density", fontsize=12, labelpad=8)
            ax.set_title(f"KDE Density of {mpl_col}", fontsize=14, fontweight="bold", pad=12, color=mpl_tc)
            ax.fill_between(ax.lines[0].get_xdata(), ax.lines[0].get_ydata(), alpha=0.2, color=mpl_col_hex)

        elif mpl_type == "Box Plot":
            bp = ax.boxplot(clean_data, vert=True, patch_artist=True,
                            boxprops=dict(facecolor=mpl_col_hex, alpha=0.7),
                            medianprops=dict(color="white", linewidth=2),
                            whiskerprops=dict(color=mpl_tc), capprops=dict(color=mpl_tc),
                            flierprops=dict(marker="o", color=mpl_col_hex, markersize=4, alpha=0.7))
            ax.set_ylabel(mpl_col.replace("_"," "), fontsize=12, labelpad=8)
            ax.set_xticks([])
            ax.set_title(f"Box Plot of {mpl_col}", fontsize=14, fontweight="bold", pad=12, color=mpl_tc)

        elif mpl_type == "Violin":
            vp = ax.violinplot(clean_data.dropna(), showmedians=True)
            for pc in vp["bodies"]:
                pc.set_facecolor(mpl_col_hex); pc.set_alpha(0.7)
            vp["cmedians"].set_color("white"); vp["cmedians"].set_linewidth(2)
            ax.set_ylabel(mpl_col.replace("_"," "), fontsize=12, labelpad=8)
            ax.set_xticks([])
            ax.set_title(f"Violin Plot of {mpl_col}", fontsize=14, fontweight="bold", pad=12, color=mpl_tc)

        st.pyplot(fig_mpl)
        buf = io.BytesIO()
        fig_mpl.savefig(buf, format="png", dpi=160, bbox_inches="tight", facecolor=mpl_bg)
        st.download_button("⬇️ Download Matplotlib PNG", buf.getvalue(),
                           f"matplotlib_{mpl_col}_{mpl_type.lower().replace(' ','_')}.png",
                           mime="image/png", key="mpl_dl")
        plt.close(fig_mpl)
