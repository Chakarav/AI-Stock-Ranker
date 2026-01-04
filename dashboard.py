import streamlit as st
import pandas as pd
import os
import io
from github import Github

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="IGT | TERMINAL", layout="wide")

# --- MODERN HEDGE FUND STYLING ---
st.markdown("""
    <style>
        /* IMPORT MODERN FONT */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        /* GLOBAL STYLES */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #e0e0e0;
            background-color: #0e1117;
        }

        /* REMOVE TOP PADDING */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* HEADERS */
        h1 {
            color: #ffffff !important;
            font-weight: 700;
            font-size: 1.8rem !important;
            letter-spacing: -0.5px;
            border-left: 5px solid #00d4ff; /* CYAN ACCENT */
            padding-left: 15px;
        }
        h2, h3 {
            color: #a0a0a0 !important;
            font-weight: 600;
            font-size: 1.1rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* METRIC CARDS - MINIMALIST */
        [data-testid="stMetricValue"] {
            color: #00d4ff !important; /* CYAN ACCENT */
            font-size: 1.8rem !important;
            font-weight: 600;
        }
        [data-testid="stMetricLabel"] {
            color: #666 !important;
            font-size: 0.8rem !important;
            font-weight: 600;
            text-transform: uppercase;
        }

        /* TABS - WIDER SPACING & CLEAN LOOK */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px; /* SPACE BETWEEN TABS */
            background-color: transparent;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: transparent;
            border: none;
            color: #666;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            padding-left: 20px;
            padding-right: 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: transparent !important;
            color: #00d4ff !important; /* CYAN HIGHLIGHT */
            border-bottom: 3px solid #00d4ff;
        }

        /* DATAFRAMES - CLEAN LINES */
        .stDataFrame {
            border: 1px solid #222;
        }
        
        /* BUTTONS - PREMIUM GHOST STYLE */
        .stButton button {
            background-color: transparent;
            color: #00d4ff;
            border: 1px solid #00d4ff;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #00d4ff;
            color: #000;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
        }

        /* SIDEBAR - DARK & SUBTLE */
        [data-testid="stSidebar"] {
            background-color: #0b0d10;
            border-right: 1px solid #222;
        }
        
        /* TEXT INPUTS */
        .stTextInput input {
            background-color: #161b22;
            color: white;
            border: 1px solid #333;
            border-radius: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("IRONGATE TERMINAL")
st.markdown("Global Equity Intelligence & AI Forecasts")
st.markdown("---")

# --- SIDEBAR: SUBSCRIPTION MODULE ---
with st.sidebar:
    st.markdown("### INTELLIGENCE FEED")
    st.caption("Weekly institutional-grade analysis reports.")
    
    with st.form("sub_form", clear_on_submit=True):
        email = st.text_input("ENTER EMAIL ADDRESS")
        submitted = st.form_submit_button("INITIATE ACCESS")
        
        if submitted and "@" in email:
            try:
                # 1. AUTHENTICATE
                if "GITHUB_TOKEN" not in st.secrets:
                    st.error("SYSTEM ERROR: MISSING TOKEN")
                    st.stop()
                
                token = st.secrets["GITHUB_TOKEN"]
                g = Github(token)
                
                # 2. CONNECT TO REPO
                target_repo = "Chakarav/AI-Stock-Ranker" 
                try:
                    repo = g.get_repo(target_repo)
                except:
                    st.error(f"ERROR: REPO '{target_repo}' NOT FOUND")
                    st.stop()
                
                # 3. UPDATE DATABASE
                filename = "subscribers.csv"
                try:
                    contents = repo.get_contents(filename)
                    csv_content = contents.decoded_content.decode()
                    existing_data = pd.read_csv(io.StringIO(csv_content))
                    
                    if email not in existing_data['email'].values:
                        new_row = pd.DataFrame({"email": [email]})
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        
                        repo.update_file(
                            path=contents.path, 
                            message=f"ADD SUBSCRIBER: {email}", 
                            content=updated_df.to_csv(index=False), 
                            sha=contents.sha 
                        )
                        st.success("STATUS: CONFIRMED")
                    else:
                        st.info("STATUS: ACTIVE MEMBER")
                
                except Exception as e:
                    if "404" in str(e):
                        new_df = pd.DataFrame({"email": [email]})
                        repo.create_file(
                            path=filename, 
                            message="INIT DATABASE", 
                            content=new_df.to_csv(index=False)
                        )
                        st.success("STATUS: DATABASE INITIALIZED")
                    else:
                        st.error(f"CRITICAL ERROR: {e}")

            except Exception as e:
                st.error(f"SYSTEM FAILURE: {str(e)}")

# --- MAIN CONTROLS ---
if st.button("SYNC LIVE DATA"):
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# --- MARKET TABS ---
tab1, tab2, tab3 = st.tabs(["US MARKETS", "INDIA MARKETS", "UK MARKETS"])

def render_terminal_tab(filename, currency_symbol):
    if not os.path.exists(filename):
        st.warning(f"SYSTEM: WAITING FOR DATA FEED ({filename})...")
        return

    try:
        df = pd.read_csv(filename)
        if 'Blend_Score' not in df.columns:
            st.error("ERROR: CORRUPTED DATA FILE.")
            return

        # EXTRACT METRICS
        top_stock = df.iloc[0]
        
        # DISPLAY METRICS ROW
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOP TICKER", top_stock['Ticker'])
        c2.metric("COMPOSITE SCORE", f"{top_stock['Blend_Score']}")
        c3.metric("PROJ. UPSIDE", f"{top_stock['SARIMA_Forecast_5D']}%")
        c4.metric("VALUATION", f"{top_stock['PE_Ratio']} P/E")
        
        st.markdown("### MARKET SCANNER RESULTS")
        
        # DATAFRAME CONFIG (DARK THEME TABLE)
        st.dataframe(
            df.style.background_gradient(subset=['Blend_Score'], cmap='mako', vmin=0, vmax=100),
            use_container_width=True, 
            hide_index=True,
            height=600
        )
        st.caption(f"DISPLAYING {len(df)} ASSETS RANKED BY ALGORITHM.")

    except Exception as e:
        st.error(f"READ ERROR: {e}")

# --- RENDER TABS ---
with tab1: render_terminal_tab("US_Market_Data.csv", "$")
with tab2: render_terminal_tab("IN_Market_Data.csv", "₹")
with tab3: render_terminal_tab("UK_Market_Data.csv", "£")
