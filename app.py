import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import inject_css, sidebar_dataset_info, page_header

st.set_page_config(
    page_title="DataSense AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
sidebar_dataset_info()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 0.5rem;">
    <span class="tag">Data Analysis Platform</span>
</div>
""", unsafe_allow_html=True)

page_header("📊", "DataSense AI", "Automated Data Analysis & Visualization Platform")

st.markdown("""
<p style="color:#6b6b8a; font-family:'DM Mono',monospace; font-size:0.82rem; margin: 0 0 2rem; line-height:1.8;">
Upload any dataset · Auto-clean · Visualize · Get AI insights · Ask questions in plain English
</p>
""", unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)

# ── Module grid ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Modules</div>', unsafe_allow_html=True)
st.markdown('<h2 style="color:#e2e2f0 !important; margin-top:4px; margin-bottom:20px;">What do you want to do?</h2>', unsafe_allow_html=True)

modules = [
    ("📁", "Upload & Preview",   "Upload CSV, Excel or JSON. Instant shape, types, stats & missing value overview.", "pages/1_Upload.py"),
    ("📊", "Visualize",          "10+ Plotly chart types. Color picker, themes, aggregations, live column inspector.", "pages/2_Visualize.py"),
    ("🧹", "Clean Data",         "Fill nulls with mean/median/KNN, remove duplicates, convert column types.", "pages/3_Clean.py"),
    ("🔎", "Outlier Detection",  "IQR, Z-Score & Isolation Forest. Visualize, remove, cap, or replace outliers.", "pages/4_Outliers.py"),
    ("🧠", "AI Insights",        "Auto-generated plain-English analysis: skewness, correlations, data quality.", "pages/5_Insights.py"),
    ("💬", "Data Chatbot",       "Ask natural language questions about your data and get instant answers.", "pages/6_Chatbot.py"),
]

r1 = st.columns(3)
r2 = st.columns(3)

for i, (icon, title, desc, path) in enumerate(modules):
    col = r1[i] if i < 3 else r2[i-3]
    with col:
        st.markdown(f"""
        <div class="mod-card">
            <span class="mod-icon">{icon}</span>
            <div class="mod-title">{title}</div>
            <div class="mod-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Open →", key=f"mod_{i}", use_container_width=True):
            st.switch_page(path)

# ── Dashboard CTA ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-cta">
    <h2>🖥️ Generate Full Dashboard</h2>
    <p>Skip straight to a complete analytics dashboard — KPIs, correlation heatmap,<br>
    distributions, relationships and export options. All in one click.</p>
</div>
""", unsafe_allow_html=True)

c = st.columns([1, 2, 1])
with c[1]:
    if st.button("🚀  Generate Dashboard Now", use_container_width=True):
        if "df" not in st.session_state or st.session_state["df"] is None:
            st.error("⚠️ Upload a dataset first!")
        else:
            st.session_state["dashboard_generated"] = True
            st.switch_page("pages/7_Dashboard.py")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown("""
<p style="text-align:center; font-family:'DM Mono',monospace; font-size:0.7rem; color:#2a2a4a; letter-spacing:1px;">
DATASENSE AI · PYTHON + STREAMLIT · 
</p>
""", unsafe_allow_html=True)
