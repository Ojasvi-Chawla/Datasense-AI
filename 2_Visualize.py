import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header, apply_plotly_style

st.set_page_config(page_title="Visualize · DataSense", page_icon="📊", layout="wide")
inject_css()
sidebar_dataset_info()

page_header("📊", "Visualize", "Build interactive charts from your data")
st.markdown('<hr>', unsafe_allow_html=True)

# ── Sidebar open hint ─────────────────────────────────────────────────────────
st.markdown("""
<div style="background:rgba(0,245,160,0.06); border:1px solid rgba(0,245,160,0.2);
border-radius:10px; padding:10px 16px; margin-bottom:16px; display:flex; align-items:center; gap:10px;">
    <span style="font-size:1.3rem;">👈</span>
    <span style="font-family:'DM Mono',monospace; font-size:0.8rem; color:#00f5a0;">
        Click the <b>&gt;</b> arrow on the top-left edge to open the <b>Chart Builder</b> panel
    </span>
</div>
""", unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No data loaded. Go to **Upload** first."); st.stop()

df = st.session_state["df"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()
all_cols = df.columns.tolist()

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title">Chart Builder</div>', unsafe_allow_html=True)

    chart_type = st.selectbox("Chart Type", [
        "Bar Chart","Line Chart","Scatter Plot","Histogram",
        "Box Plot","Pie Chart","Heatmap (Correlation)",
        "Area Chart","Violin Plot","Bubble Chart",
    ])

    st.markdown('<div class="section-title" style="margin-top:16px;">Row Limit</div>', unsafe_allow_html=True)
    max_rows = st.slider("Rows to plot", min_value=5,
                         max_value=min(500, len(df)),
                         value=min(10, len(df)), step=5)
    st.caption(f"First **{max_rows}** of {len(df):,} rows")

    st.markdown('<div class="section-title" style="margin-top:16px;">Appearance</div>', unsafe_allow_html=True)
    chart_color = st.color_picker("Primary Color", "#00f5a0")
    color_theme = st.selectbox("Multi-Color Theme", [
        "Plotly","Vivid","Safe","Pastel","Bold","Antique","Prism","Dark24","Light24"
    ])
    chart_title = st.text_input("Custom Title", placeholder="Auto title if blank")
    show_grid   = st.checkbox("Show Y Gridlines", value=True)

    st.markdown('<div class="section-title" style="margin-top:16px;">Columns</div>', unsafe_allow_html=True)

    x_col=y_col=color_col=size_col=val_col=name_col=agg_func=bins=selected_num=None

    if chart_type in ["Bar Chart","Line Chart","Area Chart"]:
        x_col     = st.selectbox("X Axis", all_cols)
        y_col     = st.selectbox("Y Axis (Numeric)", num_cols or all_cols)
        color_col = st.selectbox("Color By", ["None"] + cat_cols)
        agg_func  = st.selectbox("Aggregate Y by", ["None (raw)","Sum","Mean","Count","Max","Min"])

    elif chart_type == "Scatter Plot":
        x_col     = st.selectbox("X Axis", num_cols or all_cols)
        y_col     = st.selectbox("Y Axis", num_cols or all_cols, index=min(1,len(num_cols)-1))
        color_col = st.selectbox("Color By", ["None"] + cat_cols + num_cols)
        size_col  = st.selectbox("Size By",  ["None"] + num_cols)

    elif chart_type == "Histogram":
        x_col = st.selectbox("Column", num_cols or all_cols)
        bins  = st.slider("Bins", 5, 100, 25)

    elif chart_type in ["Box Plot","Violin Plot"]:
        y_col     = st.selectbox("Numeric Column (Y)", num_cols or all_cols)
        x_col     = st.selectbox("Group By (X)", ["None"] + cat_cols)
        color_col = st.selectbox("Color By", ["None"] + cat_cols)

    elif chart_type == "Pie Chart":
        val_col  = st.selectbox("Values",  num_cols or all_cols)
        name_col = st.selectbox("Labels",  cat_cols or all_cols)

    elif chart_type == "Heatmap (Correlation)":
        selected_num = st.multiselect("Columns", num_cols, default=num_cols[:min(8,len(num_cols))])

    elif chart_type == "Bubble Chart":
        x_col    = st.selectbox("X Axis", num_cols or all_cols)
        y_col    = st.selectbox("Y Axis", num_cols or all_cols, index=min(1,len(num_cols)-1))
        size_col = st.selectbox("Bubble Size", num_cols, index=min(2,len(num_cols)-1))
        color_col = st.selectbox("Color By", ["None"] + cat_cols)

# ── Slice to max_rows ─────────────────────────────────────────────────────────
df_plot = df.head(max_rows).copy()

def palette():
    return getattr(px.colors.qualitative, color_theme, px.colors.qualitative.Plotly)

def do_agg(data, x, y, func):
    if not func or func == "None (raw)": return data
    m = {"Sum":"sum","Mean":"mean","Count":"count","Max":"max","Min":"min"}
    return data.groupby(x)[y].agg(m[func]).reset_index()

# ── Render ────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-title">{chart_type} — first {max_rows} rows</div>', unsafe_allow_html=True)

try:
    fig = None
    c_arg = color_col if color_col and color_col != "None" else None

    if chart_type in ["Bar Chart","Line Chart","Area Chart"]:
        use_agg   = agg_func and agg_func != "None (raw)"
        plot_data = do_agg(df_plot, x_col, y_col, agg_func) if use_agg else df_plot
        titl      = chart_title or f"{y_col} by {x_col}"
        kw        = dict(x=x_col, y=y_col, title=titl, template="plotly_dark")
        if c_arg and not use_agg:
            kw["color"] = c_arg; kw["color_discrete_sequence"] = palette()
        else:
            kw["color_discrete_sequence"] = [chart_color]
        if chart_type == "Bar Chart":    fig = px.bar(plot_data,  **kw, barmode="group")
        elif chart_type == "Line Chart": fig = px.line(plot_data, **kw, markers=True)
        elif chart_type == "Area Chart": fig = px.area(plot_data, **kw)

    elif chart_type == "Scatter Plot":
        s = size_col if size_col and size_col != "None" else None
        fig = px.scatter(df_plot, x=x_col, y=y_col, color=c_arg, size=s,
                         hover_data=all_cols[:5],
                         title=chart_title or f"{y_col} vs {x_col}",
                         template="plotly_dark", color_discrete_sequence=palette())

    elif chart_type == "Histogram":
        fig = px.histogram(df_plot, x=x_col, nbins=bins, marginal="box",
                           title=chart_title or f"Distribution — {x_col}",
                           template="plotly_dark", color_discrete_sequence=[chart_color])

    elif chart_type == "Box Plot":
        xa = x_col if x_col != "None" else None
        fig = px.box(df_plot, x=xa, y=y_col, color=c_arg if c_arg else xa,
                     points="outliers", title=chart_title or f"Box Plot — {y_col}",
                     template="plotly_dark", color_discrete_sequence=palette())

    elif chart_type == "Violin Plot":
        xa = x_col if x_col != "None" else None
        fig = px.violin(df_plot, x=xa, y=y_col, color=c_arg if c_arg else xa,
                        box=True, points="all",
                        title=chart_title or f"Violin — {y_col}",
                        template="plotly_dark", color_discrete_sequence=palette())

    elif chart_type == "Pie Chart":
        pie_d = df_plot.groupby(name_col)[val_col].sum().reset_index()
        fig = px.pie(pie_d, names=name_col, values=val_col,
                     title=chart_title or f"{val_col} by {name_col}",
                     template="plotly_dark", hole=0.38,
                     color_discrete_sequence=palette())

    elif chart_type == "Heatmap (Correlation)":
        if not selected_num or len(selected_num) < 2:
            st.warning("Select at least 2 numeric columns."); st.stop()
        corr = df[selected_num].corr().round(2)
        fig  = px.imshow(corr, text_auto=True, aspect="auto",
                         color_continuous_scale="RdBu_r",
                         title=chart_title or "Correlation Heatmap",
                         template="plotly_dark")

    elif chart_type == "Bubble Chart":
        fig = px.scatter(df_plot, x=x_col, y=y_col, size=size_col, color=c_arg,
                         title=chart_title or "Bubble Chart",
                         template="plotly_dark", size_max=55,
                         color_discrete_sequence=palette())

    if fig:
        apply_plotly_style(fig, height=500)
        if not show_grid: fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"📊 Showing first **{max_rows}** rows · Adjust using the Row Limit slider in the sidebar")
        st.download_button("⬇️  Download Chart (HTML)",
                           data=fig.to_html(),
                           file_name=f"{chart_type.replace(' ','_')}.html",
                           mime="text/html")

except Exception as e:
    st.error(f"❌ Chart error: {e}")
    st.info("Try different columns or chart type.")

# ── Column inspector ──────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Column Inspector</div>', unsafe_allow_html=True)

sel = st.selectbox("Pick a column", all_cols, label_visibility="collapsed")
col_data = df[sel]
c1,c2,c3,c4 = st.columns(4)
if pd.api.types.is_numeric_dtype(col_data):
    c1.metric("Mean",    f"{col_data.mean():.3f}")
    c2.metric("Median",  f"{col_data.median():.3f}")
    c3.metric("Std Dev", f"{col_data.std():.3f}")
    c4.metric("Nulls",   f"{col_data.isnull().sum()}")
else:
    c1.metric("Unique",      col_data.nunique())
    c2.metric("Most Common", col_data.mode()[0] if not col_data.mode().empty else "—")
    c3.metric("Nulls",       col_data.isnull().sum())
    c4.metric("Total",       len(col_data))
