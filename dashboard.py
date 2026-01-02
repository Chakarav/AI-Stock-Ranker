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

# --- SIDEBAR SUBSCRIPTION (DEBUG MODE) ---
with st.sidebar:
    st.header("📬 Weekly Brief")
    with st.form("sub_form", clear_on_submit=True):
        email = st.text_input("Enter Email Address")
        submitted = st.form_submit_button("Subscribe")
        
        if submitted and "@" in email:
            try:
                # 1. READ TOKEN FROM SECRETS
                if "GITHUB_TOKEN" not in st.secrets:
                    st.error("❌ ERROR: 'GITHUB_TOKEN' not found in Secrets!")
                    st.stop()
                
                token = st.secrets["GITHUB_TOKEN"]
                
                # 2. CONNECT TO GITHUB
                g = Github(token)
                user = g.get_user()
                
                # 3. CONNECT TO REPO (Replace 'AI-Stock-Ranker' if your repo name is different)
                repo_name = "AI-Stock-Ranker"
                try:
                    repo = user.get_repo(repo_name)
                except:
                    st.error(f"❌ ERROR: Could not find repo '{repo_name}'. Check spelling!")
                    st.stop()
                
                # 4. SAVE EMAIL
                filename = "subscribers.csv"
                try:
                    contents = repo.get_contents(filename)
                    existing_data = pd.read_csv(pd.compat.StringIO(contents.decoded_content.decode()))
                    
                    if email not in existing_data['email'].values:
                        new_row = pd.DataFrame({"email": [email]})
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        repo.update_file(contents.path, f"Add subscriber {email}", updated_df.to_csv(index=False), contents.sha)
                        st.success(f"✅ Subscribed! (Saved to {filename})")
                    else:
                        st.info("You are already subscribed.")
                
                except:
                    # File doesn't exist yet, create it
                    new_df = pd.DataFrame({"email": [email]})
                    repo.create_file(filename, "Create subscribers file", new_df.to_csv(index=False))
                    st.success(f"✅ Subscribed! (Created {filename})")

            except Exception as e:
                # THIS WILL SHOW US THE REAL ERROR
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
