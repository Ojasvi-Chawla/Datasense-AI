import streamlit as st
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.styles import inject_css, sidebar_dataset_info, page_header, stat_card

st.set_page_config(page_title="Clean · DataSense", page_icon="🧹", layout="wide")
inject_css()
sidebar_dataset_info()

page_header("🧹", "Clean Data", "Handle missing values, duplicates, and data type conversions")
st.markdown('<hr>', unsafe_allow_html=True)

if "df" not in st.session_state or st.session_state["df"] is None:
    st.warning("⚠️ No data loaded. Go to **Upload** first."); st.stop()

if "df_clean" not in st.session_state:
    st.session_state["df_clean"] = st.session_state["df"].copy()

df = st.session_state["df_clean"]
num_cols = df.select_dtypes(include=np.number).columns.tolist()

c1,c2,c3 = st.columns(3)
c1.markdown(stat_card("Missing Values", f"{df.isnull().sum().sum():,}", f"{df.isnull().sum().sum()/df.size*100:.1f}% of cells"), unsafe_allow_html=True)
c2.markdown(stat_card("Duplicate Rows", f"{df.duplicated().sum():,}", "exact row matches"), unsafe_allow_html=True)
c3.markdown(stat_card("Dataset Shape",  f"{df.shape[0]:,} × {df.shape[1]}", "rows × columns"), unsafe_allow_html=True)

st.markdown('<hr>', unsafe_allow_html=True)

tab1,tab2,tab3,tab4 = st.tabs(["❓  Missing Values","🔁  Duplicates","🔠  Data Types","✅  Final Dataset"])

# ── Tab 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    missing = df.isnull().sum(); missing = missing[missing > 0]
    if missing.empty:
        st.success("🎉 No missing values!")
    else:
        miss_df = pd.DataFrame({
            "Column": missing.index,
            "Missing": missing.values,
            "Missing %": (missing.values / len(df) * 100).round(2)
        })
        st.dataframe(miss_df, use_container_width=True)
        st.markdown('<br>', unsafe_allow_html=True)

        col_a, col_b = st.columns([1,1])
        with col_a:
            fill_col = st.selectbox("Column to fix", missing.index.tolist())
            strategy = st.radio("Fill Strategy", [
                "Mean","Median","Mode","Custom Value",
                "KNN Imputer (ML)","Drop Rows","Forward Fill","Backward Fill"
            ])
        with col_b:
            custom_val = None
            if strategy == "Custom Value":
                custom_val = st.text_input("Enter value")
            st.markdown('<br>', unsafe_allow_html=True)
            if st.button("✅  Apply to this Column", use_container_width=True):
                try:
                    if strategy == "Mean":      df[fill_col] = df[fill_col].fillna(df[fill_col].mean())
                    elif strategy == "Median":  df[fill_col] = df[fill_col].fillna(df[fill_col].median())
                    elif strategy == "Mode":    df[fill_col] = df[fill_col].fillna(df[fill_col].mode()[0])
                    elif strategy == "Custom Value":
                        try:    df[fill_col] = df[fill_col].fillna(float(custom_val))
                        except: df[fill_col] = df[fill_col].fillna(custom_val)
                    elif strategy == "KNN Imputer (ML)":
                        if fill_col not in num_cols: st.error("KNN works on numeric only.")
                        else:
                            imp = KNNImputer(n_neighbors=5)
                            df[num_cols] = pd.DataFrame(imp.fit_transform(df[num_cols]), columns=num_cols, index=df.index)
                    elif strategy == "Drop Rows":     df = df.dropna(subset=[fill_col])
                    elif strategy == "Forward Fill":  df[fill_col] = df[fill_col].ffill()
                    elif strategy == "Backward Fill": df[fill_col] = df[fill_col].bfill()
                    st.session_state["df_clean"] = df
                    st.success(f"✅ Applied '{strategy}' to **{fill_col}**"); st.rerun()
                except Exception as e: st.error(f"❌ {e}")

        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Bulk Fix All Columns</div>', unsafe_allow_html=True)
        bulk = st.selectbox("Strategy", ["Mean (num) + Mode (cat)","Median (num) + Mode (cat)","Drop all rows with any null"])
        if st.button("🔥  Apply to ALL Missing Columns", use_container_width=True):
            if "Drop" in bulk:
                df = df.dropna()
            else:
                use_mean = "Mean" in bulk
                for col in df.columns:
                    if df[col].isnull().sum() > 0:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col] = df[col].fillna(df[col].mean() if use_mean else df[col].median())
                        elif not df[col].mode().empty:
                            df[col] = df[col].fillna(df[col].mode()[0])
            st.session_state["df_clean"] = df
            st.success("✅ All columns fixed!"); st.rerun()

# ── Tab 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    n_dup = df.duplicated().sum()
    if n_dup == 0:
        st.success("🎉 No duplicate rows!")
    else:
        st.warning(f"⚠️ **{n_dup}** duplicate rows found.")
        st.dataframe(df[df.duplicated()].head(20), use_container_width=True)
        if st.button("🗑️  Remove Duplicates", use_container_width=True):
            df = df.drop_duplicates()
            st.session_state["df_clean"] = df
            st.success(f"✅ Removed {n_dup} rows."); st.rerun()

# ── Tab 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)
    with col_a:
        col_ch = st.selectbox("Column", df.columns.tolist())
        st.info(f"Current type: **{df[col_ch].dtype}**")
    with col_b:
        new_type = st.selectbox("Convert to", ["int64","float64","str (object)","datetime","bool"])
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🔄  Convert", use_container_width=True):
            try:
                if new_type == "int64":       df[col_ch] = pd.to_numeric(df[col_ch], errors="coerce").astype("Int64")
                elif new_type == "float64":   df[col_ch] = pd.to_numeric(df[col_ch], errors="coerce")
                elif new_type == "str (object)": df[col_ch] = df[col_ch].astype(str)
                elif new_type == "datetime":  df[col_ch] = pd.to_datetime(df[col_ch], errors="coerce")
                elif new_type == "bool":      df[col_ch] = df[col_ch].astype(bool)
                st.session_state["df_clean"] = df
                st.success(f"✅ Converted!"); st.rerun()
            except Exception as e: st.error(f"❌ {e}")

# ── Tab 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    c1,c2,c3 = st.columns(3)
    c1.metric("Rows",            df.shape[0])
    c2.metric("Remaining Nulls", df.isnull().sum().sum())
    c3.metric("Duplicates",      df.duplicated().sum())
    st.dataframe(df, use_container_width=True, height=350)

    st.session_state["df_clean"] = df
    st.session_state["df"] = df

    col1,col2 = st.columns(2)
    with col1:
        st.download_button("⬇️  Download Cleaned CSV",
                           data=df.to_csv(index=False).encode("utf-8"),
                           file_name="cleaned_data.csv", mime="text/csv",
                           use_container_width=True)
    with col2:
        if st.button("🔄  Reset to Original", use_container_width=True):
            st.session_state["df_clean"] = st.session_state["df"].copy()
            st.success("Reset!"); st.rerun()
