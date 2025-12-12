import yfinance as yf
import pandas as pd
import requests
from niftystocks import ns
from datetime import datetime

# ==========================================
# 1. LIVE PRICE FETCHER (With Fallback)
# ==========================================
def get_live_price(ticker):
    """
    1. Tries to get LIVE price (1000).
    2. If blocked, returns None (so we can handle it gracefully).
    """
    try:
        stock = yf.Ticker(ticker)
        # Try 'currentPrice'
        if 'currentPrice' in stock.info and stock.info['currentPrice']:
            return float(stock.info['currentPrice'])
        # Try Fast Info
        return float(stock.fast_info['last_price'])
    except:
        return None

# ==========================================
# 2. CONFIGURATION
# ==========================================
def get_nifty_tickers():
    print("🔄 Fetching Nifty 50 tickers...")
    try:
        tickers = ns.get_nifty50()
        tickers = [t + '.NS' for t in tickers]
        return tickers
    except:
        return ['RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'TCS.NS']

# ==========================================
# 3. ANALYSIS ENGINE
# ==========================================
def get_history_batch(tickers):
    print(f"\n📥 Downloading historical context...")
    try:
        data = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False)
        if 'Adj Close' in data.columns: return data['Adj Close']
        elif 'Close' in data.columns: return data['Close']
        else: return data.xs('Close', level=0, axis=1, drop_level=False)
    except:
        return pd.DataFrame()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market(tickers, market_name):
    print(f"\n⚙️ Running Analysis for {market_name}...")
    history_df = get_history_batch(tickers)
    results = []
    
    # TIMESTAMP TO PROVE IT UPDATED
    run_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"   ⚡ Fetching prices (Fail-Safe Mode)...")
    
    for ticker in tickers:
        try:
            # 1. Get Price
            live_price = get_live_price(ticker)
            is_live = True
            
            # FALLBACK LOGIC (The Fix)
            if live_price is None:
                # If Live Fetch failed, use yesterday's close from history
                # This ensures we ALWAYS have a number.
                if ticker in history_df.columns:
                    live_price = history_df[ticker].iloc[-1]
                    is_live = False
                else:
                    continue # Skip only if we have NO data at all

            # 2. Indicators
            if ticker in history_df.columns:
                hist_series = history_df[ticker].dropna()
                if len(hist_series) < 50: continue
                
                rsi = calculate_rsi(hist_series).iloc[-1]
                sma_50 = hist_series.rolling(window=50).mean().iloc[-1]
                sma_200 = hist_series.rolling(window=200).mean().iloc[-1]
                
                score = 50
                if live_price > sma_50: score += 10
                if sma_50 > sma_200: score += 10
                if 30 < rsi < 50: score += 20    
                elif rsi > 70: score -= 20       
                
                score = min(100, max(0, score))
                
                results.append({
                    'Ticker': ticker,
                    'Close': round(live_price, 2),
                    'Alpha_Score': int(score),
                    'RSI': round(rsi, 2),
                    'SMA_50': round(sma_50, 2),
                    'Data_Source': "LIVE" if is_live else "DELAYED",
                    'Last_Updated': run_timestamp
                })
        except:
            continue

    # ALWAYS SAVE (Even if results are imperfect)
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='Alpha_Score', ascending=False)
        filename = f"{market_name}_rankings.csv"
        df_results.to_csv(filename, index=False)
        
        top = df_results.iloc[0]
        print(f"✅ Saved {market_name}. Top: {top['Ticker']} (Source: {top['Data_Source']})")
    else:
        print(f"❌ CRITICAL: No results generated at all.")

if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    tickers_in = get_nifty_tickers()
    analyze_market(tickers_in, "IN")
    print("\n✅ All Tasks Completed.")
