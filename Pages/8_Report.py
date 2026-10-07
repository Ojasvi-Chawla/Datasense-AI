from utils.ai_handler import get_ai_response
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, base64, re
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.styles import inject_css, sidebar_dataset_info, page_header, stat_card, apply_plotly_style

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Report · DataSense", page_icon="📄", layout="wide")
inject_css()
sidebar_dataset_info()

# ══════════════════════════════════════════════════════════════════════════════
# GROQ AI HELPER  —  paste your Groq API key here
# Get free key at: https://console.groq.com
GROQ_API_KEY = ""   # ← PASTE YOUR KEY HERE
# ══════════════════════════════════════════════════════════════════════════════

page_header("📄", "Analytics Report", "Professional data analysis report with AI-generated insights")
st.markdown('<hr>', unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No dataset loaded. Go to **Upload** first.")
    st.stop()

df       = st.session_state["df"]
filename = st.session_state.get("filename", "dataset.csv").rsplit(".", 1)[0]
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()
all_cols = df.columns.tolist()

# ── Detect date columns ───────────────────────────────────────────────────────
date_cols = []
for col in df.columns:
    if df[col].dtype == "datetime64[ns]":
        date_cols.append(col)
    elif df[col].dtype == object and any(w in col.lower() for w in ["date","time","year","month","day"]):
        try:
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().sum() > len(df) * 0.5:
                date_cols.append(col)
        except:
            pass

# ── Pick important columns (exclude date, id-like) ────────────────────────────
def pick_important_cols(df, num_cols, cat_cols, n=4):
    """Score columns by variance / uniqueness to find most informative ones."""
    scores = {}
    for c in num_cols:
        if df[c].std() > 0 and df[c].nunique() > 3:
            scores[c] = df[c].std() / (df[c].abs().mean() + 1e-9)   # CV
    top_num = sorted(scores, key=scores.get, reverse=True)[:n]

    # Exclude likely ID / date columns from cat
    top_cat = [c for c in cat_cols
                if 2 < df[c].nunique() <= 30
                and not any(w in c.lower() for w in ["id","uuid","key","date","time","index"])
               ][:2]
    return top_num, top_cat

top_num, top_cat = pick_important_cols(df, num_cols, cat_cols)

# ── Dataset topic guesser ─────────────────────────────────────────────────────
def guess_topic():
    hints = (filename + " " + " ".join(all_cols)).lower()
    topics = {
        "Automotive":     ["mpg","cyl","hp","wt","gear","carb","engine","car","vehicle"],
        "Sales & Revenue":["sales","revenue","profit","price","discount","order","quantity","amount"],
        "Human Resources":["salary","employee","department","experience","hire","job","gender"],
        "Healthcare":     ["bmi","glucose","blood","diabetes","cholesterol","patient","hospital"],
        "Real Estate":    ["sqft","bedroom","bathroom","house","property","location","zip"],
        "E-Commerce":     ["product","category","rating","review","seller","shipping","cart"],
        "Finance":        ["open","close","high","low","volume","stock","return","dividend"],
        "Education":      ["marks","grade","score","student","subject","exam","gpa","attendance"],
        "Weather":        ["temperature","humidity","wind","rain","pressure","forecast"],
        "Titanic":        ["survived","pclass","ticket","fare","cabin","embarked"],
        "Iris / Biology": ["sepal","petal","species"],
    }
    for topic, kws in topics.items():
        if any(k in hints for k in kws):
            return topic
    return "General Dataset"

TOPIC = guess_topic()

# ── Groq AI summary ───────────────────────────────────────────────────────────
def groq_summary(prompt, max_tokens=400):
    if not GROQ_API_KEY:
        return None
    try:
        import requests
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": "llama3-70b-8192",
                  "messages": [{"role":"user","content": prompt}],
                  "max_tokens": max_tokens, "temperature": 0.4},
            timeout=15
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return None

# ── Auto-generate all text sections ──────────────────────────────────────────
@st.cache_data(show_spinner=False)
def generate_report_text(shape, topic, columns, missing, dupes, api_key):

    context = (f"Dataset: {topic}. Shape: {shape[0]} rows × {shape[1]} cols. "
               f"Columns: {', '.join(columns[:12])}. "
               f"Missing values: {missing}. Duplicate rows: {dupes}.")

    if api_key:
        exec_sum = groq_summary(
            f"{context}\n\nWrite a 3-sentence executive summary for a data analytics report. "
            "Be professional and concise. Mention what the dataset is about and its scale.")
        objectives = groq_summary(
            f"{context}\n\nList 4 clear analytical objectives for this dataset as bullet points. "
            "Start each with an action verb. Keep each under 15 words.")
        methodology = groq_summary(
            f"{context}\n\nDescribe the data analysis methodology in 3 sentences covering: "
            "data ingestion, cleaning steps, and analysis approach.")
        findings = groq_summary(
            f"{context}\n\nList 4 key analytical findings for this dataset as bullet points. "
            "Be specific and data-driven. Keep each under 20 words.")
        conclusions = groq_summary(
            f"{context}\n\nWrite a 2-sentence conclusion for a data analytics report on this dataset.")
        recommendations = groq_summary(
            f"{context}\n\nList 4 actionable business recommendations based on this dataset. "
            "Each should be practical and under 20 words.")
    else:
        exec_sum = None
        objectives = None
        methodology = None
        findings = None
        conclusions = None
        recommendations = None

    return exec_sum, objectives, methodology, findings, conclusions, recommendations

with st.spinner("🤖 Generating AI report content..."):
    ai_exec, ai_obj, ai_method, ai_findings, ai_concl, ai_recs = generate_report_text(
        df.shape, TOPIC, all_cols, int(df.isnull().sum().sum()),
        int(df.duplicated().sum()), GROQ_API_KEY
    )

# ── Fallback text generators ──────────────────────────────────────────────────
def fallback_exec():
    return (f"This report presents a comprehensive analysis of the **{TOPIC}** dataset "
            f"comprising **{df.shape[0]:,} records** across **{df.shape[1]} features**. "
            f"The dataset contains **{len(num_cols)} numeric** and **{len(cat_cols)} categorical** columns, "
            f"with **{df.isnull().sum().sum()} missing values** addressed during the cleaning phase. "
            f"Key patterns, correlations, and actionable insights are documented below.")

def fallback_objectives():
    return (f"- Explore the structure and quality of the {TOPIC} dataset\n"
            f"- Identify distributions and statistical properties of key features\n"
            f"- Detect correlations, outliers, and anomalies in the data\n"
            f"- Generate actionable recommendations for data-driven decision making")

def fallback_methodology():
    return (f"Data was ingested in CSV/Excel format and validated for structure integrity. "
            f"Automated cleaning was applied to handle {df.isnull().sum().sum()} missing values "
            f"and {df.duplicated().sum()} duplicate records. "
            f"Exploratory analysis, statistical summaries, and correlation analysis were performed "
            f"across all {df.shape[1]} features.")

def fallback_findings(top_num, top_cat):
    lines = []
    for c in top_num[:2]:
        lines.append(f"- **{c}**: Mean = {df[c].mean():.2f}, Std = {df[c].std():.2f}, skewness = {df[c].skew():.2f}")
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        us = corr.abs().unstack()
        us = us[us < 1.0].drop_duplicates().sort_values(ascending=False)
        if len(us):
            a, b = us.index[0]
            lines.append(f"- **{a}** and **{b}** show the strongest correlation (r = {corr.loc[a,b]:.3f})")
    lines.append(f"- Dataset completeness: **{(1 - df.isnull().sum().sum()/df.size)*100:.1f}%** of cells are populated")
    return "\n".join(lines)

def fallback_conclusions():
    return (f"The {TOPIC} dataset provides a solid foundation for data-driven analysis and modeling. "
            f"After cleaning and exploration, the data reveals meaningful patterns across key features "
            f"that can inform strategic decisions and future predictive modeling efforts.")

def fallback_recommendations():
    recs = [
        f"- Address remaining **{df.isnull().sum().sum()} missing values** before building predictive models",
        f"- Focus feature engineering on the top correlated columns identified in this report",
        f"- Apply dimensionality reduction (PCA) if building ML models with all {df.shape[1]} features",
        f"- Schedule periodic data refresh to maintain dataset timeliness and relevance",
    ]
    return "\n".join(recs)

# ── Power BI style chart theme ────────────────────────────────────────────────
PBI = dict(
    paper_bgcolor="#1e1e2e",
    plot_bgcolor="#1e1e2e",
    font=dict(family="Segoe UI, sans-serif", color="#c8c8d4", size=11),
    title_font=dict(family="Segoe UI, sans-serif", size=13, color="#ffffff"),
    margin=dict(t=48, b=36, l=48, r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#888899")),
    xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.06)",
               tickfont=dict(size=10, color="#888899")),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
               zeroline=False, tickfont=dict(size=10, color="#888899")),
)
PBI_COLORS = ["#e03e3e","#3a86ff","#8ecae6","#06d6a0","#ffb703","#fb5607","#a8dadc","#e9c46a"]

def pbi_fig(fig, height=320):
    fig.update_layout(**PBI, height=height)
    return fig

# ── Build 4-5 smart charts ────────────────────────────────────────────────────
def build_report_charts():
    charts = []

    # Chart 1: Distribution of most important numeric col (histogram + KDE line)
    if top_num:
        col = top_num[0]
        vals = df[col].dropna()
        hist_data = np.histogram(vals, bins=25)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hist_data[1][:-1], y=hist_data[0],
            marker_color="#e03e3e", opacity=0.85, name="Frequency",
            marker_line_width=0,
        ))
        # Smooth KDE line
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(vals)
        x_range = np.linspace(vals.min(), vals.max(), 200)
        scale = hist_data[0].max() / kde(x_range).max()
        fig.add_trace(go.Scatter(
            x=x_range, y=kde(x_range)*scale,
            mode="lines", line=dict(color="#3a86ff", width=2.5),
            name="Trend"
        ))
        fig.update_layout(title=f"Distribution — {col}", showlegend=True, **PBI, height=300)
        charts.append(("Distribution Analysis", fig,
                        f"The distribution of **{col}** shows a {'right' if vals.skew()>0.5 else 'left' if vals.skew()<-0.5 else 'near-normal'} skew "
                        f"(skewness = {vals.skew():.2f}). Mean: **{vals.mean():.2f}**, Median: **{vals.median():.2f}**."))

    # Chart 2: Correlation heatmap (top numeric cols)
    if len(top_num) >= 3:
        corr = df[top_num].corr().round(2)
        fig = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale=[[0,"#3a86ff"],[0.5,"#1e1e2e"],[1,"#e03e3e"]],
            zmid=0, text=corr.values,
            texttemplate="%{text}", textfont=dict(size=11, color="white"),
            showscale=True,
            colorbar=dict(tickfont=dict(color="#888899"), len=0.8)
        ))
        fig.update_layout(title="Feature Correlation Matrix", **PBI, height=300)
        fig.update_xaxes(side="bottom")
        # Find top pair
        us = corr.abs().unstack()
        us = us[us<1].drop_duplicates().sort_values(ascending=False)
        top_pair = f"**{us.index[0][0]}** ↔ **{us.index[0][1]}** (r={corr.loc[us.index[0][0], us.index[0][1]]:.2f})" if len(us) else "N/A"
        charts.append(("Correlation Matrix", fig,
                        f"Strongest relationship: {top_pair}. "
                        f"High correlation indicates potential multicollinearity to address before modeling."))

    # Chart 3: Category breakdown (stacked horizontal bar — Power BI style)
    if top_cat and top_num:
        cat_col = top_cat[0]
        num_col = top_num[0]
        grp = df.groupby(cat_col)[num_col].agg(["mean","sum","count"]).reset_index()
        grp = grp.sort_values("mean", ascending=True).tail(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=grp[cat_col].astype(str), x=grp["mean"],
            orientation="h",
            marker=dict(color=PBI_COLORS[0], opacity=0.9),
            name=f"Mean {num_col}", text=grp["mean"].round(1),
            textposition="outside", textfont=dict(color="#c8c8d4", size=10),
        ))
        fig.update_layout(title=f"{num_col} by {cat_col}", **PBI, height=320)
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        fig.update_yaxes(showgrid=False)
        
        top_cat_val = grp.iloc[-1][cat_col]
        charts.append(("Category Breakdown", fig,
                        f"**{top_cat_val}** leads with the highest average {num_col}. "
                        f"Category analysis reveals significant variation across {df[cat_col].nunique()} groups."))

    # Chart 4: Top 2 numeric cols scatter (with regression line)
    if len(top_num) >= 2:
        x_c, y_c = top_num[0], top_num[1]
        sample = df[[x_c, y_c]].dropna().sample(min(300, len(df)), random_state=42)
        # regression
        z = np.polyfit(sample[x_c], sample[y_c], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sample[x_c].min(), sample[x_c].max(), 100)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample[x_c], y=sample[y_c],
            mode="markers",
            marker=dict(color="#3a86ff", size=5, opacity=0.6),
            name="Data Points"
        ))
        fig.add_trace(go.Scatter(
            x=x_line, y=p(x_line),
            mode="lines", line=dict(color="#e03e3e", width=2.5, dash="dash"),
            name="Trend Line"
        ))
        r = np.corrcoef(sample[x_c], sample[y_c])[0,1]
        fig.update_layout(title=f"{x_c} vs {y_c}  (r = {r:.3f})", **PBI, height=300)
        charts.append(("Relationship Analysis", fig,
                        f"**{x_c}** and **{y_c}** have a {'strong' if abs(r)>0.7 else 'moderate' if abs(r)>0.4 else 'weak'} "
                        f"{'positive' if r>0 else 'negative'} relationship (r = {r:.3f}). "
                        f"The trend line shows the direction of linear dependency."))

    # Chart 5: Time series if date exists, else top cat pie
    if date_cols and top_num:
        try:
            ts = df.copy()
            ts[date_cols[0]] = pd.to_datetime(ts[date_cols[0]], errors="coerce")
            ts = ts.dropna(subset=[date_cols[0], top_num[0]])
            ts = ts.sort_values(date_cols[0])
            ts_g = ts.set_index(date_cols[0])[top_num[0]].resample("M").mean().reset_index()
            if len(ts_g) >= 3:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=ts_g[date_cols[0]], y=ts_g[top_num[0]],
                    mode="lines+markers",
                    line=dict(color="#e03e3e", width=2.5),
                    marker=dict(size=5, color="#e03e3e"),
                    fill="tozeroy",
                    fillcolor="rgba(224,62,62,0.08)",
                    name=top_num[0]
                ))
                fig.update_layout(title=f"{top_num[0]} Over Time", **PBI, height=300)
                charts.append(("Time Series Trend", fig,
                                f"Monthly trend of **{top_num[0]}** from {ts_g[date_cols[0]].min().strftime('%b %Y')} "
                                f"to {ts_g[date_cols[0]].max().strftime('%b %Y')}. "
                                f"Overall {'upward' if ts_g[top_num[0]].iloc[-1] > ts_g[top_num[0]].iloc[0] else 'downward'} trend observed."))
        except:
            pass

    if not date_cols and len(top_cat) >= 1 and top_num:
        cat_col = top_cat[0]
        vc = df[cat_col].value_counts().head(8)
        fig = go.Figure(go.Pie(
            labels=vc.index.astype(str), values=vc.values,
            hole=0.5,
            marker=dict(colors=PBI_COLORS, line=dict(color="#1e1e2e", width=2)),
            textfont=dict(size=11, color="white"),
            textinfo="percent+label",
        ))
        fig.update_layout(
            title=f"Composition — {cat_col}", **PBI, height=300,
            showlegend=False,
            annotations=[dict(text=cat_col, x=0.5, y=0.5, font_size=11,
                              showarrow=False, font_color="#888899")]
        )
        charts.append(("Composition Analysis", fig,
                        f"**{vc.index[0]}** is the dominant category ({vc.values[0]/vc.sum()*100:.1f}%) in **{cat_col}**. "
                        f"{df[cat_col].nunique()} distinct categories present."))

    return charts[:5]

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER REPORT
# ═══════════════════════════════════════════════════════════════════════════════

t = {"accent": "#00f5a0", "muted": "#6b6b8a"}

# ── Report header banner ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#1e1e2e 0%,#16213e 100%);
border:1px solid rgba(224,62,62,0.2); border-radius:20px; padding:40px 44px;
position:relative; overflow:hidden; margin-bottom:32px;">
    <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
    background:radial-gradient(circle,rgba(224,62,62,0.08) 0%,transparent 70%);"></div>
    <div style="position:absolute;bottom:-40px;left:-40px;width:180px;height:180px;
    background:radial-gradient(circle,rgba(58,134,255,0.06) 0%,transparent 70%);"></div>
    <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:20px;">
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#e03e3e;
            letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
                ◆ Analytics Report
            </div>
            <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:2rem;
            color:#ffffff;line-height:1.1;margin-bottom:6px;">
                {filename.replace('_',' ').title()}
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:0.78rem;color:#888899;">
                {TOPIC} &nbsp;·&nbsp; {df.shape[0]:,} records &nbsp;·&nbsp; {df.shape[1]} features
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#888899;
            letter-spacing:1px;text-transform:uppercase;">Generated</div>
            <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:0.95rem;color:#c8c8d4;">
                {datetime.now().strftime("%d %b %Y, %H:%M")}
            </div>
            <div style="margin-top:10px;">
                <span style="background:rgba(224,62,62,0.12);border:1px solid rgba(224,62,62,0.3);
                border-radius:6px;padding:4px 12px;font-family:'DM Mono',monospace;
                font-size:0.68rem;color:#e03e3e;letter-spacing:1px;">CONFIDENTIAL</span>
            </div>
        </div>
    </div>
    <div style="display:flex;gap:32px;margin-top:28px;padding-top:24px;
    border-top:1px solid rgba(255,255,255,0.06);flex-wrap:wrap;">
        <div><div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#888899;
        letter-spacing:1px;text-transform:uppercase;">Total Records</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;color:#e03e3e;">
        {df.shape[0]:,}</div></div>
        <div><div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#888899;
        letter-spacing:1px;text-transform:uppercase;">Features</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;color:#3a86ff;">
        {df.shape[1]}</div></div>
        <div><div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#888899;
        letter-spacing:1px;text-transform:uppercase;">Completeness</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;color:#06d6a0;">
        {(1-df.isnull().sum().sum()/df.size)*100:.1f}%</div></div>
        <div><div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#888899;
        letter-spacing:1px;text-transform:uppercase;">Numeric Cols</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;color:#ffb703;">
        {len(num_cols)}</div></div>
        <div><div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#888899;
        letter-spacing:1px;text-transform:uppercase;">Category Cols</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;color:#e03e3e;">
        {len(cat_cols)}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Section renderer helper ───────────────────────────────────────────────────
def section(number, title, icon):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:32px 0 16px;">
        <div style="background:#e03e3e;color:white;font-family:'Outfit',sans-serif;
        font-weight:800;font-size:0.8rem;width:28px;height:28px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;flex-shrink:0;">{number}</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:1.15rem;color:#e2e2f0;">
        {icon} {title}</div>
        <div style="flex:1;height:1px;background:rgba(224,62,62,0.15);"></div>
    </div>
    """, unsafe_allow_html=True)

def text_card(content, accent="#e03e3e"):
    st.markdown(f"""
    <div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.06);
    border-left:3px solid {accent};border-radius:0 12px 12px 0;
    padding:20px 24px;font-family:'DM Mono',monospace;font-size:0.82rem;
    color:#c8c8d4;line-height:1.9;">
    {content.replace(chr(10),'<br>')}
    </div>
    """, unsafe_allow_html=True)

def bullet_card(content, accent="#3a86ff"):
    lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
    items_html = ""
    for l in lines:
        clean = l.lstrip("-•*").strip()
        items_html += f"""<div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;">
            <div style="width:6px;height:6px;border-radius:50%;background:{accent};
            margin-top:6px;flex-shrink:0;"></div>
            <div style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#c8c8d4;line-height:1.6;">
            {clean}</div></div>"""
    st.markdown(f"""
    <div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;padding:20px 24px;">{items_html}</div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — EXECUTIVE SUMMARY
section(1, "Executive Summary", "📌")
text_card(ai_exec if ai_exec else fallback_exec(), "#e03e3e")

if not GROQ_API_KEY:
    st.caption("💡 Add your Groq API key at the top of this file for AI-generated summaries.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — OBJECTIVES
section(2, "Objectives", "🎯")
bullet_card(ai_obj if ai_obj else fallback_objectives(), "#3a86ff")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — METHODOLOGY
section(3, "Methodology", "🔬")

m_cols = st.columns(3)
steps = [
    ("01", "Data Ingestion", f"Loaded **{filename}** ({df.shape[0]:,} rows × {df.shape[1]} cols). "
     f"Format validated, column types inferred.", "#e03e3e"),
    ("02", "Data Cleaning", f"Addressed **{df.isnull().sum().sum()} missing values** and "
     f"**{df.duplicated().sum()} duplicates**. Types standardized.", "#3a86ff"),
    ("03", "Analysis", f"Statistical summaries, correlation analysis, outlier detection, "
     f"and visualization across all {df.shape[1]} features.", "#06d6a0"),
]
for col, (n, title, desc, color) in zip(m_cols, steps):
    col.markdown(f"""
    <div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.06);
    border-radius:14px;padding:20px 18px;height:100%;">
        <div style="font-family:'Outfit',sans-serif;font-weight:900;
        font-size:1.8rem;color:{color};opacity:0.3;line-height:1;">{n}</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;
        font-size:0.95rem;color:#ffffff;margin:8px 0 6px;">{title}</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.74rem;
        color:#888899;line-height:1.7;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

if ai_method:
    st.markdown('<br>', unsafe_allow_html=True)
    text_card(ai_method, "#06d6a0")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — DATA OVERVIEW (mini stats)
section(4, "Data Overview", "📊")

ov_cols = st.columns(4)
overview_items = []
for c in top_num[:4]:
    overview_items.append((c, f"{df[c].mean():.2f}", f"std: {df[c].std():.2f}"))
if len(overview_items) < 4 and top_cat:
    for c in top_cat:
        v = df[c].mode()[0] if not df[c].mode().empty else "—"
        overview_items.append((c, str(v), f"{df[c].nunique()} unique"))

for col, (label, val, sub) in zip(ov_cols, overview_items[:4]):
    col.markdown(f"""
    <div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.06);
    border-top:3px solid #e03e3e;border-radius:0 0 12px 12px;
    padding:18px 16px;transition:all 0.2s;">
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#888899;
        text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">{label}</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:800;
        font-size:1.6rem;color:#e03e3e;line-height:1;">{val}</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;
        color:#555566;margin-top:4px;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — VISUALIZATIONS
section(5, "Data Visualizations", "📈")

st.markdown("""
<p style="font-family:'DM Mono',monospace;font-size:0.78rem;color:#888899;
margin-bottom:20px;line-height:1.7;">
Charts are built on the most statistically significant features of the dataset.
Hover over any chart for detailed values.
</p>
""", unsafe_allow_html=True)

with st.spinner("Building charts..."):
    charts = build_report_charts()

# Layout: charts 1+2 side by side, then 3+4, then 5 full width
chart_store = {}  # save for PDF
for i in range(0, len(charts)-1, 2):
    c1, c2 = st.columns(2)
    for col, idx in [(c1, i), (c2, i+1)]:
        if idx < len(charts):
            title, fig, insight = charts[idx]
            chart_store[title] = fig
            with col:
                st.markdown(f'<div class="chart-label">{title}</div>', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown(f"""
                <div style="background:rgba(224,62,62,0.04);border-left:2px solid rgba(224,62,62,0.3);
                border-radius:0 8px 8px 0;padding:8px 14px;margin-bottom:12px;">
                    <span style="font-family:'DM Mono',monospace;font-size:0.74rem;color:#888899;">
                    💡 {insight}</span>
                </div>
                """, unsafe_allow_html=True)

# Last chart full width if odd count
if len(charts) % 2 == 1:
    title, fig, insight = charts[-1]
    chart_store[title] = fig
    st.markdown(f'<div class="chart-label">{title}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(f"""
    <div style="background:rgba(224,62,62,0.04);border-left:2px solid rgba(224,62,62,0.3);
    border-radius:0 8px 8px 0;padding:8px 14px;margin-bottom:12px;">
        <span style="font-family:'DM Mono',monospace;font-size:0.74rem;color:#888899;">
        💡 {insight}</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — KEY FINDINGS
section(6, "Key Findings", "🔍")
bullet_card(ai_findings if ai_findings else fallback_findings(top_num, top_cat), "#ffb703")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — STATISTICAL SNAPSHOT
section(7, "Statistical Snapshot", "🧮")

if num_cols:
    snap_df = df[top_num].describe().T.round(3)
    snap_df.index.name = "Column"
    snap_df = snap_df.reset_index()
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] {{border-radius:12px !important; overflow:hidden;}}
    </style>
    """, unsafe_allow_html=True)
    st.dataframe(snap_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — CONCLUSIONS
section(8, "Conclusions", "✅")
text_card(ai_concl if ai_concl else fallback_conclusions(), "#06d6a0")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — ACTIONABLE RECOMMENDATIONS
section(9, "Actionable Recommendations", "💡")

recs_text = ai_recs if ai_recs else fallback_recommendations()
rec_lines = [l.strip().lstrip("-•*").strip() for l in recs_text.strip().split("\n") if l.strip()]

rec_cols = st.columns(2)
rec_colors = ["#e03e3e","#3a86ff","#06d6a0","#ffb703"]
for i, rec in enumerate(rec_lines[:4]):
    col = rec_cols[i % 2]
    col.markdown(f"""
    <div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.06);
    border-radius:12px;padding:18px 20px;margin-bottom:12px;
    border-left:3px solid {rec_colors[i]};">
        <div style="display:flex;gap:10px;align-items:flex-start;">
            <div style="background:{rec_colors[i]};color:white;font-family:'Outfit',sans-serif;
            font-weight:800;font-size:0.72rem;width:22px;height:22px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">
            {i+1}</div>
            <div style="font-family:'DM Mono',monospace;font-size:0.78rem;
            color:#c8c8d4;line-height:1.7;">{rec}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — NEXT STEPS
section(10, "Suggested Next Steps", "🚀")

next_steps = [
    ("Clean & Enrich",  "🧹", "Handle remaining missing values and engineer new features from existing columns.", "#e03e3e"),
    ("Build ML Model",  "🤖", f"Train predictive models using the top correlated features: {', '.join(top_num[:3])}.", "#3a86ff"),
    ("Monitor KPIs",    "📊", "Set up automated dashboards to track key metrics over time.", "#06d6a0"),
    ("Share Insights",  "📤", "Export this report and share with stakeholders for data-driven decisions.", "#ffb703"),
]
ns_cols = st.columns(4)
for col, (title, icon, desc, color) in zip(ns_cols, next_steps):
    col.markdown(f"""
    <div style="background:#1e1e2e;border:1px solid rgba(255,255,255,0.06);
    border-radius:14px;padding:18px 16px;text-align:center;height:100%;">
        <div style="font-size:1.6rem;margin-bottom:10px;">{icon}</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;
        font-size:0.88rem;color:{color};margin-bottom:8px;">{title}</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;
        color:#888899;line-height:1.6;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 — DOWNLOAD PDF
st.markdown('<hr>', unsafe_allow_html=True)
section(11, "Export Report", "📥")

def generate_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, Image)
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        import plotly.io as pio
        import tempfile

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        W = A4[0] - 4*cm

        # ── Colors ────────────────────────────────────────────────────────
        C_RED    = colors.HexColor("#e03e3e")
        C_BLUE   = colors.HexColor("#3a86ff")
        C_GREEN  = colors.HexColor("#06d6a0")
        C_BLACK  = colors.HexColor("#111111")
        C_DARK   = colors.HexColor("#222222")
        C_GREY   = colors.HexColor("#555555")
        C_LGREY  = colors.HexColor("#f4f4f4")
        C_WHITE  = colors.white
        C_ACCENT = colors.HexColor("#e03e3e")

        # ── Styles — all text BLACK for readability ────────────────────────
        def S(name, **kw):
            return ParagraphStyle(name, **kw)

        S_COVER_TAG  = S("ctag",  fontName="Helvetica",      fontSize=8,  textColor=C_RED,   leading=12, spaceAfter=4)
        S_COVER_TITL = S("ctitl", fontName="Helvetica-Bold", fontSize=24, textColor=C_WHITE, leading=30, spaceAfter=6)
        S_COVER_META = S("cmeta", fontName="Helvetica",      fontSize=9,  textColor=colors.HexColor("#cccccc"), leading=13, spaceAfter=0)
        S_SECTION    = S("sec",   fontName="Helvetica-Bold", fontSize=12, textColor=C_BLACK, leading=16, spaceBefore=16, spaceAfter=6)
        S_BODY       = S("body",  fontName="Helvetica",      fontSize=9.5,textColor=C_BLACK, leading=15, spaceAfter=5)
        S_BULLET     = S("blt",   fontName="Helvetica",      fontSize=9.5,textColor=C_BLACK, leading=15, spaceAfter=4, leftIndent=16, bulletIndent=4)
        S_CAPTION    = S("cap",   fontName="Helvetica-Oblique", fontSize=8, textColor=C_GREY, leading=11, spaceAfter=10, alignment=TA_CENTER)
        S_FOOTER     = S("ftr",   fontName="Helvetica",      fontSize=7,  textColor=C_GREY,  leading=10, alignment=TA_CENTER)
        S_KPI_LBL    = S("klbl",  fontName="Helvetica",      fontSize=7,  textColor=colors.HexColor("#aaaaaa"), leading=10, alignment=TA_CENTER)
        S_KPI_VAL    = S("kval",  fontName="Helvetica-Bold", fontSize=20, textColor=C_RED,   leading=24, alignment=TA_CENTER)
        S_TH         = S("th",    fontName="Helvetica-Bold", fontSize=8,  textColor=C_WHITE, leading=11, alignment=TA_CENTER)
        S_TD         = S("td",    fontName="Helvetica",      fontSize=8,  textColor=C_BLACK, leading=11, alignment=TA_CENTER)

        story = []

        # ── Helper: clean markdown bold ───────────────────────────────────
        def clean(text):
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', str(text))
            text = text.replace("\n\n","<br/><br/>").replace("\n","<br/>")
            return text

        def body(text):
            story.append(Paragraph(clean(text), S_BODY))
            story.append(Spacer(1, 3))

        def bullets(text):
            lines = [l.strip().lstrip("-•*").strip() for l in text.strip().split("\n") if l.strip()]
            for l in lines:
                story.append(Paragraph(f"• {clean(l)}", S_BULLET))

        def sec_heading(num, title):
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width=W, thickness=0.6, color=colors.HexColor("#dddddd"), spaceAfter=6))
            row = [[
                Paragraph(f'<font color="#e03e3e"><b>{num}</b></font>', S_SECTION),
                Paragraph(f"  {title}", S_SECTION),
            ]]
            t = Table(row, colWidths=[22, W-22])
            t.setStyle(TableStyle([
                ("LEFTPADDING",  (0,0),(-1,-1), 0),
                ("TOPPADDING",   (0,0),(-1,-1), 0),
                ("BOTTOMPADDING",(0,0),(-1,-1), 0),
                ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))

        # ══════════════════════════════════════════════════════════════════
        # COVER BLOCK (dark background)
        # ══════════════════════════════════════════════════════════════════
        cover_rows = [
            [Paragraph("◆  ANALYTICS REPORT", S_COVER_TAG)],
            [Paragraph(filename.replace("_"," ").title(), S_COVER_TITL)],
            [Paragraph(f"{TOPIC}  ·  {df.shape[0]:,} records  ·  {df.shape[1]} features  ·  {datetime.now().strftime('%d %b %Y')}", S_COVER_META)],
        ]
        cover_tbl = Table(cover_rows, colWidths=[W])
        cover_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#1e1e2e")),
            ("TOPPADDING",   (0,0),(-1,-1), 14),
            ("BOTTOMPADDING",(0,0),(-1,-1), 14),
            ("LEFTPADDING",  (0,0),(-1,-1), 22),
            ("RIGHTPADDING", (0,0),(-1,-1), 22),
        ]))
        story.append(cover_tbl)
        story.append(Spacer(1, 14))

        # ── KPI row ────────────────────────────────────────────────────────
        kpi_items = [
            ("Records",       f"{df.shape[0]:,}"),
            ("Features",      str(df.shape[1])),
            ("Completeness",  f"{(1-df.isnull().sum().sum()/df.size)*100:.1f}%"),
            ("Missing Values",str(df.isnull().sum().sum())),
        ]
        kpi_labels = [Paragraph(lbl, S_KPI_LBL) for lbl,_ in kpi_items]
        kpi_values = [Paragraph(val, S_KPI_VAL) for _,val in kpi_items]
        kpi_tbl = Table([kpi_labels, kpi_values], colWidths=[W/4]*4, rowHeights=[14, 28])
        kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#f9f9f9")),
            ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("LINEBEFORE",    (1,0),(3,-1),  0.5, colors.HexColor("#eeeeee")),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ]))
        story.append(kpi_tbl)

        # ══════════════════════════════════════════════════════════════════
        # SECTIONS
        # ══════════════════════════════════════════════════════════════════

        sec_heading("01", "Executive Summary")
        body(ai_exec if ai_exec else fallback_exec())

        sec_heading("02", "Objectives")
        bullets(ai_obj if ai_obj else fallback_objectives())

        sec_heading("03", "Methodology")
        body(ai_method if ai_method else fallback_methodology())

        # ── Statistical Snapshot table ─────────────────────────────────────
        sec_heading("04", "Statistical Snapshot")
        if top_num:
            snap = df[top_num].describe().T.round(3).reset_index()
            snap.columns = [str(c) for c in snap.columns]
            header = [Paragraph(c, S_TH) for c in snap.columns]
            rows   = [header]
            for _, row in snap.iterrows():
                rows.append([Paragraph(str(v), S_TD) for v in row])
            col_w = [W / len(snap.columns)] * len(snap.columns)
            stbl  = Table(rows, colWidths=col_w)
            stbl.setStyle(TableStyle([
                ("BACKGROUND",     (0,0),(-1,0),  colors.HexColor("#e03e3e")),
                ("BACKGROUND",     (0,1),(-1,-1), C_WHITE),
                ("ROWBACKGROUNDS", (0,1),(-1,-1), [C_WHITE, C_LGREY]),
                ("GRID",           (0,0),(-1,-1), 0.4, colors.HexColor("#dddddd")),
                ("TOPPADDING",     (0,0),(-1,-1), 5),
                ("BOTTOMPADDING",  (0,0),(-1,-1), 5),
                ("ALIGN",          (0,0),(-1,-1), "CENTER"),
            ]))
            story.append(stbl)

        # ══════════════════════════════════════════════════════════════════
        # VISUALIZATIONS — export each chart as PNG image
        # ══════════════════════════════════════════════════════════════════
        sec_heading("05", "Data Visualizations")
        story.append(Paragraph(
            "Charts are generated on the most statistically significant features of the dataset.",
            S_BODY))
        story.append(Spacer(1, 8))

        chart_imgs = []
        for chart_title_str, fig, insight in charts:
            try:
                # Make chart white-background for PDF
                fig_pdf = go.Figure(fig)
                fig_pdf.update_layout(
                    paper_bgcolor="white",
                    plot_bgcolor="#f8f8f8",
                    font=dict(color="#111111", size=10),
                    title_font=dict(color="#111111", size=12),
                    height=300,
                    margin=dict(t=44, b=32, l=40, r=20),
                )
                fig_pdf.update_xaxes(tickfont=dict(color="#333333"), title_font=dict(color="#333333"), gridcolor="#eeeeee")
                fig_pdf.update_yaxes(tickfont=dict(color="#333333"), title_font=dict(color="#333333"), gridcolor="#eeeeee")
                # Update trace colors for light background
                for trace in fig_pdf.data:
                    if hasattr(trace, 'marker') and hasattr(trace.marker, 'colorscale'):
                        pass  # keep heatmap colorscale
                    if hasattr(trace, 'line') and trace.line.color in [None, "#e03e3e", "#3a86ff"]:
                        pass  # keep accent colors — they look fine on white

                img_bytes = pio.to_image(fig_pdf, format="png", width=680, height=300, scale=1.8)
                chart_imgs.append((chart_title_str, img_bytes, insight))
            except Exception as e:
                chart_imgs.append((chart_title_str, None, insight))

        # Render charts 2-per-row
        half = W / 2 - 4
        i = 0
        while i < len(chart_imgs):
            row_cells = []
            for j in range(2):
                if i + j < len(chart_imgs):
                    ctitle, img_bytes, insight = chart_imgs[i+j]
                    cell_content = [Paragraph(f"<b>{ctitle}</b>", S_BODY)]
                    if img_bytes:
                        img_buf = io.BytesIO(img_bytes)
                        img_obj = Image(img_buf, width=half, height=half*0.46)
                        cell_content.append(img_obj)
                    else:
                        cell_content.append(Paragraph("[Chart could not be rendered — install kaleido: pip install kaleido]", S_CAPTION))
                    cell_content.append(Paragraph(f"<i>{clean(insight)}</i>", S_CAPTION))
                    row_cells.append(cell_content)
                else:
                    row_cells.append([Paragraph("", S_BODY)])

            chart_row = Table([row_cells], colWidths=[half+4, half+4])
            chart_row.setStyle(TableStyle([
                ("VALIGN",        (0,0),(-1,-1), "TOP"),
                ("LEFTPADDING",   (0,0),(-1,-1), 4),
                ("RIGHTPADDING",  (0,0),(-1,-1), 4),
                ("TOPPADDING",    (0,0),(-1,-1), 0),
                ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ]))
            story.append(chart_row)
            i += 2

        # If kaleido not installed show notice
        if all(img is None for _, img, _ in chart_imgs):
            story.append(Paragraph(
                "⚠ Chart images require kaleido. Run: pip install kaleido",
                S_CAPTION))

        # ══════════════════════════════════════════════════════════════════
        sec_heading("06", "Key Findings")
        bullets(ai_findings if ai_findings else fallback_findings(top_num, top_cat))

        sec_heading("07", "Conclusions")
        body(ai_concl if ai_concl else fallback_conclusions())

        sec_heading("08", "Actionable Recommendations")
        recs_t = ai_recs if ai_recs else fallback_recommendations()
        rec_lines = [l.strip().lstrip("-•*").strip() for l in recs_t.strip().split("\n") if l.strip()]
        rec_rows = []
        for idx, rec in enumerate(rec_lines[:4]):
            rec_rows.append([
                Paragraph(f"<b><font color='#e03e3e'>{idx+1}</font></b>", S_BODY),
                Paragraph(clean(rec), S_BODY),
            ])
        if rec_rows:
            rec_tbl = Table(rec_rows, colWidths=[18, W-18])
            rec_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), C_LGREY),
                ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_WHITE, C_LGREY]),
                ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#dddddd")),
                ("TOPPADDING",    (0,0),(-1,-1), 7),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
                ("LEFTPADDING",   (0,0),(-1,-1), 8),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ]))
            story.append(rec_tbl)

        sec_heading("09", "Suggested Next Steps")
        next_data = [
            ["Clean & Enrich",  "Handle missing values and engineer new features"],
            ["Build ML Model",  f"Train on top features: {', '.join(top_num[:3])}"],
            ["Monitor KPIs",    "Set up automated dashboards for key metrics"],
            ["Share Insights",  "Distribute report to stakeholders for decisions"],
        ]
        ns_tbl = Table(next_data, colWidths=[W*0.28, W*0.72])
        ns_tbl.setStyle(TableStyle([
            ("FONTNAME",      (0,0),(0,-1),  "Helvetica-Bold"),
            ("FONTNAME",      (1,0),(1,-1),  "Helvetica"),
            ("FONTSIZE",      (0,0),(-1,-1), 9),
            ("TEXTCOLOR",     (0,0),(0,-1),  C_RED),
            ("TEXTCOLOR",     (1,0),(1,-1),  C_BLACK),
            ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_WHITE, C_LGREY]),
            ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#dddddd")),
            ("TOPPADDING",    (0,0),(-1,-1), 7),
            ("BOTTOMPADDING", (0,0),(-1,-1), 7),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ]))
        story.append(ns_tbl)

        # ── Footer ─────────────────────────────────────────────────────────
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#cccccc")))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Generated by DataSense AI  ·  {datetime.now().strftime('%d %B %Y, %H:%M')}  ·  CONFIDENTIAL",
            S_FOOTER))

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    except ImportError as e:
        st.error(f"Missing library: {e}. Run: pip install reportlab")
        return None
    except Exception as e:
        st.error(f"PDF error: {e}")
        return None

        # ── Styles ──────────────────────────────────────────────────────────
        styles = getSampleStyleSheet()  # noqa: F821

        def style(name, **kw):
            return ParagraphStyle(name, **kw)

        S_TITLE   = style("title",   fontName="Helvetica-Bold",   fontSize=22, textColor=C_WHITE,   spaceAfter=4,  leading=28)
        S_SUB     = style("sub",     fontName="Helvetica",         fontSize=10, textColor=C_GREY,    spaceAfter=16, leading=14)
        S_SEC     = style("sec",     fontName="Helvetica-Bold",    fontSize=13, textColor=C_WHITE,   spaceBefore=18,spaceAfter=8, leading=18)
        S_BODY    = style("body",    fontName="Helvetica",         fontSize=9,  textColor=C_LIGHT,   spaceAfter=6,  leading=14)  # noqa: F821
        S_BULLET  = style("bullet",  fontName="Helvetica",         fontSize=9,  textColor=C_LIGHT,   spaceAfter=4,  leading=14,  # noqa: F821
                          leftIndent=14, bulletIndent=4)
        S_CAPTION = style("caption", fontName="Helvetica-Oblique", fontSize=8,  textColor=C_GREY,    spaceAfter=8,  leading=12)
        S_KPI_LBL = style("kpilbl",  fontName="Helvetica",         fontSize=7,  textColor=C_GREY,    leading=10,    spaceAfter=2, alignment=TA_CENTER)
        S_KPI_VAL = style("kpival",  fontName="Helvetica-Bold",    fontSize=18, textColor=C_RED,     leading=22,    spaceAfter=0, alignment=TA_CENTER)

        story = []
        W = A4[0] - 4*cm   # usable width

        # ── Cover block ─────────────────────────────────────────────────────
        cover_data = [[
            Paragraph(f"<font color='#e03e3e'>◆ Analytics Report</font>", S_CAPTION),
        ]]
        cover_tbl = Table(cover_data, colWidths=[W])
        cover_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0),(-1,-1), C_DARK),
            ("ROWPADDING",  (0,0),(-1,-1), 6),
            ("TOPPADDING",  (0,0),(-1,-1), 20),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("LEFTPADDING", (0,0),(-1,-1), 20),
        ]))
        story.append(cover_tbl)

        title_data = [[Paragraph(filename.replace("_"," ").title(), S_TITLE)]]
        title_tbl  = Table(title_data, colWidths=[W])
        title_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), C_DARK),
            ("LEFTPADDING",  (0,0),(-1,-1), 20),
            ("RIGHTPADDING", (0,0),(-1,-1), 20),
            ("TOPPADDING",   (0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]))
        story.append(title_tbl)

        meta_data = [[Paragraph(f"{TOPIC}  ·  {df.shape[0]:,} records  ·  {df.shape[1]} features  ·  {datetime.now().strftime('%d %b %Y')}", S_SUB)]]
        meta_tbl  = Table(meta_data, colWidths=[W])
        meta_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), C_DARK),
            ("LEFTPADDING",  (0,0),(-1,-1), 20),
            ("RIGHTPADDING", (0,0),(-1,-1), 20),
            ("TOPPADDING",   (0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 20),
        ]))
        story.append(meta_tbl)

        # KPI row ─────────────────────────────────────────────────────────
        kpi_items = [
            ("Records",      f"{df.shape[0]:,}"),
            ("Features",     str(df.shape[1])),
            ("Completeness", f"{(1-df.isnull().sum().sum()/df.size)*100:.1f}%"),
            ("Numeric Cols", str(len(num_cols))),
        ]
        kpi_cells  = [[Paragraph(lbl, S_KPI_LBL) for lbl,_ in kpi_items],
                      [Paragraph(val, S_KPI_VAL) for _,val in kpi_items]]
        kpi_widths = [W/4]*4
        kpi_tbl    = Table(kpi_cells, colWidths=kpi_widths, rowHeights=[16, 30])
        kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), colors.HexColor("#16213e")),
            ("LINEBELOW",    (0,0),(-1,0),  0.5, C_GREY),
            ("TOPPADDING",   (0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("LINEBEFORE",   (1,0),(3,-1),  0.5, colors.HexColor("#2a2a3e")),
        ]))
        story.append(kpi_tbl)
        story.append(Spacer(1, 18))

        def section_heading(num, title):
            story.append(HRFlowable(width=W, thickness=0.5, color=C_GREY, spaceAfter=0))
            data = [[
                Paragraph(f"<font color='#e03e3e'>{num}</font>", S_SEC),
                Paragraph(f"  {title}", S_SEC),
            ]]
            t = Table(data, colWidths=[20, W-20])
            t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("TOPPADDING",(0,0),(-1,-1),2)]))
            story.append(t)
            story.append(Spacer(1, 6))

        def body_para(text):
            clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            clean = clean.replace("\n\n", "<br/><br/>").replace("\n","<br/>")
            story.append(Paragraph(clean, S_BODY))
            story.append(Spacer(1, 4))

        def bullet_paras(text):
            lines = [l.strip().lstrip("-•*").strip() for l in text.strip().split("\n") if l.strip()]
            for l in lines:
                clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', l)
                story.append(Paragraph(f"• {clean}", S_BULLET))

        # ── 1. Executive Summary ─────────────────────────────────────────────
        section_heading("01", "Executive Summary")
        body_para(ai_exec if ai_exec else fallback_exec())

        # ── 2. Objectives ────────────────────────────────────────────────────
        section_heading("02", "Objectives")
        bullet_paras(ai_obj if ai_obj else fallback_objectives())
        story.append(Spacer(1,6))

        # ── 3. Methodology ───────────────────────────────────────────────────
        section_heading("03", "Methodology")
        body_para(ai_method if ai_method else fallback_methodology())

        # ── 4. Statistical Snapshot ──────────────────────────────────────────
        section_heading("04", "Statistical Snapshot")
        if num_cols:
            snap = df[top_num].describe().T.round(3).reset_index()
            snap.columns = [str(c) for c in snap.columns]
            tbl_data  = [snap.columns.tolist()] + snap.values.tolist()
            col_w     = [W/(len(snap.columns))]*len(snap.columns)
            snap_tbl  = Table(tbl_data, colWidths=col_w)
            snap_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0,0),(-1,0),   C_DARK),
                ("TEXTCOLOR",   (0,0),(-1,0),   C_RED),
                ("FONTNAME",    (0,0),(-1,0),   "Helvetica-Bold"),
                ("FONTSIZE",    (0,0),(-1,-1),  7.5),
                ("BACKGROUND",  (0,1),(-1,-1),  colors.HexColor("#16213e")),
                ("TEXTCOLOR",   (0,1),(-1,-1),  C_LIGHT),  # noqa: F821
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.HexColor("#16213e"), colors.HexColor("#1a1a2e")]),
                ("GRID",        (0,0),(-1,-1),  0.3, colors.HexColor("#2a2a3e")),
                ("ALIGN",       (0,0),(-1,-1),  "CENTER"),
                ("TOPPADDING",  (0,0),(-1,-1),  5),
                ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ]))
            story.append(snap_tbl)
        story.append(Spacer(1,10))

        # ── 5. Key Findings ──────────────────────────────────────────────────
        section_heading("05", "Key Findings")
        bullet_paras(ai_findings if ai_findings else fallback_findings(top_num, top_cat))
        story.append(Spacer(1,6))

        # ── 6. Conclusions ───────────────────────────────────────────────────
        section_heading("06", "Conclusions")
        body_para(ai_concl if ai_concl else fallback_conclusions())

        # ── 7. Recommendations ───────────────────────────────────────────────
        section_heading("07", "Actionable Recommendations")
        recs = ai_recs if ai_recs else fallback_recommendations()
        bullet_paras(recs)
        story.append(Spacer(1,6))

        # ── 8. Next Steps ────────────────────────────────────────────────────
        section_heading("08", "Suggested Next Steps")
        steps_data = [
            ["Clean & Enrich",  "Handle missing values and engineer features"],
            ["Build ML Model",  f"Train models on: {', '.join(top_num[:3])}"],
            ["Monitor KPIs",    "Set up automated dashboards for key metrics"],
            ["Share Insights",  "Export and share report with stakeholders"],
        ]
        steps_tbl = Table(steps_data, colWidths=[W*0.28, W*0.72])
        steps_tbl.setStyle(TableStyle([
            ("FONTNAME",    (0,0),(0,-1), "Helvetica-Bold"),
            ("FONTNAME",    (1,0),(1,-1), "Helvetica"),
            ("FONTSIZE",    (0,0),(-1,-1), 8.5),
            ("TEXTCOLOR",   (0,0),(0,-1), C_RED),
            ("TEXTCOLOR",   (1,0),(1,-1), C_LIGHT),  # noqa: F821
            ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#16213e")),
            ("ROWBACKGROUNDS",(0,0),(-1,-1), [colors.HexColor("#16213e"), colors.HexColor("#1a1a2e")]),
            ("GRID",        (0,0),(-1,-1), 0.3, colors.HexColor("#2a2a3e")),
            ("TOPPADDING",  (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("LEFTPADDING", (0,0),(-1,-1), 10),
        ]))
        story.append(steps_tbl)

        # ── Footer ───────────────────────────────────────────────────────────
        story.append(Spacer(1, 24))
        story.append(HRFlowable(width=W, thickness=0.5, color=C_GREY))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Generated by DataSense AI  ·  {datetime.now().strftime('%d %B %Y, %H:%M')}  ·  CONFIDENTIAL",
            style("footer", fontName="Helvetica", fontSize=7, textColor=C_GREY,
                  alignment=TA_CENTER, leading=10)
        ))

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    except ImportError:
        return None

# ── Export buttons ────────────────────────────────────────────────────────────
dl1, dl2, dl3 = st.columns(3)

with dl1:
    st.markdown("""
    <div class="stat-card" style="background:#1e1e2e; text-align:center; padding:24px 16px;">
        <div style="font-size:2rem; margin-bottom:8px;">📑</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;
        font-size:0.95rem;color:#ffffff;margin-bottom:6px;">PDF Report</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#888899;">
        Full formatted report with all sections</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    if st.button("⬇️  Download PDF", use_container_width=True, key="dl_pdf"):
        with st.spinner("Generating PDF..."):
            pdf_bytes = generate_pdf()
        if pdf_bytes:
            st.download_button(
                label="📥  Click to Save PDF",
                data=pdf_bytes,
                file_name=f"{filename}_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.error("❌ reportlab not installed. Run: pip install reportlab")

with dl2:
    st.markdown("""
    <div class="stat-card" style="background:#1e1e2e; text-align:center; padding:24px 16px;">
        <div style="font-size:2rem; margin-bottom:8px;">📄</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;
        font-size:0.95rem;color:#ffffff;margin-bottom:6px;">CSV Data</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#888899;">
        Download the cleaned dataset</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.download_button(
        "⬇️  Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"{filename}_clean.csv",
        mime="text/csv",
        use_container_width=True
    )

with dl3:
    st.markdown("""
    <div class="stat-card" style="background:#1e1e2e; text-align:center; padding:24px 16px;">
        <div style="font-size:2rem; margin-bottom:8px;">📊</div>
        <div style="font-family:'Outfit',sans-serif;font-weight:700;
        font-size:0.95rem;color:#ffffff;margin-bottom:6px;">Excel Report</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#888899;">
        Data + Stats + Findings in sheets</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Data")
        if num_cols:
            df[num_cols].describe().round(3).to_excel(w, sheet_name="Statistics")
        findings_df = pd.DataFrame({
            "Section": ["Executive Summary","Objectives","Methodology","Findings","Conclusions","Recommendations"],
            "Content": [
                ai_exec or fallback_exec(),
                ai_obj  or fallback_objectives(),
                ai_method or fallback_methodology(),
                ai_findings or fallback_findings(top_num, top_cat),
                ai_concl or fallback_conclusions(),
                ai_recs  or fallback_recommendations(),
            ]
        })
        findings_df.to_excel(w, index=False, sheet_name="Report")
    st.download_button(
        "⬇️  Download Excel",
        data=excel_buf.getvalue(),
        file_name=f"{filename}_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown(f"""
<p style="text-align:center;font-family:'DM Mono',monospace;font-size:0.68rem;
color:#2a2a4a;letter-spacing:1px;">
DATASENSE AI &nbsp;·&nbsp; ANALYTICS REPORT &nbsp;·&nbsp; {datetime.now().strftime('%d %B %Y')}
</p>
""", unsafe_allow_html=True)
