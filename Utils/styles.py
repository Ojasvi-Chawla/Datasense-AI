# utils/styles.py
# Central place for all CSS — import this in every page

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Outfit:wght@300;400;600;700;800&display=swap');

/* ── Reset & Base ─────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Force sidebar always visible ────────────────── */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    min-width: 300px !important;
    max-width: 320px !important;
}
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}
section[data-testid="stSidebarContent"] {
    display: block !important;
    visibility: visible !important;
}

html, body, [data-testid="stAppViewContainer"] {
    background: #080810 !important;
    color: #e2e2f0 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Hide Streamlit chrome ────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ──────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0c0c1a !important;
    border-right: 1px solid rgba(0,245,160,0.08) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Mono', monospace !important; }

/* Sidebar nav items */
[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    margin: 2px 8px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(0,245,160,0.08) !important;
}

/* ── Main container ───────────────────────────────── */
.main .block-container {
    padding: 2rem 2.5rem 3rem !important;
    max-width: 1200px !important;
    animation: pageIn 0.35s ease;
}

@keyframes pageIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Typography ───────────────────────────────────── */
h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    background: linear-gradient(135deg, #00f5a0 0%, #00d4ff 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    line-height: 1.1 !important;
    margin-bottom: 0.25rem !important;
    letter-spacing: -0.5px !important;
}
h2 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    color: #e2e2f0 !important;
    font-size: 1.4rem !important;
}
h3 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: #00f5a0 !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.3px !important;
}

/* ── Divider ──────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,245,160,0.1) !important;
    margin: 1.5rem 0 !important;
}

/* ── Metric cards ─────────────────────────────────── */
[data-testid="stMetric"] {
    background: #111120 !important;
    border: 1px solid rgba(0,245,160,0.12) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    transition: border-color 0.2s, transform 0.2s !important;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,245,160,0.35) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    color: #6b6b8a !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.7rem !important;
    color: #00f5a0 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Buttons ──────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00f5a0, #00d4ff) !important;
    color: #080810 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0,245,160,0.25) !important;
    filter: brightness(1.05) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button style */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(0,245,160,0.3) !important;
    color: #00f5a0 !important;
}

/* ── Inputs / Selects ─────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #111120 !important;
    border: 1px solid rgba(0,245,160,0.15) !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    color: #e2e2f0 !important;
    transition: border-color 0.2s !important;
}
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: rgba(0,245,160,0.4) !important;
}
.stTextInput > div > div > input {
    background: #111120 !important;
    border: 1px solid rgba(0,245,160,0.15) !important;
    border-radius: 10px !important;
    color: #e2e2f0 !important;
    font-family: 'DM Mono', monospace !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00f5a0 !important;
    box-shadow: 0 0 0 2px rgba(0,245,160,0.15) !important;
}

/* ── Sliders ──────────────────────────────────────── */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: #00f5a0 !important;
    border-color: #00f5a0 !important;
}

/* ── Radio ────────────────────────────────────────── */
.stRadio label { font-family: 'DM Mono', monospace !important; font-size: 0.85rem !important; }

/* ── File uploader ────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #111120 !important;
    border: 2px dashed rgba(0,245,160,0.2) !important;
    border-radius: 16px !important;
    padding: 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,245,160,0.5) !important;
}

/* ── Tabs ─────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #111120 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(0,245,160,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    color: #6b6b8a !important;
    padding: 8px 18px !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,245,160,0.12) !important;
    color: #00f5a0 !important;
}

/* ── Expander ─────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #111120 !important;
    border: 1px solid rgba(0,245,160,0.1) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(0,245,160,0.3) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 14px 18px !important;
    color: #e2e2f0 !important;
}

/* ── Dataframe ────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,245,160,0.1) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Alerts ───────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left-width: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* ── Download button ──────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(0,245,160,0.3) !important;
    color: #00f5a0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0,245,160,0.08) !important;
    border-color: #00f5a0 !important;
    transform: translateY(-2px) !important;
}

/* ── Chat messages ────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: #111120 !important;
    border: 1px solid rgba(0,245,160,0.08) !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stChatInput"] textarea {
    background: #111120 !important;
    border: 1px solid rgba(0,245,160,0.2) !important;
    border-radius: 12px !important;
    color: #e2e2f0 !important;
    font-family: 'DM Mono', monospace !important;
}

/* ── Spinner ──────────────────────────────────────── */
.stSpinner > div { border-top-color: #00f5a0 !important; }

/* ── Scrollbar ────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080810; }
::-webkit-scrollbar-thumb { background: rgba(0,245,160,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,245,160,0.4); }

/* ── Custom component classes ─────────────────────── */

/* Page header bar */
.page-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 8px;
}
.page-icon {
    font-size: 2rem;
    background: rgba(0,245,160,0.08);
    border: 1px solid rgba(0,245,160,0.15);
    border-radius: 12px;
    width: 56px; height: 56px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}

/* Stat card (custom metric) */
.stat-card {
    background: #111120;
    border: 1px solid rgba(0,245,160,0.1);
    border-radius: 14px;
    padding: 20px 22px;
    transition: all 0.22s ease;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00f5a0, #00d4ff);
    border-radius: 14px 14px 0 0;
}
.stat-card:hover {
    border-color: rgba(0,245,160,0.3);
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
}
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #6b6b8a;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
}
.stat-value {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 1.9rem;
    color: #00f5a0;
    line-height: 1;
}
.stat-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #4a4a6a;
    margin-top: 4px;
}

/* Module card on home page */
.mod-card {
    background: #111120;
    border: 1px solid rgba(0,245,160,0.08);
    border-radius: 16px;
    padding: 26px 22px 20px;
    text-align: center;
    transition: all 0.25s ease;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.mod-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 0;
    background: linear-gradient(to top, rgba(0,245,160,0.05), transparent);
    transition: height 0.3s ease;
}
.mod-card:hover {
    border-color: rgba(0,245,160,0.35);
    transform: translateY(-5px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,245,160,0.1);
}
.mod-card:hover::after { height: 100%; }
.mod-icon {
    font-size: 2.2rem;
    margin-bottom: 14px;
    display: block;
    filter: drop-shadow(0 4px 12px rgba(0,245,160,0.3));
}
.mod-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: #e2e2f0;
    margin-bottom: 8px;
}
.mod-desc {
    font-family: 'DM Mono', monospace;
    font-size: 0.74rem;
    color: #5a5a7a;
    line-height: 1.6;
}

/* Tag/badge */
.tag {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(0,245,160,0.08);
    border: 1px solid rgba(0,245,160,0.2);
    color: #00f5a0;
    letter-spacing: 0.5px;
}

/* Section heading with accent line */
.section-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #00f5a0;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* Dashboard CTA */
.dash-cta {
    background: linear-gradient(135deg, #111120 0%, #0f1428 100%);
    border: 1px solid rgba(0,245,160,0.2);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-top: 24px;
}
.dash-cta::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,245,160,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.dash-cta::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,212,255,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.dash-cta h2 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.6rem !important;
    color: #e2e2f0 !important;
    margin-bottom: 10px !important;
}
.dash-cta p {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #6b6b8a;
    margin-bottom: 24px;
    line-height: 1.7;
}

/* Insight cards */
.insight-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 8px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-info    { background: rgba(0,212,255,0.1);  border: 1px solid rgba(0,212,255,0.25);  color: #00d4ff; }
.badge-warning { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #f59e0b; }
.badge-success { background: rgba(0,245,160,0.1);  border: 1px solid rgba(0,245,160,0.25);  color: #00f5a0; }
.badge-danger  { background: rgba(239,68,68,0.1);  border: 1px solid rgba(239,68,68,0.25);  color: #ef4444; }

/* Sidebar dataset pill */
.ds-pill {
    background: rgba(0,245,160,0.06);
    border: 1px solid rgba(0,245,160,0.15);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 8px 0;
}
.ds-pill-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #00f5a0;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.ds-pill-name {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: #e2e2f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.ds-pill-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #4a4a6a;
    margin-top: 2px;
}
</style>
"""

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#080810",
    plot_bgcolor="#0d0d1a",
    font=dict(family="DM Mono, monospace", color="#e2e2f0", size=11),
    title_font=dict(family="Outfit, sans-serif", size=15, color="#e2e2f0"),
    height=420,
    margin=dict(t=50, b=40, l=40, r=20),
    xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(0,245,160,0.1)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(0,245,160,0.05)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,245,160,0.1)"),
    colorway=["#00f5a0","#00d4ff","#7c3aed","#f59e0b","#ef4444","#10b981","#8b5cf6","#f97316"],
)

def apply_plotly_style(fig, height=420):
    """Apply consistent dark style to any plotly figure."""
    layout = dict(PLOTLY_LAYOUT)
    layout["height"] = height
    fig.update_layout(**layout)
    return fig

def inject_css():
    """Call this at top of every page."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def sidebar_dataset_info():
    """Show dataset info pill in sidebar."""
    import streamlit as st
    with st.sidebar:
        if "df" in st.session_state and st.session_state["df"] is not None:
            df = st.session_state["df"]
            st.markdown(f"""
            <div class="ds-pill">
                <div class="ds-pill-title">📦 Active Dataset</div>
                <div class="ds-pill-name">{st.session_state.get('filename','dataset')}</div>
                <div class="ds-pill-meta">{df.shape[0]:,} rows · {df.shape[1]} cols · {df.isnull().sum().sum()} nulls</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ds-pill" style="border-color:rgba(245,158,11,0.2); background:rgba(245,158,11,0.04);">
                <div class="ds-pill-title" style="color:#f59e0b;">⚠ No Dataset</div>
                <div class="ds-pill-meta">Go to Upload page first</div>
            </div>
            """, unsafe_allow_html=True)

def stat_card(label, value, sub=""):
    """Return HTML for a custom stat card."""
    return f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
        {"<div class='stat-sub'>"+sub+"</div>" if sub else ""}
    </div>
    """

def page_header(icon, title, subtitle=""):
    """Render a styled page header."""
    import streamlit as st
    st.markdown(f"""
    <div class="page-header">
        <div class="page-icon">{icon}</div>
        <div>
            <h1 style="margin:0 !important;">{title}</h1>
            {"<p style='color:#6b6b8a; font-family:DM Mono,monospace; font-size:0.82rem; margin:2px 0 0;'>"+subtitle+"</p>" if subtitle else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    def get_theme():
     return {
        "accent":  "#00f5a0",
        "accent2": "#00d4ff",
        "bg":      "#080810",
        "bg2":     "#111120",
        "text":    "#e2e2f0",
        "muted":   "#6b6b8a",
        "card_border":       "rgba(0,245,160,0.12)",
        "card_border_hover": "rgba(0,245,160,0.35)",
        "plotly_bg":   "#080810",
        "plotly_plot": "#0d0d1a",
        "colorway": ["#00f5a0","#00d4ff","#7c3aed","#f59e0b","#ef4444","#10b981"],
    }
