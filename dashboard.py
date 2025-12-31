import streamlit as st
import pandas as pd
import os
from github import Github

# PAGE CONFIG
st.set_page_config(page_title="IronGate Global", layout="wide")

# CSS
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .stDataFrame {border: 1px solid #333;}
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR (Keep your existing subscription code here if you want)
st.sidebar.title("IronGate Global")
st.sidebar.info("Markets: US | UK | INDIA")

# HEADER
st.title("IRONGATE | GLOBAL TERMINAL")
st.markdown("**STRATEGY:** `VALUE_GROWTH_BLEND` + `SARIMA_FORECAST`")
st.markdown("---")

def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return None

# TABS FOR MARKETS
tab1, tab2, tab3 = st.tabs(["🇺🇸 UNITED STATES", "🇮🇳 INDIA", "🇬🇧 UNITED KINGDOM"])

def render_tab(filename, currency):
    df = load_data(filename)
    if df is not None:
        # Metrics
        top = df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top Pick", top['Ticker'])
        c2.metric("Blend Score", f"{top['Blend_Score']}/100")
        c3.metric("Proj. Upside (5D)", f"{top['SARIMA_Forecast_5D']}%")
        c4.metric("Valuation (P/E)", top['PE_Ratio'])
        
        # Color Logic for Forecast
        st.dataframe(
            df.style.background_gradient(subset=['SARIMA_Forecast_5D'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Awaiting Market Data...")

with tab1:
    render_tab("US_rankings.csv", "$")
with tab2:
    render_tab("IN_rankings.csv", "₹")
with tab3:
    render_tab("UK_rankings.csv", "£")

st.markdown("---")
st.caption("CONFIDENTIAL: IronGate Global Research. SARIMA Models are probabilistic, not guaranteed.")
