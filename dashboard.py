# src/dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Config (Dark Mode & Wide Layout)
st.set_page_config(page_title="AlphaQuant Dashboard", layout="wide", page_icon="📈")

# Custom CSS for that "Hedge Fund" Dark Look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ AlphaQuant: AI-Driven Stock Ranking System")
st.markdown("### *Institutional-Grade Analysis for Retail Traders*")

# 2. Sidebar Controls
market = st.sidebar.selectbox("Select Market", ["IN", "US"])
st.sidebar.markdown("---")
st.sidebar.caption("Last Updated: " + str(datetime.now().date()))

# 3. Load Data Helper
@st.cache_data
def load_data(market):
    try:
        rankings = pd.read_csv(f"data/{market}_rankings.csv")
        backtest = pd.read_csv(f"data/{market}_backtest_curve.csv")
        # Ensure date column is correct
        if not backtest.empty:
            backtest['Date'] = pd.to_datetime(backtest['Date'])
        return rankings, backtest
    except:
        return pd.DataFrame(), pd.DataFrame()

rankings, backtest = load_data(market)

# 4. KPI Section (The "Heads Up" Display)
col1, col2, col3, col4 = st.columns(4)

if not backtest.empty:
    total_return = backtest['Strategy_Cumulative'].iloc[-1]
    market_return = backtest['Market_Cumulative'].iloc[-1]
    
    col1.metric("Strategy Return", f"{total_return:.1%}", delta=f"{total_return*100:.1f}%")
    col2.metric("Market Benchmark", f"{market_return:.1%}", delta=f"{market_return*100:.1f}%", delta_color="off")
    
    alpha = total_return - market_return
    col3.metric("Alpha (Excess Return)", f"{alpha:.1%}", delta=f"{alpha*100:.1f}%")
else:
    col1.metric("Status", "No Data", "Run main.py")

if not rankings.empty:
    top_pick = rankings.iloc[0]['Ticker']
    confidence = rankings.iloc[0]['ML_Confidence']
    col4.metric(f"Top Pick ({market})", top_pick, f"{confidence:.1%} Conf.")

# 5. Advanced Charts (Candlestick + Equity Curve)
st.markdown("---")
tab1, tab2 = st.tabs(["📈 Strategy Performance", "📊 Top Picks Analysis"])

with tab1:
    if not backtest.empty:
        # Professional Equity Curve
        fig = go.Figure()
        
        # Strategy Line
        fig.add_trace(go.Scatter(
            x=backtest['Date'], y=backtest['Strategy_Cumulative'],
            mode='lines', name='AI Strategy',
            line=dict(color='#00ff00', width=2)
        ))
        
        # Benchmark Line
        fig.add_trace(go.Scatter(
            x=backtest['Date'], y=backtest['Market_Cumulative'],
            mode='lines', name='Benchmark (S&P/Nifty)',
            line=dict(color='gray', dash='dash')
        ))
        
        fig.update_layout(
            title="Equity Curve (Growth of $1)",
            xaxis_title="Date",
            yaxis_title="Return Multiple",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run the backend to generate performance data.")

with tab2:
    if not rankings.empty:
        st.dataframe(
            rankings.head(10).style.background_gradient(subset=['ML_Confidence'], cmap='Greens'),
            use_container_width=True
        )
        st.caption("*Confidence > 55% indicates strong buy signal based on historical backtesting.")