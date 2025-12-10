import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AlphaQuant Dashboard", layout="wide")
st.title("📈 AI-Powered Stock Ranker")

market = st.sidebar.selectbox("Select Market", ["IN", "US"])

@st.cache_data
def load_data(market):
    try:
        # UPDATED: No 'data/' prefix because files are in root
        rankings = pd.read_csv(f"{market}_rankings.csv")
        backtest = pd.read_csv(f"{market}_backtest_curve.csv")
        return rankings, backtest
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

rankings, backtest = load_data(market)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"🏆 Top 10 Picks ({market})")
    if not rankings.empty:
        st.dataframe(rankings.head(10).style.background_gradient(subset=['ML_Confidence'], cmap='Greens'))
    else:
        st.error(f"No data found for {market}_rankings.csv in root folder.")

with col2:
    st.subheader("🤖 Stats")
    if not rankings.empty:
        st.metric("Top Confidence", f"{rankings['ML_Confidence'].max():.1%}")

st.markdown("---")
if not backtest.empty:
    fig = px.line(backtest, x='Date', y=['Market_Cumulative', 'Strategy_Cumulative'], 
                  title="Equity Curve", color_discrete_sequence=['gray', 'blue'])
    st.plotly_chart(fig, use_container_width=True)
