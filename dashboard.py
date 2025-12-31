import streamlit as st
import pandas as pd
import os
from github import Github

st.set_page_config(page_title="IronGate Research", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .stDataFrame {border: 1px solid #333;}
    </style>
    """, unsafe_allow_html=True)

st.title("IRONGATE | EQUITY MONITOR")
st.markdown("**GLOBAL SCREENER** | STRATEGY: `BLEND` + `SARIMA`")

if st.button("SYNC DATA"):
    st.rerun()

tab1, tab2, tab3 = st.tabs(["🇺🇸 USA", "🇮🇳 INDIA", "🇬🇧 UK"])

def render_tab(filename, currency):
    if not os.path.exists(filename):
        st.warning("Data not available.")
        return

    try:
        df = pd.read_csv(filename)
        
        # ERROR PREVENTION: Check if new columns exist
        if 'Blend_Score' not in df.columns:
            st.error("⚠️ Data Mismatch: This file is from the old version.")
            st.info("The system is updating. Please wait for the next scheduled run.")
            st.dataframe(df) # Show old data anyway
            return

        # Show New Metrics
        top = df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top Pick", top['Ticker'])
        c2.metric("Blend Score", f"{top['Blend_Score']}/100")
        c3.metric("Proj. Upside", f"{top['SARIMA_Forecast_5D']}%")
        c4.metric("Valuation", f"{top['PE_Ratio']} P/E")
        
        st.dataframe(
            df.style.background_gradient(subset=['Blend_Score'], cmap='Greens'),
            use_container_width=True, hide_index=True
        )
    except Exception as e:
        st.error(f"Error loading data: {e}")

with tab1: render_tab("US_rankings.csv", "$")
with tab2: render_tab("IN_rankings.csv", "₹")
with tab3: render_tab("UK_rankings.csv", "£")
