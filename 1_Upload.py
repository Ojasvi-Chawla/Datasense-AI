import scipy
from scipy import stats
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header, stat_card

st.set_page_config(page_title="Upload · DataSense", page_icon="📁", layout="wide",initial_sidebar_state="auto")
inject_css()
sidebar_dataset_info()

page_header("📁", "Upload & Preview", "Load your dataset and instantly explore its structure")
st.markdown('<hr>', unsafe_allow_html=True)

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Drop your CSV, Excel or JSON file here",
    type=["csv","xlsx","xls","json"],
    label_visibility="collapsed"
)

def load_file(file):
    name = file.name
    if name.endswith(".csv"):
        for enc in ["utf-8","latin1","cp1252"]:
            try:
                file.seek(0); return pd.read_csv(file, encoding=enc)
            except: continue
    elif name.endswith((".xlsx",".xls")):
        return pd.read_excel(file)
    elif name.endswith(".json"):
        return pd.read_json(file)

st.markdown("""
<p style="font-family:'DM Mono',monospace; font-size:0.75rem; color:#4a4a6a; margin-top:6px; text-align:center;">
Supports CSV · Excel (.xlsx/.xls) · JSON &nbsp;·&nbsp; Max ~200MB
</p>
""", unsafe_allow_html=True)

# ── Cache logic ───────────────────────────────────────────────────────────────
if uploaded_file:
    if st.session_state.get("filename") != uploaded_file.name:
        df = load_file(uploaded_file)
        if df is not None:
            st.session_state["df"]       = df
            st.session_state["df_clean"] = df.copy()
            st.session_state["filename"] = uploaded_file.name
            st.success(f"✅ **{uploaded_file.name}** loaded and cached.")
        else:
            st.error("❌ Could not read file. Check format and try again."); st.stop()
    else:
        st.info(f"📦 Using cached dataset: **{st.session_state['filename']}**")

if "df" not in st.session_state or st.session_state["df"] is None:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">No Dataset Loaded</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-family:'DM Mono',monospace; font-size:0.82rem; color:#5a5a7a; line-height:1.8;">
    Upload a file above to get started. Need sample data?
    </p>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown("""<div class="stat-card"><div class="stat-label">Kaggle</div>
    <div class="stat-value" style="font-size:1rem;">kaggle.com/datasets</div>
    <div class="stat-sub">1000s of free datasets</div></div>""", unsafe_allow_html=True)
    c2.markdown("""<div class="stat-card"><div class="stat-label">UCI ML Repo</div>
    <div class="stat-value" style="font-size:1rem;">archive.ics.uci.edu</div>
    <div class="stat-sub">Classic ML datasets</div></div>""", unsafe_allow_html=True)
    c3.markdown("""<div class="stat-card"><div class="stat-label">Google</div>
    <div class="stat-value" style="font-size:1rem;">datasetsearch.research</div>
    <div class="stat-sub">Google Dataset Search</div></div>""", unsafe_allow_html=True)
    st.stop()

df = st.session_state["df"]

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Dataset Overview</div>', unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
cards = [
    ("Rows",           f"{df.shape[0]:,}",                    "total records"),
    ("Columns",        f"{df.shape[1]}",                      "features"),
    ("Missing Values", f"{df.isnull().sum().sum():,}",         f"{df.isnull().sum().sum()/df.size*100:.1f}% of cells"),
    ("Duplicates",     f"{df.duplicated().sum():,}",           "duplicate rows"),
    ("Memory",         f"{df.memory_usage(deep=True).sum()/1024:.1f} KB", "in memory"),
]
for col, (label, val, sub) in zip([c1,c2,c3,c4,c5], cards):
    col.markdown(stat_card(label, val, sub), unsafe_allow_html=True)

# ── DATA QUALITY SCORE ────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Data Quality</div>', unsafe_allow_html=True)

def compute_quality(df):
    scores = {}
    n_rows, n_cols = df.shape
    total_cells = n_rows * n_cols

    # 1. COMPLETENESS — how many cells are filled
    missing = df.isnull().sum().sum()
    completeness = round((1 - missing / total_cells) * 100, 1)
    scores["Completeness"] = {
        "score": completeness,
        "icon": "📋",
        "detail": f"{total_cells - missing:,} of {total_cells:,} cells filled. {missing:,} missing.",
        "tip": "Fill missing values on the Clean Data page." if missing > 0 else "No missing values — perfect!"
    }

    # 2. UNIQUENESS — penalise duplicate rows
    dupes = df.duplicated().sum()
    uniqueness = round((1 - dupes / n_rows) * 100, 1)
    scores["Uniqueness"] = {
        "score": uniqueness,
        "icon": "🔁",
        "detail": f"{n_rows - dupes:,} unique rows out of {n_rows:,} total. {dupes} duplicates found.",
        "tip": "Remove duplicates on the Clean Data page." if dupes > 0 else "No duplicate rows."
    }

    # 3. CONSISTENCY — detect mixed types inside object columns
    inconsistent = 0
    for col in df.select_dtypes(include="object").columns:
        sample = df[col].dropna().head(200)
        num_like = sample.apply(lambda x: str(x).replace('.','',1).replace('-','',1).isdigit()).sum()
        if 0 < num_like < len(sample):        # mixed numeric + text
            inconsistent += 1
    consistency = round((1 - inconsistent / max(n_cols, 1)) * 100, 1)
    scores["Consistency"] = {
        "score": consistency,
        "icon": "🔀",
        "detail": f"{inconsistent} column(s) have mixed data types (text + numbers).",
        "tip": "Convert column types using the Clean Data page." if inconsistent > 0 else "All columns have consistent types."
    }

    # 4. VALIDITY — check numeric columns for suspicious values (all zeros, negative if unlikely)
    invalid_cols = 0
    for col in df.select_dtypes(include="number").columns:
        if df[col].dropna().std() == 0:       # constant column — no information
            invalid_cols += 1
    validity = round((1 - invalid_cols / max(len(df.select_dtypes(include="number").columns), 1)) * 100, 1)
    scores["Validity"] = {
        "score": validity,
        "icon": "✅",
        "detail": f"{invalid_cols} numeric column(s) have zero variance (constant values).",
        "tip": "Drop constant columns — they carry no information." if invalid_cols > 0 else "All numeric columns carry meaningful variance."
    }

    # 5. ACCURACY — proxy: outlier ratio across numeric columns (high outliers = suspicious data)
    import numpy as np
    from scipy import stats
    num_df = df.select_dtypes(include="number")
    outlier_flags = 0
    total_numeric_cells = 0
    for col in num_df.columns:
        col_clean = num_df[col].dropna()
        if len(col_clean) < 4:
            continue
        z = np.abs(stats.zscore(col_clean.to_numpy()))
        outlier_flags     += int((z > 3).sum())
        total_numeric_cells += len(col_clean)
    outlier_ratio = outlier_flags / max(total_numeric_cells, 1)
    accuracy = round(max(0, (1 - outlier_ratio * 10)) * 100, 1)   # penalise heavily
    scores["Accuracy"] = {
        "score": min(accuracy, 100),
        "icon": "🎯",
        "detail": f"{outlier_flags} extreme outlier cells detected across all numeric columns (Z > 3).",
        "tip": "Handle outliers on the Outlier Detection page." if outlier_flags > 0 else "No extreme outliers detected."
    }

    # 6. TIMELINESS — check if any datetime columns exist and are recent
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    # also try to parse object cols named date/time/year
    for col in df.select_dtypes(include="object").columns:
        if any(w in col.lower() for w in ["date","time","year","month","day"]):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() > len(df) * 0.5:
                    date_cols.append(col)
            except:
                pass
    if date_cols:
        try:
            latest = pd.to_datetime(df[date_cols[0]], errors="coerce").max()
            days_old = (pd.Timestamp.now() - latest).days
            timeliness = round(max(0, 100 - days_old * 0.05), 1)   # -0.05 per day old
            detail_t = f"Most recent date in '{date_cols[0]}': {latest.date()} ({days_old} days ago)."
            tip_t    = "Data is fresh." if days_old < 30 else "Consider updating with more recent data."
        except:
            timeliness = 70.0
            detail_t   = "Date column found but could not parse dates precisely."
            tip_t      = "Ensure date columns are in a standard format."
    else:
        timeliness = 70.0   # neutral — no date column to judge
        detail_t   = "No date/time column detected. Score set to neutral (70)."
        tip_t      = "Add a date column to measure timeliness properly."
    scores["Timeliness"] = {
        "score": timeliness,
        "icon": "🕐",
        "detail": detail_t,
        "tip": tip_t
    }

    # 7. DENSITY — ratio of non-null numeric data (bonus metric)
    if not num_df.empty:
        density = round(num_df.notna().sum().sum() / max(num_df.size, 1) * 100, 1)
    else:
        density = 100.0
    scores["Density"] = {
        "score": density,
        "icon": "📊",
        "detail": f"{density}% of numeric cells contain actual values.",
        "tip": "A high density means more data is available for analysis."
    }

    # ── Final weighted score ──────────────────────────────────────────────────
    weights = {
        "Completeness": 0.25,
        "Uniqueness":   0.15,
        "Consistency":  0.15,
        "Validity":     0.15,
        "Accuracy":     0.20,
        "Timeliness":   0.05,
        "Density":      0.05,
    }
    final = sum(scores[k]["score"] * weights[k] for k in weights)
    return round(final, 1), scores

overall_score, metric_scores = compute_quality(df)

# ── Score color ───────────────────────────────────────────────────────────────
if overall_score >= 85:
    score_color = "#00f5a0"; grade = "Excellent"; grade_icon = "🏆"
elif overall_score >= 70:
    score_color = "#f59e0b"; grade = "Good";      grade_icon = "👍"
elif overall_score >= 50:
    score_color = "#f97316"; grade = "Fair";      grade_icon = "⚠️"
else:
    score_color = "#ef4444"; grade = "Poor";      grade_icon = "🚨"

# ── Score display ─────────────────────────────────────────────────────────────
qc1, qc2 = st.columns([1, 3])

with qc1:
    st.markdown(f"""
    <div class="stat-card" style="text-align:center; padding:24px 16px;">
        <div class="stat-label">Overall Score</div>
        <div style="font-family:'Outfit',sans-serif; font-weight:900;
                    font-size:3rem; color:{score_color}; line-height:1;">
            {overall_score}
        </div>
        <div style="font-family:'DM Mono',monospace; font-size:0.7rem;
                    color:{score_color}; margin-top:4px; letter-spacing:1px;">
            / 100 &nbsp;·&nbsp; {grade_icon} {grade}
        </div>
    </div>
    """, unsafe_allow_html=True)

with qc2:
    # Mini bar chart for each metric
    for name, info in metric_scores.items():
        s = info["score"]
        bar_color = "#00f5a0" if s >= 85 else ("#f59e0b" if s >= 70 else ("#f97316" if s >= 50 else "#ef4444"))
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:7px;">
            <div style="font-family:'DM Mono',monospace; font-size:0.72rem;
                        color:#6b6b8a; width:110px; flex-shrink:0;">
                {info['icon']} {name}
            </div>
            <div style="flex:1; background:rgba(255,255,255,0.05);
                        border-radius:99px; height:8px; overflow:hidden;">
                <div style="width:{s}%; height:100%; background:{bar_color};
                            border-radius:99px; transition:width 0.6s ease;"></div>
            </div>
            <div style="font-family:'Outfit',sans-serif; font-weight:700;
                        font-size:0.82rem; color:{bar_color}; width:40px; text-align:right;">
                {s}%
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Breakdown dropdown ────────────────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)
with st.expander("📐  How is this score calculated? (click to expand)", expanded=False):
    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.78rem; color:#6b6b8a;
                line-height:1.9; padding:4px 0;">
    The <b>Data Quality Score</b> is a weighted average of 7 industry-standard dimensions:
    </div>
    """, unsafe_allow_html=True)

    breakdown_cols = st.columns(2)
    weights_display = {
        "Completeness": ("25%", "Are all cells filled? Penalises missing values."),
        "Accuracy":     ("20%", "Are values realistic? Penalises extreme outliers (Z > 3)."),
        "Uniqueness":   ("15%", "Are rows unique? Penalises duplicate records."),
        "Consistency":  ("15%", "Are column types uniform? Penalises mixed types."),
        "Validity":     ("15%", "Do numeric columns have variance? Penalises constant columns."),
        "Timeliness":   ("5%",  "How recent is the data? Based on the latest date column."),
        "Density":      ("5%",  "What % of numeric cells contain values?"),
    }

    items = list(weights_display.items())
    for i, (metric, (weight, desc)) in enumerate(items):
        col = breakdown_cols[i % 2]
        info = metric_scores[metric]
        s    = info["score"]
        bar_color = "#00f5a0" if s >= 85 else ("#f59e0b" if s >= 70 else ("#f97316" if s >= 50 else "#ef4444"))
        col.markdown(f"""
        <div class="stat-card" style="margin-bottom:10px; padding:14px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="font-family:'Outfit',sans-serif; font-weight:700;
                            font-size:0.9rem; color:#e2e2f0;">
                    {info['icon']} {metric}
                </div>
                <div style="font-family:'Outfit',sans-serif; font-weight:800;
                            font-size:1.1rem; color:{bar_color};">{s}%</div>
            </div>
            <div style="font-family:'DM Mono',monospace; font-size:0.68rem;
                        color:#f59e0b; margin:4px 0;">Weight: {weight}</div>
            <div style="font-family:'DM Mono',monospace; font-size:0.7rem;
                        color:#6b6b8a; line-height:1.5;">{desc}</div>
            <div style="font-family:'DM Mono',monospace; font-size:0.7rem;
                        color:#4a4a6a; margin-top:6px; padding-top:6px;
                        border-top:1px solid rgba(255,255,255,0.05);">
                📌 {info['detail']}
            </div>
            <div style="font-family:'DM Mono',monospace; font-size:0.7rem;
                        color:{bar_color}; margin-top:4px;">
                💡 {info['tip']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)
# ── END DATA QUALITY SCORE ────────────────────────────────────────────────────

st.markdown('<hr>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📄  Preview", "🔠  Column Info", "📈  Statistics", "❓  Missing Values"])

with tab1:
    n = st.slider("Rows to display", 5, min(200, len(df)), 10)
    st.dataframe(df.head(n), use_container_width=True, height=380)
    st.markdown(f'<p class="stat-sub" style="margin-top:4px;">Showing {n} of {len(df):,} rows</p>', unsafe_allow_html=True)

with tab2:
    info_df = pd.DataFrame({
        "Column":         df.columns,
        "Type":           df.dtypes.values.astype(str),
        "Non-Null":       df.count().values,
        "Null Count":     df.isnull().sum().values,
        "Null %":         (df.isnull().sum().values / len(df) * 100).round(2),
        "Unique Values":  df.nunique().values,
    })
    st.dataframe(info_df, use_container_width=True, height=380)

    st.markdown('<br>', unsafe_allow_html=True)
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    dt_cols  = df.select_dtypes(include="datetime").columns.tolist()
    cc1,cc2,cc3 = st.columns(3)
    cc1.info(f"🔢 **Numeric ({len(num_cols)})**\n\n" + (', '.join(num_cols) if num_cols else "None"))
    cc2.info(f"🔤 **Categorical ({len(cat_cols)})**\n\n" + (', '.join(cat_cols) if cat_cols else "None"))
    cc3.info(f"📅 **Datetime ({len(dt_cols)})**\n\n" + (', '.join(dt_cols) if dt_cols else "None"))

with tab3:
    num_df = df.select_dtypes(include=np.number)
    if not num_df.empty:
        st.dataframe(num_df.describe().T.round(3), use_container_width=True, height=350)
    cat_df = df.select_dtypes(include="object")
    if not cat_df.empty:
        st.markdown('<br>', unsafe_allow_html=True)
        for col in cat_df.columns:
            with st.expander(f"🔤  {col}  ·  {df[col].nunique()} unique values"):
                vc = df[col].value_counts().head(10).reset_index()
                vc.columns = [col, "Count"]
                st.dataframe(vc, use_container_width=True)

with tab4:
    miss = df.isnull().sum().reset_index()
    miss.columns = ["Column", "Missing"]
    miss["Missing %"] = (miss["Missing"] / len(df) * 100).round(2)
    miss = miss[miss["Missing"] > 0].sort_values("Missing %", ascending=False)
    if miss.empty:
        st.success("🎉 No missing values — your dataset is complete!")
    else:
        st.warning(f"⚠️ **{len(miss)}** column(s) contain missing values.")
        st.dataframe(miss, use_container_width=True)
        st.info("👉 Head to **Clean Data** to fix these.")

st.markdown('<hr>', unsafe_allow_html=True)
st.download_button(
    "⬇️  Download as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"preview_{st.session_state.get('filename','data.csv')}",
    mime="text/csv"
)
