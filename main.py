import yfinance as yf
import pandas as pd
import requests
from niftystocks import ns
from datetime import datetime
import pytz # timezone

# ==========================================
# 1. LIVE PRICE FETCHER (Aggressive Mode)
# ==========================================
def get_live_price(ticker):
    """
    Tries multiple fields to find a price that ISN'T yesterday's close.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 1. Try 'currentPrice'
        if 'currentPrice' in stock.info and stock.info['currentPrice'] is not None:
            return float(stock.info['currentPrice'])
            
        # 2. Try 'dayHigh' (Often updates even if currentPrice is stuck)
        if 'dayHigh' in stock.info and stock.info['dayHigh'] is not None:
            return float(stock.info['dayHigh'])
            
        # 3. Fallback
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
    # Only for RSI/SMA history
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
    print(f"\n⚙️ Running LIVE Analysis for {market_name}...")
    history_df = get_history_batch(tickers)
    results = []
    
    # Get Current India Time for the Timestamp
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"   ⚡ Fetching prices...")
    
    for ticker in tickers:
        try:
            live_price = get_live_price(ticker)
            if live_price is None: continue

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
                    'Last_Updated': current_time  # <--- THIS FORCES THE UPDATE
                })
        except:
            continue

    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='Alpha_Score', ascending=False)
        filename = f"{market_name}_rankings.csv"
        df_results.to_csv(filename, index=False)
        
        # Verify Print
        top = df_results.iloc[0]
        print(f"✅ Saved {market_name}. Top: {top['Ticker']} @ {top['Close']} (Time: {top['Last_Updated']})")
    else:
        print(f"❌ No results for {market_name}")

if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    tickers_in = get_nifty_tickers()
    analyze_market(tickers_in, "IN")
    print("\n✅ All Tasks Completed.")
