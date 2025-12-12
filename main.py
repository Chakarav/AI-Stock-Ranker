import yfinance as yf
import pandas as pd
import requests
from niftystocks import ns
from datetime import datetime

# ==========================================
# 1. LIVE PRICE FETCHER (The "1-Minute" Trick)
# ==========================================
def get_live_prices_batch(tickers):
    """
    Fetches the last 1-minute candle for tickers.
    Yahoo NEVER caches 1m data, so this guarantees the Real Price (~1000).
    """
    print(f"   ⚡ Fetching LIVE 1-minute data for {len(tickers)} stocks...")
    
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    try:
        # Request 5 days of 1-minute data (Force fresh download)
        data = yf.download(tickers, period="5d", interval="1m", auto_adjust=False, progress=False, session=session)
        
        # Clean up columns
        if 'Adj Close' in data.columns:
            prices = data['Adj Close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            prices = data.xs('Close', level=0, axis=1, drop_level=False)
            
        # The last row is the absolute latest price (3:29 PM Today)
        latest_prices = prices.iloc[-1]
        
        # DEBUG: Print the date of the data we just got
        last_time = prices.index[-1]
        print(f"   📅 Data Timestamp: {last_time}")
        
        return latest_prices
    except Exception as e:
        print(f"   ❌ 1-Minute Fetch Failed: {e}")
        return None

# ==========================================
# 2. ANALYSIS ENGINE
# ==========================================
def analyze_market(tickers, market_name):
    print(f"\n⚙️ Running LIVE Analysis for {market_name}...")
    
    # 1. Get Live Prices (The 1m Trick)
    live_prices_series = get_live_prices_batch(tickers)
    
    # 2. Get History (For RSI/SMA - 1d is fine here)
    print(f"   📥 Downloading historical context...")
    history_data = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False)
    
    if 'Adj Close' in history_data.columns: history_df = history_data['Adj Close']
    elif 'Close' in history_data.columns: history_df = history_data['Close']
    else: history_df = history_data.xs('Close', level=0, axis=1, drop_level=False)

    results = []
    
    for ticker in tickers:
        try:
            # EXTRACT LIVE PRICE
            if live_prices_series is not None and ticker in live_prices_series:
                live_price = float(live_prices_series[ticker])
            else:
                continue

            if pd.isna(live_price): continue

            # INDICATORS (From History)
            if ticker in history_df.columns:
                hist_series = history_df[ticker].dropna()
                if len(hist_series) < 50: continue
                
                # RSI / SMA Math
                delta = hist_series.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = (100 - (100 / (1 + rs))).iloc[-1]
                
                sma_50 = hist_series.rolling(window=50).mean().iloc[-1]
                sma_200 = hist_series.rolling(window=200).mean().iloc[-1]
                
                # SCORE
                score = 50
                if live_price > sma_50: score += 10
                if sma_50 > sma_200: score += 10
                if 30 < rsi < 50: score += 20
                elif rsi > 70: score -= 20
                
                results.append({
                    'Ticker': ticker,
                    'Close': round(live_price, 2),
                    'Alpha_Score': int(min(100, max(0, score))),
                    'RSI': round(rsi, 2),
                    'SMA_50': round(sma_50, 2)
                })
        except:
            continue

    # SAVE
    df = pd.DataFrame(results).sort_values(by='Alpha_Score', ascending=False)
    if not df.empty:
        df.to_csv(f"{market_name}_rankings.csv", index=False)
        print(f"✅ Saved {market_name}. Top Pick: {df.iloc[0]['Ticker']} @ {df.iloc[0]['Close']}")
    else:
        print(f"❌ No results for {market_name}")

# ==========================================
# 3. EXECUTION
# ==========================================
if __name__ == "__main__":
    try:
        tickers = [t + '.NS' for t in ns.get_nifty50()]
    except:
        tickers = ['HDFCBANK.NS', 'RELIANCE.NS', 'INFY.NS', 'TCS.NS']
        
    analyze_market(tickers, "IN")
