import streamlit as st
import pandas as pd
import os

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="IronGate Research",
    layout="wide",
    page_icon="🏛️",
    initial_sidebar_state="expanded"
)

# 2. CSS OVERRIDES (THE "BLACK MODE" FIX)
st.markdown("""
    <style>
    /* IMPORT PROFESSIONAL FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* GLOBAL RESET */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* FORCE SIDEBAR TO BE BLACK */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #333333;
    }
    
    /* SIDEBAR TEXT COLOR */
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    /* INPUT FIELDS (Make them dark) */
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
    }
    
    /* BUTTON STYLING (Minimalist) */
    .stButton button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 0px !important; /* Sharp edges for "Terminal" feel */
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    .stButton button:hover {
        border-color: #ffffff !important;
        color: #ffffff !important;
    }

    /* REMOVE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}

    /* TYPOGRAPHY */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        letter-spacing: -1.5px;
        text-transform: uppercase;
        color: #ffffff;
        font-size: 3rem;
    }
    h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 14px;
        letter-spacing: 1px;
        border-left: 3px solid #ffffff;
        padding-left: 15px;
        color: #cccccc;
    }
    
    /* DATA TABLES (The "Bloomberg" Look) */
    .stDataFrame {
        font-family: 'JetBrains Mono', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR: CLIENT ACCESS
with st.sidebar:
    st.markdown("### IRONGATE RESEARCH")
    st.caption("EST. 2025 | NEW YORK • MUMBAI")
    
    st.markdown("---")
    
    st.markdown("**CLIENT PORTAL**")
    email_input = st.text_input("INSTITUTIONAL EMAIL", placeholder="analyst@fund.com")
    
    if st.button("REQUEST TERMINAL ACCESS"):
        if email_input:
            st.success("REQUEST LOGGED. COMPLIANCE REVIEW PENDING.")
        else:
            st.warning("INVALID CREDENTIALS.")
            
    st.markdown("---")
    st.markdown("""
        <div style='font-size: 10px; color: #666; font-family: "JetBrains Mono";'>
        STATUS: LIVE<br>
        LATENCY: 14ms<br>
        ENCRYPTION: 256-BIT
        </div>
    """, unsafe_allow_html=True)

# 4. MAIN DASHBOARD
col1, col2 = st.columns([5, 1])
with col1:
    st.title("IRONGATE | EQUITY MONITOR")
    st.markdown("""
        <div style='font-family: "JetBrains Mono", monospace; font-size: 12px; color: #888; margin-bottom: 20px;'>
        // SYSTEM_READY<br>
        // MODEL: V4_CONVICTION<br>
        // DATA_STREAM: ACTIVE
        </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("↻ SYNC DATA"):
        st.rerun()

st.markdown("---")

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        numeric_cols = df.select_dtypes(include=['float64']).columns
        df[numeric_cols] = df[numeric_cols].round(2)
        return df
    return None

# --- INDIA SECTION ---
st.markdown("### MARKET: INDIA (NSE)")
df_in = load_data("IN_rankings.csv")

if df_in is not None:
    top = df_in.iloc[0]
    
    # Custom CSS Metric Cards (Dark Mode)
    def metric_card(label, value):
        st.markdown(f"""
        <div style="background-color: #111; padding: 15px; border: 1px solid #333; margin-bottom: 10px;">
            <p style="color: #666; font-size: 11px; text-transform: uppercase; margin: 0;">{label}</p>
            <p style="color: #fff; font-size: 24px; font-weight: 600; margin: 0; font-family: 'JetBrains Mono';">{value}</p>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("HIGHEST CONVICTION", top['Ticker'])
    with c2: metric_card("ALPHA SCORE", f"{top['Alpha_Score']}")
    with c3: metric_card("RSI STRENGTH", top['RSI'])
    with c4: metric_card("VALUATION (P/E)", top['PE_Ratio'])
    
    # Table with Dark Gradient
    st.dataframe(
        df_in.style.background_gradient(subset=['Alpha_Score'], cmap='Greens', vmin=0, vmax=100)
             .format("{:.2f}", subset=['Close', 'RSI', 'PE_Ratio', 'Margins']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("FEED DISCONNECTED.")

st.markdown("<br>", unsafe_allow_html=True)

# --- US SECTION ---
st.markdown("### MARKET: USA (S&P 500)")
df_us = load_data("US_rankings.csv")

if df_us is not None:
    top = df_us.iloc[0]
    
    # Re-use metric cards
    u1, u2, u3, u4 = st.columns(4)
    with u1: metric_card("HIGHEST CONVICTION", top['Ticker'])
    with u2: metric_card("ALPHA SCORE", f"{top['Alpha_Score']}")
    with u3: metric_card("RSI STRENGTH", top['RSI'])
    with u4: metric_card("VALUATION (P/E)", top['PE_Ratio'])
    
    st.dataframe(
        df_us.style.background_gradient(subset=['Alpha_Score'], cmap='Greens', vmin=0, vmax=100)
             .format("{:.2f}", subset=['Close', 'RSI', 'PE_Ratio', 'Margins']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("FEED DISCONNECTED.")
