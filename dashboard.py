import streamlit as st
import pandas as pd
import os

# PAGE CONFIG
st.set_page_config(page_title="IronGate Research", layout="wide", page_icon="🏛️")

# CSS FOR INSTITUTIONAL LOOK
st.markdown("""
    <style>
    /* HIDE STREAMLIT BRANDING */
    .block-container {padding-top: 2rem;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* TYPOGRAPHY */
    h1 {font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: -1px; text-transform: uppercase;}
    h3 {font-family: 'Helvetica Neue', sans-serif; font-weight: 600; text-transform: uppercase; font-size: 16px; border-left: 5px solid #000; padding-left: 10px;}
    
    /* DATAFRAME STYLE */
    .stDataFrame {border: 1px solid #e0e0e0;}
    </style>
    """, unsafe_allow_html=True)

# HEADER
col1, col2 = st.columns([4, 1])
with col1:
    st.title("IRONGATE | EQUITY MONITOR")
    st.caption("INSTITUTIONAL SCREENER | MODEL: `V4_CONVICTION` | FEED: `LIVE`")
with col2:
    if st.button("↻ SYNC DATA"):
        st.rerun()

st.markdown("---")

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        # Clean rounding for display
        numeric_cols = df.select_dtypes(include=['float64']).columns
        df[numeric_cols] = df[numeric_cols].round(2)
        return df
    return None

# --- INDIA SECTION ---
st.subheader("MARKET: INDIA (NSE)")
df_in = load_data("IN_rankings.csv")

if df_in is not None:
    top = df_in.iloc[0]
    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Highest Conviction", top['Ticker'])
    c2.metric("Alpha Score", f"{top['Alpha_Score']}/100")
    c3.metric("RSI Strength", top['RSI'])
    c4.metric("Valuation (P/E)", top['PE_Ratio'])
    
    # Data Table
    st.dataframe(
        df_in.style.background_gradient(subset=['Alpha_Score'], cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("NO SIGNAL DETECTED. CHECK DATA FEED.")

st.markdown("---")

# --- US SECTION ---
st.subheader("MARKET: USA (S&P 500)")
df_us = load_data("US_rankings.csv")

if df_us is not None:
    top = df_us.iloc[0]
    # Metrics Row
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("Highest Conviction", top['Ticker'])
    u2.metric("Alpha Score", f"{top['Alpha_Score']}/100")
    u3.metric("RSI Strength", top['RSI'])
    u4.metric("Valuation (P/E)", top['PE_Ratio'])
    
    # Data Table
    st.dataframe(
        df_us.style.background_gradient(subset=['Alpha_Score'], cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("NO SIGNAL DETECTED. CHECK DATA FEED.")
