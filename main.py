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
        return tickers[:50] 
    except:
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

# ==========================================
# 2. HISTORICAL DATA (For RSI/SMA)
# ==========================================
def get_history_batch(tickers):
    """
    Downloads 1 year of history for RSI/SMA calculation.
    """
    print(f"\n📥 Downloading historical context for {len(tickers)} stocks...")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"})

    try:
        # We only need history for indicators, so even if this is 1 day old, it's okay.
        data = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False, session=session)
        
        if 'Adj Close' in data.columns: return data['Adj Close']
        elif 'Close' in data.columns: return data['Close']
        else: return data.xs('Close', level=0, axis=1, drop_level=False)
    except Exception as e:
        print(f"❌ Batch download error: {e}")
        return pd.DataFrame()

# ==========================================
# 3. LIVE PRICE FETCHER (The Fix)
# ==========================================
def get_real_time_price(ticker):
    """
    Fetches the ABSOLUTE LATEST price using fast_info.
    This bypasses the candle-chart delay.
    """
    try:
        stock = yf.Ticker(ticker)
        # fast_info hits the quote summary directly (Live)
        price = stock.fast_info['last_price']
        return price
    except:
        return None

# ==========================================
# 4. ANALYSIS ENGINE
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market(tickers, market_name):
    print(f"\n⚙️ Running LIVE Analysis for {market_name}...")
    
    # 1. Get History (Batch) for Math
    history_df = get_history_batch(tickers)
    
    results = []
    
    # 2. Loop through tickers to get PRECISE Live Price
    print("   ⚡ Fetching real-time quotes...")
    
    for ticker in tickers:
        try:
            # A. Get Live Price (The Surgical Fix)
            live_price = get_real_time_price(ticker)
            
            # If live fetch fails, skip (don't use stale data)
            if live_price is None: 
                continue

            # B. Get History for Indicators
            if ticker in history_df.columns:
                hist_series = history_df[ticker].dropna()
                if len(hist_series) < 50: continue
                
                # Indicators based on history (approximate is fine for SMA/RSI)
                rsi = calculate_rsi(hist_series).iloc[-1]
                sma_50 = hist_series.rolling(window=50).mean().iloc[-1]
                sma_200 = hist_series.rolling(window=200).mean().iloc[-1]
                
                # Returns: Compare LIVE price to 5 days ago
                prev_price = hist_series.iloc[-5]
                returns_1w = (live_price - prev_price) / prev_price * 100
                
                # --- ALPHA SCORE ---
                score = 50
                if live_price > sma_50: score += 10
                if sma_50 > sma_200: score += 10 
                if 30 < rsi < 50: score += 20    
                elif rsi > 70: score -= 20       
                elif rsi < 30: score += 10       
                if returns_1w > 0: score += 10
                
                score = min(100, max(0, score))
                
                results.append({
                    'Ticker': ticker,
                    'Close': round(live_price, 2), # THIS IS NOW REAL-TIME
                    'Alpha_Score': int(score),
                    'RSI': round(rsi, 2),
                    'SMA_50': round(sma_50, 2)
                })
        except:
            continue

    # Save
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='Alpha_Score', ascending=False)
        filename = f"{market_name}_rankings.csv"
        df_results.to_csv(filename, index=False)
        
        # VERIFICATION PRINT
        top_stock = df_results.iloc[0]
        print(f"✅ Saved {market_name}. Top Pick: {top_stock['Ticker']} @ {top_stock['Close']}")
    else:
        print(f"❌ No results for {market_name}")

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    tickers_in = get_nifty_tickers()
    analyze_market(tickers_in, "IN")
    
    # Uncomment for US if needed
    # tickers_us = get_sp500_tickers()
    # analyze_market(tickers_us, "US"
    
    # Uncomment for US if needed
    # tickers_us = get_sp500_tickers()
    # analyze_market(tickers_us, "US")
    
    print("\n✅ All Tasks Completed.")
