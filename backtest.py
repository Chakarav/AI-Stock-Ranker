import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

def run_backtest():
    print("⏳ Running Robust Backtest (Stealth Mode)...")
    
    # 1. Define Tickers (The "Sector Leaders" List)
    market_ticker = "^NSEI"
    strategy_tickers = [
        'HDFCBANK.NS', 'ICICIBANK.NS',  # Banking
        'INFY.NS', 'TCS.NS',            # IT
        'TATAMOTORS.NS', 'M&M.NS',      # Auto
        'RELIANCE.NS', 'ONGC.NS',       # Energy
        'ITC.NS', 'HINDUNILVR.NS',      # Consumer
        'ZOMATO.NS', 'TRENT.NS'         # High Growth
    ]
    tickers = strategy_tickers + [market_ticker]
    
    # 2. Download Data (STEALTH MODE - prevents YFTzMissingError)
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    print(f"   Downloading data for {len(tickers)} stocks...")
    
    # Fake Browser Session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })
    
    try:
        data = yf.download(tickers, start=start_date, auto_adjust=False, progress=False, session=session)
    except Exception as e:
        print(f"❌ Critical Download Error: {e}")
        return

    # 3. Handle Column Names (Fix for Index Error)
    if 'Adj Close' in data.columns:
        prices = data['Adj Close']
    elif 'Close' in data.columns:
        prices = data['Close']
    else:
        prices = data
    
    # Drop columns that failed to download (like Zomato if it errors)
    prices = prices.dropna(axis=1, how='all')
    
    # Drop rows with missing values
    prices = prices.dropna()
    
    if prices.empty:
        print("❌ Error: No valid data found. Yahoo blocked the request.")
        return

    # 4. Normalize Data (Start at 100)
    # Check if we have data before accessing index 0
    if len(prices) > 0:
        normalized = prices / prices.iloc[0] * 100
    else:
        print("❌ Error: Dataframe is empty.")
        return
    
    # 5. Calculate Strategy Index
    # Only use tickers that actually downloaded
    valid_strategy_tickers = [t for t in strategy_tickers if t in prices.columns]
    
    if not valid_strategy_tickers:
        print("❌ Error: None of the strategy stocks downloaded.")
        return
        
    strategy_index = normalized[valid_strategy_tickers].mean(axis=1)
    
    # Check if Market Ticker downloaded, else skip comparison
    if market_ticker in normalized.columns:
        market_index = normalized[market_ticker]
    else:
        print("⚠️ Warning: Nifty 50 failed to download. Showing Strategy only.")
        market_index = pd.Series(100, index=strategy_index.index) # Flat line backup
    
    # 6. Calculate Final Returns
    strategy_return = strategy_index.iloc[-1] - 100
    market_return = market_index.iloc[-1] - 100
    
    print(f"✅ Backtest Complete!")
    print(f"📊 Market Return: {market_return:.2f}%")
    print(f"🚀 AlphaQuant Strategy: {strategy_return:.2f}%")

    # 7. Create the Chart
    fig = go.Figure()
    
    # Market Line
    fig.add_trace(go.Scatter(
        x=market_index.index, y=market_index,
        mode='lines', name='Nifty 50 Benchmark',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    # Strategy Line
    fig.add_trace(go.Scatter(
        x=strategy_index.index, y=strategy_index,
        mode='lines', name='AlphaQuant Strategy (Sector Leaders)',
        line=dict(color='#00ff00', width=3)
    ))
    
    fig.update_layout(
        title="Performance: Equal-Weight Sector Leaders vs Nifty 50 (2 Years)",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (Starts at 100)",
        template="plotly_dark",
        hovermode="x unified"
    )
    
    fig.show()

if __name__ == "__main__":
    run_backtest()
