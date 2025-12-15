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

# 2. CSS OVERRIDES (THE "PREMIUM" LOOK)
st.markdown("""
    <style>
    /* IMPORT "SEXY" FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;500;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

    /* GLOBAL RESET */
    * {
        font-family: 'Rajdhani', sans-serif;
    }

    /* PITCH BLACK SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #050505 !important; /* Almost black, slight warm tint */
        border-right: 1px solid #222;
    }
    
    /* SIDEBAR TEXT */
    [data-testid="stSidebar"] * {
        color: #888888 !important;
        font-size: 14px;
    }
    
    /* INPUT FIELDS (Stealth Mode) */
    .stTextInput input {
        background-color: #111 !important;
        color: #ddd !important;
        border: 1px solid #333 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 12px;
    }
    
    /* BUTTON STYLING (Sharp & Aggressive) */
    .stButton button {
        background-color: #000 !important;
        color: #fff !important;
        border: 1px solid #fff !important;
        border-radius: 0px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #fff !important;
        color: #000 !important;
        box-shadow: 0 0 10px rgba(255,255,255,0.5);
    }

    /* REMOVE BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}

    /* TYPOGRAPHY OVERHAUL */
    h1 {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #ffffff;
        font-size: 3.5rem;
        margin-bottom: 0px;
    }
    h3 {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 18px;
        letter-spacing: 4px; /* Wide spacing looks expensive */
        border-left: none;
        color: #666;
        margin-top: 30px;
    }
    
    /* DATA TABLES (The "Space Mono" Look) */
    .stDataFrame {
        font-family: 'Space Mono', monospace !important;
        font-size: 12px;
    }
    div[data-testid="stDataFrame"] > div {
        border: 1px solid #222;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.markdown("<h2 style='color: #fff !important; letter-spacing: 3px;'>IRONGATE</h2>", unsafe_allow_html=True)
    st.caption("QUANTITATIVE RESEARCH")
    
    st.markdown("---")
    
    st.markdown("**CLIENT PORTAL**")
    email_input = st.text_input("ACCESS KEY / EMAIL", placeholder="USR-8821...")
    
    if st.button("AUTHENTICATE"):
        if email_input:
            st.success("CREDENTIALS VERIFIED.")
        else:
            st.warning("ACCESS DENIED.")
            
    st.markdown("---")
    st.markdown("""
        <div style='font-size: 10px; color: #444; font-family: "Space Mono";'>
        SERVER: NY-4<br>
        UPTIME: 99.99%<br>
        SECURE CONNECTION
        </div>
    """, unsafe_allow_html=True)

# 4. MAIN DASHBOARD
col1, col2 = st.columns([5, 1])
with col1:
    st.title("IRONGATE EQUITY")
    st.markdown("""
        <div style='font-family: "Space Mono", monospace; font-size: 10px; color: #666; letter-spacing: 1px; margin-top: -10px;'>
        INSTITUTIONAL SCREENER // V4.1 // LIVE
        </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("SYNC"):
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
st.markdown("### INDIA / NSE")
df_in = load_data("IN_rankings.csv")

if df_in is not None:
    top = df_in.iloc[0]
    
    # Custom "Glass" Metric Cards
    def metric_card(label, value):
        st.markdown(f"""
        <div style="background-color: #0a0a0a; padding: 20px; border-left: 2px solid #fff; margin-bottom: 10px;">
            <p style="color: #666; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; margin: 0; font-family: 'Rajdhani';">{label}</p>
            <p style="color: #fff; font-size: 28px; font-weight: 300; margin: 5px 0 0 0; font-family: 'Space Mono'; letter-spacing: -1px;">{value}</p>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("TOP CONVICTION", top['Ticker'])
    with c2: metric_card("ALPHA SCORE", f"{top['Alpha_Score']}")
    with c3: metric_card("RSI INDEX", top['RSI'])
    with c4: metric_card("VALUATION (P/E)", top['PE_Ratio'])
    
    # Sleek Table
    st.dataframe(
        df_in.style.background_gradient(subset=['Alpha_Score'], cmap='Greens', vmin=0, vmax=100)
             .format("{:.2f}", subset=['Close', 'RSI', 'PE_Ratio', 'Margins']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("NO SIGNAL.")

st.markdown("<br>", unsafe_allow_html=True)

# --- US SECTION ---
st.markdown("### USA / NYSE")
df_us = load_data("US_rankings.csv")

if df_us is not None:
    top = df_us.iloc[0]
    
    u1, u2, u3, u4 = st.columns(4)
    with u1: metric_card("TOP CONVICTION", top['Ticker'])
    with u2: metric_card("ALPHA SCORE", f"{top['Alpha_Score']}")
    with u3: metric_card("RSI INDEX", top['RSI'])
    with u4: metric_card("VALUATION (P/E)", top['PE_Ratio'])
    
    st.dataframe(
        df_us.style.background_gradient(subset=['Alpha_Score'], cmap='Greens', vmin=0, vmax=100)
             .format("{:.2f}", subset=['Close', 'RSI', 'PE_Ratio', 'Margins']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("NO SIGNAL.")
