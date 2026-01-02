import streamlit as st
import pandas as pd
import os
from github import Github

# --- PAGE CONFIG ---
st.set_page_config(page_title="IronGate Research", layout="wide")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .stDataFrame {border: 1px solid #333;}
    </style>
    """, unsafe_allow_html=True)

st.title("IRONGATE | EQUITY MONITOR")

# --- SIDEBAR SUBSCRIPTION (FINAL FIX) ---
with st.sidebar:
    st.header("📬 Weekly Brief")
    with st.form("sub_form", clear_on_submit=True):
        email = st.text_input("Enter Email Address")
        submitted = st.form_submit_button("Subscribe")
        
        if submitted and "@" in email:
            try:
                # 1. READ TOKEN
                if "GITHUB_TOKEN" not in st.secrets:
                    st.error("❌ Token missing in Secrets.")
                    st.stop()
                
                token = st.secrets["GITHUB_TOKEN"]
                g = Github(token)
                
                # 2. CONNECT TO REPO (Hardcoded to match your screenshot)
                target_repo = "Chakarav/AI-Stock-Ranker" 
                try:
                    repo = g.get_repo(target_repo)
                except:
                    st.error(f"❌ Error: Could not find '{target_repo}'.")
                    st.stop()
                
                # 3. SAVE EMAIL (THE SHA FIX)
                filename = "subscribers.csv"
                try:
                    # A. TRY TO GET EXISTING FILE
                    contents = repo.get_contents(filename)
                    
                    # Read current CSV content
                    existing_data = pd.read_csv(pd.compat.StringIO(contents.decoded_content.decode()))
                    
                    if email not in existing_data['email'].values:
                        # Append new email
                        new_row = pd.DataFrame({"email": [email]})
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        
                        # --- THE FIX IS HERE: Explicitly passing contents.sha ---
                        repo.update_file(
                            path=contents.path, 
                            message=f"Add subscriber {email}", 
                            content=updated_df.to_csv(index=False), 
                            sha=contents.sha  # <--- THIS IS THE KEY!
                        )
                        st.success(f"✅ Subscribed!")
                    else:
                        st.info("You are already subscribed.")
                
                except Exception as e:
                    # B. IF FILE DOES NOT EXIST, CREATE IT (No SHA needed for creation)
                    if "404" in str(e):
                        new_df = pd.DataFrame({"email": [email]})
                        repo.create_file(
                            path=filename, 
                            message="Create subscribers file", 
                            content=new_df.to_csv(index=False)
                        )
                        st.success(f"✅ Subscribed! (Created Database)")
                    else:
                        st.error(f"❌ Error: {e}")

            except Exception as e:
                st.error(f"❌ CRITICAL ERROR: {str(e)}")

# --- DATA TABS ---
if st.button("SYNC DATA"):
    st.rerun()

tab1, tab2, tab3 = st.tabs(["🇺🇸 USA", "🇮🇳 INDIA", "🇬🇧 UK"])

def render_tab(filename, currency):
    if not os.path.exists(filename):
        st.warning(f"Waiting for data... ({filename})")
        return

    try:
        df = pd.read_csv(filename)
        if 'Blend_Score' not in df.columns:
            st.error("⚠️ Data Mismatch: Old file detected.")
            return

        top = df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top Pick", top['Ticker'])
        c2.metric("Blend Score", f"{top['Blend_Score']}/100")
        c3.metric("Proj. Upside", f"{top['SARIMA_Forecast_5D']}%")
        c4.metric("Valuation", f"{top['PE_Ratio']} P/E")
        
        st.dataframe(df.style.background_gradient(subset=['Blend_Score'], cmap='Greens'), use_container_width=True, hide_index=True, height=600)
        st.caption(f"Showing {len(df)} stocks based on available data.")

    except Exception as e:
        st.error(f"Error loading data: {e}")

with tab1: render_tab("US_Market_Data.csv", "$")
with tab2: render_tab("IN_Market_Data.csv", "₹")
with tab3: render_tab("UK_Market_Data.csv", "£")
