import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText

# 1. Page Config
st.set_page_config(page_title="AlphaQuant Dashboard", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
<style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    div[data-testid="stSidebarUserContent"] { padding-top: 2rem; }
    .success-msg { color: #4caf50; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📈 AlphaQuant | Institutional Analytics")

# --- ADMIN NOTIFICATION SYSTEM ---
def notify_admin(new_email):
    """Sends an email to YOU when someone subscribes."""
    try:
        sender = "vishwajeetchakaravarthi@gmail.com"  # YOUR EMAIL
        receiver = "vishwajeetchakaravarthi@gmail.com" # YOUR EMAIL (Send to self)
        # Load password from Streamlit Secrets (safe way)
        password = st.secrets["EMAIL_PASSWORD"] 
        
        msg = MIMEText(f"Hey! A new user wants to join the newsletter.\n\nEmail: {new_email}\n\nAction: Add them to SUBSCRIBERS list in email_bot.py")
        msg['Subject'] = f"🔔 New AlphaQuant Subscriber: {new_email}"
        msg['From'] = sender
        msg['To'] = receiver
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

# 2. Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    market = st.selectbox("Select Market", ["IN", "US"])
    
    st.markdown("---")
    st.header("📬 Daily Newsletter")
    st.write("Get the top 10 picks delivered to your inbox every morning at 8:00 AM.")
    
    # Subscribe Form
    with st.form(key='sub_form'):
        email_input = st.text_input("Enter your email")
        submit = st.form_submit_button("Join Waitlist")
        
        if submit:
            if "@" in email_input:
                # 1. Show success to user immediately
                st.success("✅ Request Sent! You are on the list.")
                st.caption("The Fund Manager will approve your request shortly.")
                
                # 2. Notify Admin (You) quietly
                if "EMAIL_PASSWORD" in st.secrets:
                    notify_admin(email_input)
                else:
                    st.warning("Admin alert not configured (Check Secrets).")
            else:
                st.error("Invalid email address.")

# 3. Load Data (Safe Mode)
@st.cache_data(ttl=0)
def load_data(market):
    try:
        # Load from Root folder
        df = pd.read_csv(f"{market}_rankings.csv")
        return df
    except:
        return pd.DataFrame()

df = load_data(market)

# 4. Main Dashboard
if not df.empty:
    # Identify the correct Score column (handles old/new data formats)
    cols = df.columns.tolist()
    # Priority: Alpha_Score -> Final_Score -> ML_Confidence
    score_col = next((c for c in ['Alpha_Score', 'Final_Score', 'ML_Confidence'] if c in cols), None)
    
    if score_col:
        # --- Top Pick Section ---
        top_stock = df.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("🏆 Top Pick", top_stock['Ticker'])
        col2.metric("Confidence Score", f"{top_stock[score_col]:.0f}/100")
        col3.metric("Current Price", f"{top_stock['Close']:.2f}")
        
        st.markdown("---")
        
        # --- Deep Dive Table ---
        st.subheader(f"📊 Market Opportunities ({market})")
        # Highlight high scores in Green
        st.dataframe(
            df.head(10).style.background_gradient(subset=[score_col], cmap='Greens'),
            use_container_width=True
        )
        
        # --- Charts (Only if extended metrics exist) ---
        if 'PE_Ratio' in cols and 'EV_EBITDA' in cols:
            st.subheader("🔍 Valuation Map")
            fig = px.scatter(
                df, x='PE_Ratio', y=score_col, size='Close', color='EV_EBITDA',
                title="Value (P/E) vs Quality (Alpha Score)",
                labels={'PE_Ratio': 'P/E Ratio (Lower is Better)', score_col: 'AI Score'},
                color_continuous_scale='RdYlGn_r' # Red to Green reversed
            )
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.error(f"Data loaded, but '{score_col}' column is missing. Check CSV.")
else:
    st.info(f"⏳ Waiting for data... The robot runs daily at 8:00 AM.")