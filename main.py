import yfinance as yf
import pandas as pd
import requests
import time
from niftystocks import ns
from datetime import datetime

# ==========================================
# 1. DYNAMIC TICKER GENERATORS
# ==========================================
def get_nifty_tickers():
    print("🔄 Fetching Nifty 50 tickers...")
    try:
        tickers = ns.get_nifty50()
        tickers = [t + '.NS' for t in tickers]
        return tickers
    except:
        return ['RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'TCS.NS']

def get_sp500_tickers():
    print("🔄 Fetching S&P 500 tickers...")
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers[:50] # Limit to Top 50 for speed
    except:
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

# ==========================================
# 2. THE DUAL-FETCH DOWNLOADER (History + Live)
# ==========================================
def get_data_dual_mode(tickers):
    """
    Fetches Daily data for analysis AND Minute data for Live Price.
    This bypasses the GitHub "Delayed Daily Data" issue.
    """
    print(f"\n📥 Dual-Fetching data for {len(tickers)} stocks...")
    
    # Session for Stealth Mode
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    # A. DOWNLOAD HISTORY (1 Year Daily) - For RSI/SMA
    print("   1. Getting Historical Data (1y)...")
    history = pd.DataFrame()
    try:
        history = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False, session=session)
        # Clean Columns
        if 'Adj Close' in history.columns: history = history['Adj Close']
        elif 'Close' in history.columns: history = history['Close']
        else: history = history.xs('Close', level=0, axis=1, drop_level=False)
    except Exception as e:
        print(f"      Error fetching history: {e}")

    # B. DOWNLOAD LIVE (1 Day, 1 Minute) - For Real-Time Price
    print("   2. Getting LIVE Data (1m)...")
    live = pd.DataFrame()
    try:
        live = yf.download(tickers, period="1d", interval="1m", auto_adjust=False, progress=False, session=session)
        # Clean Columns
        if 'Adj Close' in live.columns: live = live['Adj Close']
        elif 'Close' in live.columns: live = live['Close']
        else: live = live.xs('Close', level=0, axis=1, drop_level=False)
    except Exception as e:
        print(f"      Error fetching live data: {e}")

    return history, live

# ==========================================
# 3. TECHNICAL ANALYSIS ENGINE
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market(tickers, market_name):
    print(f"\n⚙️ Running Dual-Analysis for {market_name}...")
    
    # Fetch BOTH datasets
    history_df, live_df = get_data_dual_mode(tickers)
    
    if history_df.empty:
        print("❌ Critical Error: No historical data.")
        return

    results = []
    
    for ticker in tickers:
        try:
            # 1. Get History (for RSI / SMA)
            if ticker not in history_df.columns: continue
            hist_series = history_df[ticker].dropna()
            if len(hist_series) < 50: continue
            
            # 2. Get Live Price (Force Update)
            # If live data exists for this ticker, use it. Else fall back to history.
            if not live_df.empty and ticker in live_df.columns:
                live_series = live_df[ticker].dropna()
                if not live_series.empty:
                    current_price = live_series.iloc[-1] # The absolute latest minute price
                else:
                    current_price = hist_series.iloc[-1]
            else:
                current_price = hist_series.iloc[-1]

            # 3. Calculate Indicators (Using History)
            rsi = calculate_rsi(hist_series).iloc[-1]
            sma_50 = hist_series.rolling(window=50).mean().iloc[-1]
            sma_200 = hist_series.rolling(window=200).mean().iloc[-1]
            
            # 4. Calculate Returns (Live Price vs 5 days ago)
            prev_price = hist_series.iloc[-5]
            returns_1w = (current_price - prev_price) / prev_price * 100
            
            # --- ALPHA SCORE ---
            score = 50
            if current_price > sma_50: score += 10
            if sma_50 > sma_200: score += 10 
            if 30 < rsi < 50: score += 20    
            elif rsi > 70: score -= 20       
            elif rsi < 30: score += 10       
            if returns_1w > 0: score += 10
            
            score = min(100, max(0, score))
            
            results.append({
                'Ticker': ticker,
                'Close': round(current_price, 2), # This will now be LIVE
                'Alpha_Score': int(score),
                'RSI': round(rsi, 2),
                'SMA_50': round(sma_50, 2)
            })
            
        except Exception:
            continue

    df_results = pd.DataFrame(results)
    
    if not df_results.empty:
        df_results = df_results.sort_values(by='Alpha_Score', ascending=False)
        filename = f"{market_name}_rankings.csv"
        df_results.to_csv(filename, index=False)
        
        # Verify freshness
        print(f"✅ Saved {market_name} rankings.")
        print(f"   Sample Price ({df_results.iloc[0]['Ticker']}): {df_results.iloc[0]['Close']}")
    else:
        print(f"❌ No results for {market_name}")

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    
    # 1. Fetch Tickers
    tickers_in = get_nifty_tickers()
    tickers_us = get_sp500_tickers()
    
    # 2. Run Analysis
    analyze_market(tickers_in, "IN")
    analyze_market(tickers_us, "US")
    
    print("\n✅ All Tasks Completed.")
