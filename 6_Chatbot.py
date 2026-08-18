from utils.ai_handler import get_ai_response
import streamlit as st
import pandas as pd
import numpy as np
import re
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header

st.set_page_config(page_title="Chatbot · DataSense", page_icon="💬", layout="wide")
inject_css()
sidebar_dataset_info()

page_header("💬", "Data Chatbot", "Ask questions about your data in plain English")
st.markdown('<hr>', unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No data loaded. Go to **Upload** first."); st.stop()

df       = st.session_state["df"]
filename = st.session_state.get("filename","dataset.csv").replace(".csv","").replace(".xlsx","")
num_cols = df.select_dtypes(include=np.number).columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()
all_cols = df.columns.tolist()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── Smart dataset describer ───────────────────────────────────────────────────
def guess_dataset_topic():
    """Try to infer what the dataset is about from filename + column names."""
    hints = (filename + " " + " ".join(all_cols)).lower()

    topics = {
        "cars / automobiles": ["mpg","cyl","disp","hp","drat","wt","qsec","gear","carb","car","auto","vehicle","engine","fuel","horsepower","cylinder"],
        "sales / revenue":    ["sales","revenue","profit","price","cost","amount","discount","order","customer","product","quantity"],
        "students / education": ["marks","grade","score","student","subject","pass","fail","exam","gpa","attendance","course"],
        "employees / HR":     ["salary","employee","department","age","experience","hire","job","position","manager","gender"],
        "health / medical":   ["age","bmi","glucose","blood","pressure","diabetes","heart","cholesterol","weight","height","patient","hospital"],
        "housing / real estate": ["price","sqft","bedroom","bathroom","house","property","location","zip","area","floor"],
        "weather / climate":  ["temperature","humidity","wind","rain","pressure","weather","climate","forecast","season"],
        "e-commerce":         ["product","category","rating","review","price","seller","buyer","shipping","order"],
        "finance / stocks":   ["open","close","high","low","volume","stock","price","return","dividend","market"],
        "sports":             ["team","player","score","win","loss","goal","point","match","season","league"],
        "titanic / passengers": ["survived","pclass","name","sex","age","sibsp","parch","ticket","fare","cabin","embarked"],
        "iris / flowers":     ["sepal","petal","species","iris"],
    }

    for topic, keywords in topics.items():
        if any(k in hints for k in keywords):
            return topic
    return None

def describe_dataset():
    """Generate a smart human-readable description of what the dataset is about."""
    topic = guess_dataset_topic()
    rows, cols = df.shape
    num_count  = len(num_cols)
    cat_count  = len(cat_cols)
    miss       = df.isnull().sum().sum()

    # Topic intro
    if topic:
        topic_line = f"This appears to be a **{topic}** dataset"
    else:
        topic_line = f"This is a dataset named **'{filename}'**"

    # Key columns summary
    key_num = num_cols[:4]
    key_cat = cat_cols[:3]

    num_summary = ""
    if key_num:
        stats = [f"**{c}** (avg: {df[c].mean():.2f})" for c in key_num]
        num_summary = f"\n\n**Key numeric columns:** {', '.join(stats)}"

    cat_summary = ""
    if key_cat:
        cat_details = []
        for c in key_cat:
            top = df[c].mode()[0] if not df[c].mode().empty else "—"
            cat_details.append(f"**{c}** (e.g. '{top}')")
        cat_summary = f"\n\n**Key categorical columns:** {', '.join(cat_details)}"

    # Data quality line
    quality = "clean with no missing values" if miss == 0 else f"has **{miss} missing values** that may need cleaning"

    return (
        f"{topic_line} with **{rows:,} records** and **{cols} features** "
        f"({num_count} numeric, {cat_count} categorical)."
        f"{num_summary}"
        f"{cat_summary}"
        f"\n\nData quality: The dataset is {quality}."
    )

# ── Column finder ─────────────────────────────────────────────────────────────
def find_col(text):
    tl = text.lower()
    for col in sorted(all_cols, key=len, reverse=True):
        if col.lower() in tl: return col
    words = re.findall(r'\w+', tl)
    for w in words:
        for col in all_cols:
            if w in col.lower() and len(w) > 3: return col
    return None

# ── Answer engine ─────────────────────────────────────────────────────────────

def answer(q_raw):
    q   = q_raw.lower().strip()
    col = find_col(q)

    # ── Describe / what is / tell me about ───────────────────────────────────
    if any(w in q for w in ["describe","what is this","tell me about","about dataset",
                             "what kind","what type of data","overview","summarize","what does"]):
        return describe_dataset()

    # ── Shape ────────────────────────────────────────────────────────────────
    if any(w in q for w in ["how many rows","row count","number of rows","total rows"]):
        return f"📋 Your dataset has **{df.shape[0]:,} rows**."
    if any(w in q for w in ["how many columns","column count","number of columns","total columns"]):
        return f"📊 Your dataset has **{df.shape[1]} columns**: `{'`, `'.join(all_cols)}`"
    if any(w in q for w in ["shape","dimensions","size of dataset"]):
        return f"📐 Shape: **{df.shape[0]:,} rows × {df.shape[1]} columns**"
    if any(w in q for w in ["list columns","what columns","column names","show columns","all columns"]):
        return (f"**Numeric ({len(num_cols)}):** `{', '.join(num_cols) or 'None'}`\n\n"
                f"**Categorical ({len(cat_cols)}):** `{', '.join(cat_cols) or 'None'}`")

    # ── Missing ───────────────────────────────────────────────────────────────
    if any(w in q for w in ["missing","null","nan","empty","incomplete"]):
        if col:
            n = df[col].isnull().sum()
            return (f"✅ **'{col}'** has no missing values." if n==0
                    else f"⚠️ **'{col}'** has **{n} missing values** ({n/len(df)*100:.1f}%).")
        total = df.isnull().sum().sum()
        if total == 0: return "✅ No missing values anywhere!"
        lines = [f"- **{c}**: {v} ({v/len(df)*100:.1f}%)" for c,v in df.isnull().sum().items() if v>0]
        return f"⚠️ **{total:,} total missing values:**\n\n" + "\n".join(lines)

    # ── Mean ─────────────────────────────────────────────────────────────────
    if any(w in q for w in ["average","mean","avg"]):
        if col and col in num_cols:
            return f"📊 Average of **'{col}'** = **{df[col].mean():.4f}**"
        if num_cols:
            return "📊 Averages:\n\n" + "\n".join([f"- **{c}**: {df[c].mean():.4f}" for c in num_cols])

    # ── Max ───────────────────────────────────────────────────────────────────
    if any(w in q for w in ["maximum","max","highest","largest"]):
        if col and col in num_cols:
            return f"🔺 Max of **'{col}'** = **{df[col].max()}** (row {df[col].idxmax()})"
        if num_cols:
            return "🔺 Maximums:\n\n" + "\n".join([f"- **{c}**: {df[c].max()}" for c in num_cols])

    # ── Min ───────────────────────────────────────────────────────────────────
    if any(w in q for w in ["minimum","min","lowest","smallest"]):
        if col and col in num_cols:
            return f"🔻 Min of **'{col}'** = **{df[col].min()}** (row {df[col].idxmin()})"
        if num_cols:
            return "🔻 Minimums:\n\n" + "\n".join([f"- **{c}**: {df[c].min()}" for c in num_cols])

    # ── Sum ───────────────────────────────────────────────────────────────────
    if any(w in q for w in ["sum","total"]):
        if col and col in num_cols:
            return f"➕ Sum of **'{col}'** = **{df[col].sum():,.2f}**"

    # ── Median ────────────────────────────────────────────────────────────────
    if "median" in q:
        if col and col in num_cols:
            return f"📊 Median of **'{col}'** = **{df[col].median():.4f}**"
        if num_cols:
            return "📊 Medians:\n\n" + "\n".join([f"- **{c}**: {df[c].median():.4f}" for c in num_cols])

    # ── Std ───────────────────────────────────────────────────────────────────
    if any(w in q for w in ["std","standard deviation","variance"]):
        if col and col in num_cols:
            return f"📉 Std dev of **'{col}'** = **{df[col].std():.4f}**"

    # ── Unique ────────────────────────────────────────────────────────────────
    if any(w in q for w in ["unique","distinct"]):
        if col:
            top5  = df[col].value_counts().head(5)
            lines = [f"- **{k}**: {v}" for k,v in top5.items()]
            return f"🔍 **'{col}'** has **{df[col].nunique()} unique values**. Top 5:\n\n" + "\n".join(lines)

    # ── Most common ───────────────────────────────────────────────────────────
    if any(w in q for w in ["most common","mode","frequent","popular"]):
        if col:
            v = df[col].mode()[0] if not df[col].mode().empty else "N/A"
            n = (df[col]==v).sum()
            return f"📌 Most common in **'{col}'**: **'{v}'** ({n} times, {n/len(df)*100:.1f}%)"

    # ── Correlation ───────────────────────────────────────────────────────────
    if any(w in q for w in ["correlation","correlated","relationship"]):
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            us   = corr.abs().unstack().sort_values(ascending=False)
            us   = us[us < 1.0].drop_duplicates()
            lines = [f"- **{a}** & **{b}**: r = {corr.loc[a,b]:.3f}" for a,b in us.head(5).index]
            return "🔗 Top correlations:\n\n" + "\n".join(lines)

    # ── Duplicates ────────────────────────────────────────────────────────────
    if any(w in q for w in ["duplicate","duplicates","repeated"]):
        n = df.duplicated().sum()
        return ("✅ No duplicates found." if n==0
                else f"⚠️ **{n} duplicate rows** ({n/len(df)*100:.1f}%).")

    # ── Summary (dimensions only) ─────────────────────────────────────────────
    if any(w in q for w in ["summary","statistics","stats"]):
        if col and col in num_cols:
            d = df[col].describe()
            return (f"📊 **{col}** stats:\n\n"
                    f"- Count: **{d['count']:.0f}**  |  Mean: **{d['mean']:.4f}**\n"
                    f"- Std: **{d['std']:.4f}**  |  Min: **{d['min']:.4f}**  |  Max: **{d['max']:.4f}**\n"
                    f"- 25%: **{d['25%']:.4f}**  |  Median: **{d['50%']:.4f}**  |  75%: **{d['75%']:.4f}**")
        return describe_dataset()

    # ── Skewness ──────────────────────────────────────────────────────────────
    if any(w in q for w in ["skew","skewness"]):
        if col and col in num_cols:
            s = df[col].skew()
            d = "normal" if abs(s)<0.5 else ("right-skewed" if s>0 else "left-skewed")
            return f"📊 **'{col}'** skewness = **{s:.4f}** → {d}"
        if num_cols:
            return "📊 Skewness:\n\n" + "\n".join([f"- **{c}**: {df[c].skew():.3f}" for c in num_cols])

    # ── Outliers ──────────────────────────────────────────────────────────────
    if any(w in q for w in ["outlier","outliers","anomaly","extreme"]):
        if col and col in num_cols:
            Q1,Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            n_out = ((df[col] < Q1-1.5*(Q3-Q1))|(df[col] > Q3+1.5*(Q3-Q1))).sum()
            return (f"🔍 **{n_out} outliers** in **'{col}'** (IQR method).\n"
                    f"Range: **{Q1-1.5*(Q3-Q1):.2f}** → **{Q3+1.5*(Q3-Q1):.2f}**")
        return "→ Go to **🔎 Outlier Detection** page to detect and handle outliers."

    # ── Data type ─────────────────────────────────────────────────────────────
    if any(w in q for w in ["data type","dtype","type of"]):
        if col: return f"🔠 **'{col}'** type: **{df[col].dtype}**"

    # ── Top N ─────────────────────────────────────────────────────────────────
    m = re.search(r'top\s+(\d+)', q)
    if m:
        n = int(m.group(1))
        if col and col in num_cols:
            top = df.nlargest(n, col)[all_cols[:5]]
            return f"🏆 Top **{n}** rows by **'{col}'**:\n\n{top.to_markdown(index=False)}"

    # ── What topic / what about ───────────────────────────────────────────────
    if any(w in q for w in ["what is","what kind","topic","what about","what does this"]):
        return describe_dataset()
    
    # ── Fallback (Groq AI) ─────────────────────────────────────
        # ── Gemini AI Fallback ─────────────────────────────────────

    try:

        # Optimized dataset summary
        summary = df.describe().to_string()

        sample = df.head(5).to_string()

        # Ask Gemini AI
        ai_reply = get_ai_response(
            all_cols,
            sample,
            summary,
            q_raw
        )

        return ai_reply

    except Exception as e:

        return (
            f"❌ Gemini AI Error: {str(e)}\n\n"
            "Try asking:\n"
            "- Describe the dataset\n"
            "- Average of [column]\n"
            "- Missing values in [column]\n"
            "- Show trends in the dataset\n"
            "- Any anomalies?\n"
        )
    

    # # ── Fallback ──────────────────────────────────────────────────────────────
    # col_hint = f" (found column **'{col}'** in your question)" if col else ""
      
    # return (
    #     f"🤔 I couldn't fully parse that{col_hint}. Try:\n\n"
    #     "- *Describe the dataset*\n"
    #     "- *Average / max / min / sum / median of [column]*\n"
    #     "- *How many missing values in [column]?*\n"
    #     "- *Unique values in [column]*\n"
    #     "- *Top correlations*\n"
    #     "- *Any duplicates?*\n"
    #     "- *Any outliers in [column]?*\n\n"
    #     f"Columns: `{'`, `'.join(all_cols[:6])}{'...' if len(all_cols)>6 else ''}`"
    # )

# ── Layout ────────────────────────────────────────────────────────────────────
main_col, side_col = st.columns([3,1])

with side_col:
    st.markdown('<div class="section-title">Quick Ask</div>', unsafe_allow_html=True)
    quick = [
        "Describe the dataset",
        "How many rows and columns?",
        "List all column names",
        "How many missing values?",
        "Average of all columns",
        "Top correlations",
        "Any duplicates?",
    ]
    if num_cols: quick.append(f"Max {num_cols[0]}?")
    if cat_cols: quick.append(f"Most common {cat_cols[0]}?")

    for qn in quick:
        if st.button(qn, use_container_width=True, key=f"q_{qn}"):
            st.session_state["chat_history"].append({"role":"user","content":qn})
            st.session_state["chat_history"].append({"role":"assistant","content":answer(qn)})
            st.rerun()

    st.markdown('<br>', unsafe_allow_html=True)
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

with main_col:
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state["chat_history"]:
        with st.chat_message("assistant"):
            topic = guess_dataset_topic()
            topic_str = f"Looks like a **{topic}** dataset! " if topic else ""
            st.markdown(
                f"👋 Hi! I'm your **DataSense AI Assistant**.\n\n"
                f"{topic_str}Loaded: **{filename}** — "
                f"**{df.shape[0]:,} rows × {df.shape[1]} columns**\n\n"
                "Try asking: *Describe the dataset* or *What is this data about?*"
            )

    user_input = st.chat_input("Ask anything about your data...")
    if user_input:
        st.session_state["chat_history"].append({"role":"user","content":user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner(""):
                reply = answer(user_input)
            st.markdown(reply)
            st.session_state["chat_history"].append({"role":"assistant","content":reply})
