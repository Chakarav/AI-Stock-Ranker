import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AlphaQuant Institutional", layout="wide")

# Professional CSS (Hide header, clean fonts)
st.markdown("""
<style>
    .block-container {padding-top: 1rem;}
    div[data-testid="stMetricValue"] {font-size: 28px; color: #4caf50;}
    .stDataFrame {border: 1px solid #333;}
</style>
""", unsafe_allow_html=True)

st.title("AlphaQuant | Institutional Analytics")
st.markdown("---")

# Sidebar
market = st.sidebar.selectbox("MARKET DATA", ["IN", "US"])
st.sidebar.markdown("### Newsletter")
email = st.sidebar.text_input("Recipient Email")
if st.sidebar.button("Subscribe"):
    st.sidebar.success("Added to distribution list.")

# Load Data
@st.cache_data(ttl=0)
def load_data(m):
    try:
        return pd.read_csv(f"{m}_rankings.csv")
    except:
        return pd.DataFrame()

df = load_data(market)

if not df.empty:
    top_pick = df.iloc[0]

    # --- ROW 1: HEADLINE METRICS ---
    st.subheader("High Conviction Alpha Pick")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ticker", top_pick['Ticker'])
    c1.caption(f"Price: {top_pick['Close']:.2f}")
    
    c2.metric("Alpha Score", f"{top_pick['Alpha_Score']:.0f}/100")
    c2.caption("Composite Rating")

    c3.metric("Valuation (EV/EBITDA)", f"{top_pick['EV_EBITDA']:.2f}")
    c3.caption("Sector Avg: ~12.0")

    c4.metric("Profit Margin", f"{top_pick['Margins']:.1f}%")
    c4.caption("Net Income / Revenue")

    st.markdown("---")

    # --- ROW 2: DEEP DIVE TABS ---
    tab1, tab2 = st.tabs(["RANKINGS TABLE", "VALUATION MATRIX"])
    
    with tab1:
        st.subheader("Market Opportunities")
        # Format table for readability
        display_df = df[['Ticker', 'Alpha_Score', 'Close', 'PE_Ratio', 'EV_EBITDA', 'Margins', 'Debt_Equity', 'RSI']]
        st.dataframe(
            display_df.style.background_gradient(subset=['Alpha_Score'], cmap='Greens'),
            use_container_width=True,
            height=600
        )

    with tab2:
        st.subheader("Valuation vs Quality")
        fig = px.scatter(
            df,
            x="EV_EBITDA",
            y="Margins",
            size="Alpha_Score",
            color="Sentiment",
            text="Ticker",
            title="Quality (Margins) vs Price (EV/EBITDA)",
            labels={"EV_EBITDA": "EV / EBITDA (Lower is Cheaper)", "Margins": "Profit Margin (Higher is Better)"},
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Awaiting Data Ingestion. Run pipeline locally.")