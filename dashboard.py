import streamlit as st
import pandas as pd
import os
from github import Github

# --- PAGE SETUP ---
st.set_page_config(page_title="IronGate Research", layout="wide")
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .stDataFrame {border: 1px solid #333;}
    </style>
    """, unsafe_allow_html=True)

# --- TITLE (REMOVED STRATEGY LINE) ---
st.title("IRONGATE | EQUITY MONITOR")

# --- SIDEBAR SUBSCRIPTION SYSTEM ---
with st.sidebar:
    st.header(" Weekly Brief")
    with st.form("sub_form", clear_on_submit=True):
        email = st.text_input("Enter Email Address")
        submitted = st.form_submit_button("Subscribe")
        
        if submitted and "@" in email:
            # TRY TO SAVE TO GITHUB (PERSISTENT)
            try:
                # 1. Connect to Repo
                token = os.environ.get("GITHUB_TOKEN") # Must be in Secrets
                g = Github(token)
                repo = g.get_user().get_repo("AI-Stock-Ranker") # YOUR REPO NAME HERE
                
                # 2. Get existing file
                try:
                    contents = repo.get_contents("subscribers.csv")
                    existing_data = pd.read_csv(pd.compat.StringIO(contents.decoded_content.decode()))
                    
                    if email not in existing_data['email'].values:
                        # Append new email
                        new_row = pd.DataFrame({"email": [email]})
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        
                        # Update file on GitHub
                        repo.update_file(contents.path, f"Add subscriber {email}", updated_df.to_csv(index=False), contents.sha)
                        st.success("✅ Subscribed successfully!")
                    else:
                        st.info("You are already subscribed.")
                
                except:
                    # Create file if it doesn't exist
                    new_df = pd.DataFrame({"email": [email]})
                    repo.create_file("subscribers.csv", "Create subscribers file", new_df.to_csv(index=False))
                    st.success("✅ Subscribed successfully!")

            except Exception as e:
                # FALLBACK: LOCAL SAVE (If no Github token)
                # Note: This resets on app reboot, strictly for testing
                try:
                    if os.path.exists("subscribers.csv"):
                        df = pd.read_csv("subscribers.csv")
                    else:
                        df = pd.DataFrame(columns=["email"])
                    
                    if email not in df["email"].values:
                        new_row = pd.DataFrame({"email": [email]})
                        df = pd.concat([df, new_row], ignore_index=True)
                        df.to_csv("subscribers.csv", index=False)
                        st.success("✅ Added (Local Only)")
                    else:
                        st.info("Already in list")
                except:
                    st.error("Could not save email.")

# --- MAIN DASHBOARD LOGIC ---
if st.button("SYNC DATA"):
    st.rerun()

tab1, tab2, tab3 = st.tabs(["🇺🇸 USA", "🇮🇳 INDIA", "🇬🇧 UK"])

def render_tab(filename, currency):
    if not os.path.exists(filename):
        st.warning(f"Waiting for data... ({filename})")
        return

    try:
        df = pd.read_csv(filename)
        
        # Check for data match
        if 'Blend_Score' not in df.columns:
            st.error("⚠️ Data Mismatch: Old file detected.")
            return

        # Top Pick Metrics
        top = df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top Pick", top['Ticker'])
        c2.metric("Blend Score", f"{top['Blend_Score']}/100")
        c3.metric("Proj. Upside", f"{top['SARIMA_Forecast_5D']}%")
        c4.metric("Valuation", f"{top['PE_Ratio']} P/E")
        
        # FULL TABLE WITH SORTING
        # use_container_width=True makes it pretty
        # Standard Streamlit dataframes allow clicking headers to sort!
        st.dataframe(
            df.style.background_gradient(subset=['Blend_Score'], cmap='Greens'),
            use_container_width=True, 
            hide_index=True,
            height=600 # Makes the table taller to see more stocks
        )
        st.caption(f"Showing {len(df)} stocks based on available data.")

    except Exception as e:
        st.error(f"Error loading data: {e}")

# Load the NEW filenames
with tab1: render_tab("US_Market_Data.csv", "$")
with tab2: render_tab("IN_Market_Data.csv", "₹")
with tab3: render_tab("UK_Market_Data.csv", "£")

