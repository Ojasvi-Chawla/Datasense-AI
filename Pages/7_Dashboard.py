import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header, stat_card, apply_plotly_style

st.set_page_config(page_title="Dashboard · DataSense", page_icon="🖥️", layout="wide")
inject_css()

# Subtle chart label CSS
st.markdown("""
<style>
.chart-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: rgba(100,100,130,0.5);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
</style>
""", unsafe_allow_html=True)

sidebar_dataset_info()

page_header("🖥️", "Auto Dashboard", "One-click full analytics report of your dataset")
st.markdown('<hr>', unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No data loaded. Go to **Upload** first."); st.stop()

df       = st.session_state["df"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()
filename = st.session_state.get("filename","dataset")

c = st.columns([1,2,1])
with c[1]:
    if st.button("🚀  Generate Full Dashboard", type="primary", use_container_width=True):
        st.session_state["dashboard_generated"] = True

if not st.session_state.get("dashboard_generated"):
    st.info("👆 Click **Generate Dashboard** above to create your analytics report.")
    st.stop()

st.markdown(f'<div class="section-title">Dashboard · {filename}</div>', unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<h2 style="color:#e2e2f0 !important; margin:12px 0 16px;">📌 Key Metrics</h2>', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col,(lbl,val,sub) in zip([c1,c2,c3,c4,c5],[
    ("Total Rows",     f"{df.shape[0]:,}",             "records"),
    ("Columns",        f"{df.shape[1]}",               "features"),
    ("Missing Values", f"{df.isnull().sum().sum():,}",  f"{df.isnull().sum().sum()/df.size*100:.1f}% of cells"),
    ("Duplicates",     f"{df.duplicated().sum()}",     "exact matches"),
    ("Numeric Cols",   f"{len(num_cols)}",             f"{len(cat_cols)} categorical"),
]):
    col.markdown(stat_card(lbl,val,sub), unsafe_allow_html=True)

if num_cols:
    st.markdown('<br>', unsafe_allow_html=True)
    extra = st.columns(min(4, len(num_cols)))
    for i,col in enumerate(num_cols[:4]):
        extra[i].markdown(stat_card(f"Avg {col}", f"{df[col].mean():.2f}", f"max: {df[col].max():.2f}"), unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)

# ── Row 1: Distribution + Heatmap ─────────────────────────────────────────────
r1a, r1b = st.columns(2)

with r1a:
    if num_cols:
        st.markdown('<div class="chart-label">Histogram + Box</div>', unsafe_allow_html=True)
        fig = px.histogram(df, x=num_cols[0], nbins=30, marginal="box",
                           title=f"Distribution — {num_cols[0]}",
                           template="plotly_dark", color_discrete_sequence=["#00f5a0"])
        apply_plotly_style(fig); st.plotly_chart(fig, use_container_width=True)

with r1b:
    if len(num_cols) >= 2:
        st.markdown('<div class="chart-label">Correlation Heatmap</div>', unsafe_allow_html=True)
        corr = df[num_cols].corr().round(2)
        fig2 = px.imshow(corr, text_auto=True, aspect="auto",
                         color_continuous_scale="RdBu_r",
                         title="Correlation Heatmap", template="plotly_dark")
        apply_plotly_style(fig2); st.plotly_chart(fig2, use_container_width=True)

st.markdown('<hr>', unsafe_allow_html=True)

# ── Row 2: Categorical ─────────────────────────────────────────────────────────
if cat_cols:
    r2 = st.columns(min(3, len(cat_cols)))
    for i,col in enumerate(cat_cols[:3]):
        with r2[i]:
            st.markdown('<div class="chart-label">Bar Chart</div>', unsafe_allow_html=True)
            top = df[col].value_counts().head(8).reset_index()
            top.columns = [col,"Count"]
            fig = px.bar(top, x=col, y="Count", title=f"'{col}' — Top Values",
                         template="plotly_dark", color_discrete_sequence=["#7c3aed"])
            apply_plotly_style(fig, height=320)
            fig.update_layout(margin=dict(t=50,b=50))
            st.plotly_chart(fig, use_container_width=True)
    st.markdown('<hr>', unsafe_allow_html=True)

# ── Row 3: Scatter + Box ───────────────────────────────────────────────────────
if len(num_cols) >= 2:
    r3a, r3b = st.columns(2)
    with r3a:
        st.markdown('<div class="chart-label">Scatter Plot</div>', unsafe_allow_html=True)
        fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                         color=cat_cols[0] if cat_cols else None,
                         title=f"{num_cols[0]} vs {num_cols[1]}",
                         template="plotly_dark", opacity=0.7,
                         color_discrete_sequence=px.colors.qualitative.Vivid)
        apply_plotly_style(fig); st.plotly_chart(fig, use_container_width=True)

    with r3b:
        st.markdown('<div class="chart-label">Box Plot</div>', unsafe_allow_html=True)
        fig = px.box(df, x=cat_cols[0] if cat_cols else None, y=num_cols[0],
                     points="outliers", title=f"Box Plot — {num_cols[0]}",
                     template="plotly_dark", color_discrete_sequence=["#f59e0b"])
        apply_plotly_style(fig); st.plotly_chart(fig, use_container_width=True)
    st.markdown('<hr>', unsafe_allow_html=True)

# ── Missing values ────────────────────────────────────────────────────────────
miss = df.isnull().sum().reset_index()
miss.columns = ["Column","Missing"]
miss = miss[miss["Missing"] > 0]
if miss.empty:
    st.success("✅ No missing values in your dataset!")
else:
    st.markdown('<div class="chart-label">Bar Chart · Missing Values</div>', unsafe_allow_html=True)
    fig = px.bar(miss, x="Column", y="Missing", title="Missing Values per Column",
                 template="plotly_dark", color="Missing", color_continuous_scale="Reds")
    apply_plotly_style(fig, height=300); st.plotly_chart(fig, use_container_width=True)

# ── Sample ────────────────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<h2 style="color:#e2e2f0 !important; margin-bottom:12px;">📄 Data Sample</h2>', unsafe_allow_html=True)
st.dataframe(df.head(10), use_container_width=True)

# ── Exports ───────────────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)

exp1, exp2, exp3 = st.columns(3)

with exp1:
    st.markdown("""<div class="stat-card"><div class="stat-label">CSV Export</div>
    <div class="stat-value" style="font-size:1rem; margin:8px 0;">📄 Standard Format</div>
    <div class="stat-sub">Works in Excel, Python, R, Tableau, Power BI</div></div>""", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.download_button("⬇️  Download CSV",
                       data=df.to_csv(index=False).encode("utf-8"),
                       file_name=f"{filename}_clean.csv", mime="text/csv",
                       use_container_width=True)

with exp2:
    st.markdown("""<div class="stat-card"><div class="stat-label">Excel Export</div>
    <div class="stat-value" style="font-size:1rem; margin:8px 0;">📊 Multi-Sheet</div>
    <div class="stat-sub">Data + Statistics sheets included</div></div>""", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Data")
        if num_cols: df.describe().to_excel(w, sheet_name="Statistics")
    st.download_button("⬇️  Download Excel (.xlsx)", data=buf.getvalue(),
                       file_name=f"{filename}_export.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

with exp3:
    st.markdown("""<div class="stat-card"><div class="stat-label">Power BI & Tableau</div>
    <div class="stat-value" style="font-size:1rem; margin:8px 0;">📈 BI Tools</div>
    <div class="stat-sub">Import the CSV into either tool</div></div>""", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    with st.expander("ℹ️  How to import"):
        st.markdown("""
**Power BI Desktop (free):**
Download CSV → `Get Data → Text/CSV` → Import → Build visuals

**Tableau Public (free):**
Download CSV → `Connect → Text File` → Import → Build dashboard

*`.pbix` / `.twbx` files cannot be generated by Python as they are proprietary formats.*
        """)

st.markdown('<hr>', unsafe_allow_html=True)
st.success("✅ Dashboard ready!")
