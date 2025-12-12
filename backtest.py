import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from niftystocks import ns
from datetime import datetime, timedelta

def run_backtest():
    print("⏳ Running Dynamic Backtest on ALL Nifty 50 Stocks...")
    
    # 1. DYNAMICALLY GET TICKERS (No Hardcoding)
    try:
        print("   🔄 Fetching current Nifty 50 list from NSE...")
        nifty_tickers = ns.get_nifty50()
        # Add .NS extension
        strategy_tickers = [t + '.NS' for t in nifty_tickers]
        print(f"   ✅ Found {len(strategy_tickers)} stocks (e.g., {strategy_tickers[:3]}...)")
    except Exception as e:
        print(f"   ❌ Failed to fetch Nifty list: {e}")
        return

    market_ticker = "^NSEI"
    tickers = strategy_tickers + [market_ticker]
    
    # 2. DOWNLOAD DATA (Stealth Mode to prevent crashes)
    start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d') # 2 Years
    print(f"   📥 Downloading 2 years of data for {len(tickers)} stocks...")
    
    # Fake Browser Session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    
    try:
        # Download all 51 tickers at once
        data = yf.download(tickers, start=start_date, auto_adjust=False, progress=False, session=session)
    except Exception as e:
        print(f"❌ Critical Download Error: {e}")
        return

    # 3. CLEAN UP DATA
    if 'Adj Close' in data.columns:
        prices = data['Adj Close']
    elif 'Close' in data.columns:
        prices = data['Close']
    else:
        prices = data
    
    # Drop columns that failed (like if a stock was delisted)
    prices = prices.dropna(axis=1, how='all')
    prices = prices.dropna() # Drop rows with NaNs to align dates
    
    if prices.empty:
        print("❌ Error: No valid data found.")
        return

    # 4. RUN STRATEGY (Equal Weight of ENTIRE Nifty 50)
    # This tests: "If I bought the whole index equal-weighted, how does it do vs the actual index?"
    # (You can modify this logic to pick 'Top 5' if you want a strategy test)
    
    normalized = prices / prices.iloc[0] * 100
    
    # Filter for stocks that actually downloaded
    valid_tickers = [t for t in strategy_tickers if t in prices.columns]
    
    # Strategy: Equal Weight of all Nifty 50 components
    strategy_index = normalized[valid_tickers].mean(axis=1)
    
    if market_ticker in normalized.columns:
        market_index = normalized[market_ticker]
    else:
        market_index = pd.Series(100, index=strategy_index.index)
    
    # 5. PLOT RESULTS
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=market_index.index, y=market_index,
        mode='lines', name='Nifty 50 Index (Actual)',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=strategy_index.index, y=strategy_index,
        mode='lines', name='Nifty 50 Equal-Weight (Strategy)',
        line=dict(color='#00ff00', width=3)
    ))
    
    fig.update_layout(
        title="Backtest: Nifty 50 Equal Weight vs Market
