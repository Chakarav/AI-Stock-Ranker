import streamlit as st
import pandas as pd
import os
from github import Github

# PAGE CONFIG
st.set_page_config(page_title="IronGate Research", layout="wide")

# CSS FOR INSTITUTIONAL LOOK
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 {font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: -1px;}
    h2, h3 {font-family: 'Helvetica Neue', sans-serif; font-weight: 600;}
    .stDataFrame {border: 1px solid #333;}
    .stButton>button {width: 100%; border-radius: 0px; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: NEWSLETTER SUBSCRIPTION ---
st.sidebar.header("IronGate Intelligence")
st.sidebar.caption("Institutional Daily Briefing")

email_input = st.sidebar.text_input("Enter Email Address")

if st.sidebar.button("SUBSCRIBE"):
    if "@" in email_input and "." in email_input:
        try:
            # Connect to GitHub to save email
            token = st.secrets["GITHUB_TOKEN"]
            g = Github(token)
            repo = g.get_user().get_repo("AI-Stock-Ranker") # Ensure this matches your Repo Name
            file = repo.get_contents("subscribers.csv")
            
            # Read & Update
            content = file.decoded_content.decode()
            current_emails = content.splitlines()
            
            if email_input in str(current_emails):
                st.sidebar.warning("Subscriber already registered.")
            else:
                new_content = content + f"\n{email_input}"
                repo.update_file(file.path, f"Add subscriber: {email_input}", new_content, file.sha)
                st.sidebar.success("Subscription Confirmed.")
                
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.error("Invalid email format.")

st.sidebar.markdown("---")
st.sidebar.caption("System Status: ONLINE")

# --- MAIN HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("IRONGATE | EQUITY MONITOR")
    st.markdown("**INSTITUTIONAL SCREENER** | MODEL: `V4_CONVICTION` | FEED: `LIVE`")
with col2:
    if st.button("SYNC DATA"):
        st.rerun()

st.markdown("---")

# LOAD DATA FUNCTION
def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        numeric_cols = df.select_dtypes(include=['float64']).columns
        df[numeric_cols] = df[numeric_cols].round(2)
        return df
    return None

# --- SECTION 1: INDIA MARKET ---
st.subheader("MARKET: INDIA (NSE)")
df_in = load_data("IN_rankings.csv")

if df_in is not None:
    # Key Metrics
    top = df_in.iloc[0]
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
    st.error("NO SIGNAL DETECTED.")

st.markdown("---")

# --- SECTION 2: US MARKET ---
st.subheader("MARKET: USA (S&P 500)")
df_us = load_data("US_rankings.csv")

if df_us is not None:
    # Key Metrics
    top = df_us.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Highest Conviction", top['Ticker'])
    c2.metric("Alpha Score", f"{top['Alpha_Score']}/100")
    c3.metric("RSI Strength", top['RSI'])
    c4.metric("Valuation (P/E)", top['PE_Ratio'])
    
    # Data Table
    st.dataframe(
        df_us.style.background_gradient(subset=['Alpha_Score'], cmap='Greens'), 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.error("NO SIGNAL DETECTED.")

# FOOTER
st.markdown("---")
st.caption("CONFIDENTIAL: For internal research purposes only. IronGate Research.")
