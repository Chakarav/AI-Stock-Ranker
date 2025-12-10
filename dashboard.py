import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="AlphaQuant Dashboard", layout="wide")

# Custom Styling to make it look pro
st.markdown("""
<style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    div[data-testid="stSidebarUserContent"] { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("📈 AlphaQuant | Institutional Analytics")

# 2. Sidebar with Subscribe Box
with st.sidebar:
    st.header("⚙️ Settings")
    market = st.selectbox("Select Market", ["IN", "US"])
    
    st.markdown("---")
    st.header("📬 Daily Newsletter")
    st.write("Get these top picks in your inbox every morning.")
    
    # The Subscribe Form
    with st.form(key='subscribe_form'):
        email_input = st.text_input("Enter your email")
        submit_button = st.form_submit_button(label='Subscribe')
        
        if submit_button:
            if "@" in email_input:
                st.success("✅ Request Sent!")
                st.info("Since this is an exclusive beta, the Fund Manager will approve your email manually.")
            else:
                st.error("Please enter a valid email.")

# 3. Load Data Function (Safe Mode)
@st.cache_data(ttl=0)
def load_data(market):
    try:
        # Try loading from root
        df = pd.read_csv(f"{market}_rankings.csv")
        return df
    except:
        return pd.DataFrame()

df = load_data(market)

# 4. Main Dashboard Logic
if not df.empty:
    # Safe Column Mapping
    cols = df.columns.tolist()
    score_col = next((c for c in ['Alpha_Score', 'Final_Score', 'ML_Confidence'] if c in cols), None)
    
    if score_col:
        # Top Stock Section
        top_stock = df.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("🏆 Top Pick", top_stock['Ticker'])
        col2.metric("Confidence Score", f"{top_stock[score_col]:.0f}/100")
        col3.metric("Current Price", f"{top_stock['Close']:.2f}")
        
        # Deep Dive Table
        st.subheader(f"📊 Market Opportunities ({market})")
        
        # Formatting for a clean look
        st.dataframe(
            df.head(10).style.background_gradient(subset=[score_col], cmap='Greens'),
            use_container_width=True
        )
        
        # Analysis Chart
        if 'PE_Ratio' in cols and 'EV_EBITDA' in cols:
            st.subheader("🔍 Valuation Map")
            fig = px.scatter(
                df, x='PE_Ratio', y=score_col, size='Close', color='EV_EBITDA',
                title="Value (P/E) vs Quality (Alpha Score)",
                color_continuous_scale='RdYlGn_r' # Red to Green reversed (Lower EV is better)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.error("Data loaded, but score column is missing.")
else:
    st.info(f"⏳ Waiting for data... The robot runs daily at 8:00 AM.")