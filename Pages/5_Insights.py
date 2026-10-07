from utils.ai_handler import get_ai_response
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys, os
import matplotlib as plt
import seaborn as sns
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header, apply_plotly_style

st.set_page_config(page_title="Insights · DataSense", page_icon="🧠", layout="wide")
inject_css()
sidebar_dataset_info()

page_header("🧠", "Rule Based Insights", "Auto-generated plain-English analysis of your dataset")
st.markdown('<hr>', unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No data loaded. Go to **Upload** first."); st.stop()

df = st.session_state["df"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()

def generate(df):
    out = []

    # Each item: (short_title, emoji, kind, body)
    out.append(("Dataset Overview", "📋", "info",
        f"Your dataset has **{df.shape[0]:,} rows** and **{df.shape[1]} columns** — "
        f"**{len(num_cols)} numeric** and **{len(cat_cols)} categorical**. "
        f"Total cell count: **{df.size:,}**."))

    total_miss = df.isnull().sum().sum()
    if total_miss == 0:
        out.append(("No Missing Values", "✅", "success",
            "Zero missing values across all columns. Your dataset is complete."))
    else:
        worst = df.isnull().sum().idxmax()
        pct   = df.isnull().sum().max() / len(df) * 100
        detail = "\n".join([f"- **{c}**: {v} missing ({v/len(df)*100:.1f}%)"
                            for c,v in df.isnull().sum().items() if v > 0])
        out.append(("Missing Values", "⚠️", "warning",
            f"**{total_miss:,} missing values** found. Worst: **'{worst}'** at **{pct:.1f}%**.\n\n{detail}\n\n"
            "→ Fix on the **Clean Data** page."))

    n_dup = df.duplicated().sum()
    if n_dup > 0:
        out.append(("Duplicate Rows", "🔁", "warning",
            f"**{n_dup} duplicate rows** ({n_dup/len(df)*100:.1f}%). "
            "Remove on the **Clean Data** page."))
    else:
        out.append(("No Duplicates", "✅", "success",
            "No duplicate rows found in your dataset."))

    for col in num_cols:
        skew = df[col].skew()
        if abs(skew) > 1:
            d = "right-skewed" if skew > 0 else "left-skewed"
            out.append((f"'{col}' is {d}", "📊", "info",
                f"**'{col}'** skewness = **{skew:.3f}** ({d}).\n\n"
                f"Mean **{df[col].mean():.3f}** ≠ Median **{df[col].median():.3f}**.\n\n"
                "Tip: use **log transformation** to normalize for ML models."))

    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        us   = corr.abs().unstack().sort_values(ascending=False)
        us   = us[us < 1.0].drop_duplicates()
        if len(us) > 0:
            a,b  = us.index[0]
            r    = corr.loc[a,b]
            s    = "strong" if abs(r)>0.7 else ("moderate" if abs(r)>0.4 else "weak")
            d    = "positive" if r > 0 else "negative"
            out.append((f"Top Correlation: {a} & {b}", "🔗", "info",
                f"**'{a}'** and **'{b}'** have a **{s} {d} correlation** (r = **{r:.3f}**).\n\n"
                f"{'They move together.' if r>0 else 'They move inversely.'} "
                "Useful for feature selection in ML."))

        near_zero = us[us < 0.05]
        if len(near_zero) > 0:
            a2,b2 = near_zero.index[0]
            out.append((f"No Correlation: {a2} & {b2}", "🔍", "info",
                f"**'{a2}'** and **'{b2}'** show almost no relationship "
                f"(r ≈ **{corr.loc[a2,b2]:.3f}**). These columns appear independent."))

    for col in cat_cols:
        n_u = df[col].nunique()
        if n_u > 50:
            out.append((f"High Cardinality: '{col}'", "🔤", "warning",
                f"**'{col}'** has **{n_u} unique values**. "
                "Consider grouping rare values or using target encoding for ML."))
        if not df[col].mode().empty:
            top_v = df[col].mode()[0]
            top_p = (df[col]==top_v).sum()/len(df)*100
            if top_p > 60:
                out.append((f"Dominant Value in '{col}'", "📌", "warning",
                    f"**'{top_v}'** appears in **{top_p:.1f}%** of '{col}'. "
                    "Very low diversity — may not be useful as a feature."))

    for col in df.columns:
        if df[col].nunique() == 1:
            out.append((f"Constant Column: '{col}'", "🚫", "danger",
                f"**'{col}'** has only 1 unique value. "
                "Carries no information — drop before ML."))

    for col in num_cols:
        Q1,Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        n_out = ((df[col] < Q1-1.5*IQR)|(df[col] > Q3+1.5*IQR)).sum()
        if n_out > 0 and n_out/len(df) > 0.05:
            out.append((f"Many Outliers in '{col}'", "⚠️", "warning",
                f"**{n_out} outliers** ({n_out/len(df)*100:.1f}%) in **'{col}'** (IQR method).\n\n"
                f"Valid range: **{Q1-1.5*IQR:.2f}** → **{Q3+1.5*IQR:.2f}**\n\n"
                "→ Go to **Outlier Detection** to handle."))

    return out

with st.spinner("Analyzing..."):
    insights = generate(df)

# ── Color-coded count row ─────────────────────────────────────────────────────
good    = sum(1 for _,_,k,_ in insights if k=="success")
warning = sum(1 for _,_,k,_ in insights if k=="warning")
danger  = sum(1 for _,_,k,_ in insights if k=="danger")
info    = sum(1 for _,_,k,_ in insights if k=="info")

st.markdown(f"""
<div style="display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;">
    <div style="background:rgba(0,245,160,0.08); border:1px solid rgba(0,245,160,0.2);
    border-radius:8px; padding:8px 16px; font-family:'DM Mono',monospace; font-size:0.8rem; color:#00f5a0;">
    ✅ {good} Good</div>
    <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.2);
    border-radius:8px; padding:8px 16px; font-family:'DM Mono',monospace; font-size:0.8rem; color:#f59e0b;">
    ⚠️ {warning} Action Needed</div>
    <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2);
    border-radius:8px; padding:8px 16px; font-family:'DM Mono',monospace; font-size:0.8rem; color:#ef4444;">
    🚫 {danger} Critical</div>
    <div style="background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.2);
    border-radius:8px; padding:8px 16px; font-family:'DM Mono',monospace; font-size:0.8rem; color:#00d4ff;">
    💡 {info} Info</div>
</div>
""", unsafe_allow_html=True)

# ── Render expanders — plain text titles only (no HTML inside expander label) ──
for short_title, emoji, kind, body in insights:
    # Plain label — no HTML tags, Streamlit renders this as text
    label = f"{emoji}  {short_title}"
    with st.expander(label, expanded=False):
        if kind == "success":   st.success(body)
        elif kind == "warning": st.warning(body)
        elif kind == "danger":  st.error(body)
        else:                   st.info(body)

st.markdown('<hr>', unsafe_allow_html=True)

# ── NEW SECTION: Quick Statistical Insights ───────────────────────────────────
with st.expander("📊 Quick Statistical Insights"):
    st.subheader("🔥 Key Insights")
    quick_insights = []

    if num_cols:
        for col in num_cols:
            quick_insights.append(f"{col}: avg = {df[col].mean():.2f}, max = {df[col].max()}")

    if cat_cols:
        for col in cat_cols[:2]:
            if not df[col].mode().empty:
                top = df[col].mode()[0]
                quick_insights.append(f"{col}: most common = {top}")

    for ins in quick_insights[:6]:
        st.write("•", ins)

# ── Heatmap ───────────────────────────────────────────────────────────────────
if len(num_cols) >= 2:
    st.markdown('<div class="section-title">Correlation Matrix</div>', unsafe_allow_html=True)
    corr = df[num_cols].corr().round(2)
    fig  = px.imshow(corr, text_auto=True, aspect="auto",
                     color_continuous_scale="RdBu_r",
                     title="Correlation Heatmap", template="plotly_dark")
    apply_plotly_style(fig, height=500)
    st.plotly_chart(fig, use_container_width=True)

if num_cols:
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Distributions</div>', unsafe_allow_html=True)
    rows = [num_cols[i:i+3] for i in range(0, len(num_cols), 3)]
    for row in rows:
        cols = st.columns(len(row))
        for i, cn in enumerate(row):
            with cols[i]:
                fig = px.histogram(df, x=cn, nbins=30, template="plotly_dark",
                                   color_discrete_sequence=["#00f5a0"])
                apply_plotly_style(fig, height=230)
                fig.update_layout(margin=dict(t=36,b=20,l=10,r=10),
                                  title=dict(text=cn, font_size=12))
                fig.update_xaxes(showgrid=False); fig.update_yaxes(showgrid=False)
                st.plotly_chart(fig, use_container_width=True)

                
# ── 🤖 AI INSIGHTS (Gemini) ───────────────────────────────────
# ── 🤖 AI INSIGHTS WITH DROPDOWN ───────────────────────────

# ── 🤖 AI INSIGHTS (Gemini) ───────────────────────────

st.markdown(" 🤖 AI Insights")

user_query = st.text_input(
    "Ask questions about your dataset",
    placeholder="Example: What trends do you observe?"
)

if st.button("Generate AI Insights"):

    with st.spinner("Analyzing dataset with Gemini AI..."):

        try:

            # Prepare optimized dataset info
            columns = df.columns.tolist()

            sample = df.head(5).to_string()

            summary = df.describe(include="all").to_string()

            # Use user question if provided
            if not user_query:
                user_query = """
Provide:
- Key Trends
- Patterns
- Anomalies
- Opportunities
- Risks
"""

            # Generate AI response
            ai_response = get_ai_response(
                columns,
                sample,
                summary,
                user_query
            )

            st.success("✅ AI Insights Generated")

            # Split nicely into expandable sections
            sections = ai_response.split("###")

            if len(sections) > 1:

                for sec in sections:

                    if sec.strip():

                        lines = sec.strip().split("\n")

                        title = lines[0]

                        content = "\n".join(lines[1:])

                        with st.expander(f"📌 {title}"):

                            st.write(content)

            else:

                st.write(ai_response)

        except Exception as e:

            st.error(f"❌ Gemini AI Error: {str(e)}")

            print("FULL ERROR:", e)