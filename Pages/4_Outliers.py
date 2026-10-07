import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
from sklearn.ensemble import IsolationForest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header, stat_card, apply_plotly_style

st.set_page_config(page_title="Outliers · DataSense", page_icon="🔎", layout="wide")
inject_css()
sidebar_dataset_info()

page_header("🔎", "Outlier Detection", "Detect and handle anomalies using statistical & ML methods")
st.markdown('<hr>', unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No data loaded. Go to **Upload** first."); st.stop()

df = st.session_state["df"].copy()
num_cols = df.select_dtypes(include=np.number).columns.tolist()
if not num_cols:
    st.error("No numeric columns found."); st.stop()

col_a, col_b = st.columns([1,2])
with col_a:
    col_select = st.selectbox("Numeric Column", num_cols)
with col_b:
    method = st.radio("Detection Method",
                      ["IQR (Box Plot)","Z-Score","Isolation Forest"],
                      horizontal=True)

# Settings
if method == "Z-Score":
    threshold = st.slider("Z-Score Threshold", 1.0, 5.0, 3.0, 0.1)
elif method == "Isolation Forest":
    contamination = st.slider("Expected Outlier %", 0.01, 0.30, 0.05)

st.markdown('<hr>', unsafe_allow_html=True)

# ── Detect ────────────────────────────────────────────────────────────────────
col_filled = df[col_select].fillna(df[col_select].median())
outlier_mask = pd.Series(False, index=df.index)

if method == "IQR (Box Plot)":
    Q1, Q3 = col_filled.quantile(0.25), col_filled.quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
    outlier_mask = (col_filled < lower) | (col_filled > upper)
    st.info(f"📐 IQR = **{IQR:.3f}**  |  Valid range: **{lower:.3f}** → **{upper:.3f}**")

elif method == "Z-Score":
    z_arr = np.abs(stats.zscore(col_filled.to_numpy()))          # ✅ fixed
    outlier_mask = pd.Series(z_arr > threshold, index=df.index)
    st.info(f"📊 Values with |Z| > **{threshold}** are outliers. Max Z in this column: **{z_arr.max():.2f}**")

elif method == "Isolation Forest":
    iso  = IsolationForest(contamination=contamination, random_state=42)
    pred = iso.fit_predict(col_filled.to_numpy().reshape(-1,1))
    outlier_mask = pd.Series(pred == -1, index=df.index)
    st.info(f"🤖 Isolation Forest flagged ~**{contamination*100:.0f}%** as outliers.")

n_out = int(outlier_mask.sum())

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
c1.markdown(stat_card("Total Rows",     f"{len(df):,}",          ""), unsafe_allow_html=True)
c2.markdown(stat_card("Outliers Found", f"{n_out}",              f"{n_out/len(df)*100:.1f}% of rows"), unsafe_allow_html=True)
c3.markdown(stat_card("Clean Rows",     f"{len(df)-n_out:,}",    "remaining after removal"), unsafe_allow_html=True)
c4.markdown(stat_card("Column Mean",    f"{df[col_select].mean():.2f}", f"median: {df[col_select].median():.2f}"), unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────────────────────
plot_df = df[[col_select]].copy()
plot_df["Type"] = np.where(outlier_mask, "Outlier ⚠️","Normal ✅")

tab1, tab2 = st.tabs(["📦  Box Plot","📈  Distribution"])

cmap = {"Outlier ⚠️":"#ef4444","Normal ✅":"#00f5a0"}

with tab1:
    fig = px.box(plot_df, y=col_select, color="Type", points="all",
                 color_discrete_map=cmap,
                 title=f"Box Plot — {col_select}", template="plotly_dark")
    apply_plotly_style(fig)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig2 = px.histogram(plot_df, x=col_select, color="Type", nbins=40,
                        color_discrete_map=cmap, barmode="overlay", marginal="rug",
                        title=f"Distribution — {col_select}", template="plotly_dark")
    apply_plotly_style(fig2)
    st.plotly_chart(fig2, use_container_width=True)

if n_out > 0:
    with st.expander(f"👀  View {n_out} outlier rows"):
        st.dataframe(df[outlier_mask], use_container_width=True)

# ── Handle ────────────────────────────────────────────────────────────────────
st.markdown('<hr>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Handle Outliers</div>', unsafe_allow_html=True)

action = st.radio("Action", [
    "Keep them","Remove outlier rows",
    "Cap at 5th–95th percentile","Replace with Median"
], horizontal=True)

if st.button("✅  Apply Action", use_container_width=False) and action != "Keep them":
    df_r = st.session_state["df"].copy()
    cf   = df_r[col_select].fillna(df_r[col_select].median())

    if method == "IQR (Box Plot)":
        mask2 = (cf < lower) | (cf > upper)
    elif method == "Z-Score":
        z2    = np.abs(stats.zscore(cf.to_numpy()))
        mask2 = pd.Series(z2 > threshold, index=df_r.index)
    else:
        p2    = iso.fit_predict(cf.to_numpy().reshape(-1,1))
        mask2 = pd.Series(p2 == -1, index=df_r.index)

    if action == "Remove outlier rows":
        before = len(df_r); df_r = df_r[~mask2]
        st.success(f"✅ Removed {before-len(df_r)} rows.")
    elif action == "Cap at 5th–95th percentile":
        p5, p95 = df_r[col_select].quantile(0.05), df_r[col_select].quantile(0.95)
        df_r[col_select] = df_r[col_select].clip(p5, p95)
        st.success(f"✅ Capped to [{p5:.2f}, {p95:.2f}]")
    elif action == "Replace with Median":
        med = df_r[col_select].median()
        df_r.loc[mask2, col_select] = med
        st.success(f"✅ Replaced with median ({med:.2f})")

    st.session_state["df"] = df_r
    st.dataframe(df_r.head(20), use_container_width=True)
    st.download_button("⬇️  Download",
                       data=df_r.to_csv(index=False).encode("utf-8"),
                       file_name="no_outliers.csv", mime="text/csv")
