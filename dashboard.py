import streamlit as st
import pandas as pd
import os
import io
from github import Github

st.set_page_config(page_title="IGT | TERMINAL", layout="wide")

st.markdown("""
    <style>
        /* IMPORT TERMINAL FONT */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

        /* GLOBAL STYLES */
        html, body, [class*="css"] {
            font-family: 'Roboto Mono', monospace !important;
            color: #e0e0e0; 
        }

        /* BACKGROUND */
        .stApp {
            background-color: #000000;
        }

        /* HEADERS */
        h1, h2, h3 {
            color: #ff9900 !important; /* BLOOMBERG AMBER */
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }

        /* DATAFRAMES */
        .stDataFrame {
            border: 1px solid #333;
        }

        /* METRIC CARDS */
        [data-testid="stMetricValue"] {
            color: #ff9900 !important;
            font-size: 1.5rem !important;
        }
        [data-testid="stMetricLabel"] {
            color: #888 !important;
            text-transform: uppercase;
            font-size: 0.8rem !important;
        }

        /* BUTTONS (SQUARE & SHARP) */
        .stButton button {
            background-color: #1a1a1a;
            color: #ff9900;
            border: 1px solid #ff9900;
            border-radius: 0px !important;
            text-transform: uppercase;
            font-weight: bold;
            transition: all 0.2s;
        }
        .stButton button:hover {
            background-color: #ff9900;
            color: #000000;
            border: 1px solid #ff9900;
        }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 5px;
            background-color: #000;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: #111;
            border: 1px solid #333;
            border-radius: 0px !important;
            color: #666;
            text-transform: uppercase;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ff9900 !important;
            color: #000 !important;
            font-weight: bold;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("IRONGATE TERMINAL // GLOBAL EQUITIES")
st.markdown("---")

# --- SIDEBAR: SUBSCRIPTION MODULE ---
with st.sidebar:
    st.header("MARKET INTELLIGENCE")
    st.caption("RECEIVE WEEKLY ANALYSIS REPORTS")
    
    with st.form("sub_form", clear_on_submit=True):
        email = st.text_input("ENTER EMAIL TERMINAL")
        submitted = st.form_submit_button("INITIATE SUBSCRIPTION")
        
        if submitted and "@" in email:
            try:
                # 1. AUTHENTICATE
                if "GITHUB_TOKEN" not in st.secrets:
                    st.error("[SYSTEM ERROR]: MISSING AUTH TOKEN")
                    st.stop()
                
                token = st.secrets["GITHUB_TOKEN"]
                g = Github(token)
                
                # 2. CONNECT TO REPO
                target_repo = "Chakarav/AI-Stock-Ranker" 
                try:
                    repo = g.get_repo(target_repo)
                except:
                    st.error(f"[ERROR]: REPO '{target_repo}' NOT FOUND")
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
                        st.success("[STATUS: CONFIRMED]")
                    else:
                        st.info("[STATUS: ALREADY REGISTERED]")
                
                except Exception as e:
                    if "404" in str(e):
                        new_df = pd.DataFrame({"email": [email]})
                        repo.create_file(
                            path=filename, 
                            message="INIT DATABASE", 
                            content=new_df.to_csv(index=False)
                        )
                        st.success("[STATUS: DATABASE CREATED]")
                    else:
                        st.error(f"[CRITICAL ERROR]: {e}")

            except Exception as e:
                st.error(f"[SYSTEM FAILURE]: {str(e)}")

# --- MAIN CONTROLS ---
if st.button("SYNC MARKET DATA"):
    st.rerun()

# --- MARKET TABS ---
tab1, tab2, tab3 = st.tabs(["US MARKETS", "INDIA MARKETS", "UK MARKETS"])

def render_terminal_tab(filename, currency_symbol):
    if not os.path.exists(filename):
        st.warning(f"[SYSTEM]: WAITING FOR DATA FEED ({filename})...")
        return

    try:
        df = pd.read_csv(filename)
        if 'Blend_Score' not in df.columns:
            st.error("[ERROR]: CORRUPTED DATA FILE.")
            return

        # EXTRACT METRICS
        top_stock = df.iloc[0]
        
        # DISPLAY METRICS ROW
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOP TICKER", top_stock['Ticker'])
        c2.metric("COMPOSITE SCORE", f"{top_stock['Blend_Score']}")
        c3.metric("PROJ. UPSIDE", f"{top_stock['SARIMA_Forecast_5D']}%")
        c4.metric("VALUATION (P/E)", f"{top_stock['PE_Ratio']}")
        
        st.markdown("### MARKET SCANNER RESULTS")
        
        # DATAFRAME CONFIG
        st.dataframe(
            df.style.background_gradient(subset=['Blend_Score'], cmap='Greens', vmin=0, vmax=100),
            use_container_width=True, 
            hide_index=True,
            height=600
        )
        st.caption(f"[SYSTEM]: DISPLAYING {len(df)} ASSETS sorted by COMPOSITE SCORE.")

    except Exception as e:
        st.error(f"[READ ERROR]: {e}")

# --- RENDER TABS ---
with tab1: render_terminal_tab("US_Market_Data.csv", "$")
with tab2: render_terminal_tab("IN_Market_Data.csv", "₹")
with tab3: render_terminal_tab("UK_Market_Data.csv", "£")
