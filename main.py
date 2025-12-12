import yfinance as yf
import pandas as pd
import requests
from niftystocks import ns
from datetime import datetime

# ==========================================
# 1. LIVE PRICE FETCHER (NSE OFFICIAL API)
# ==========================================
def get_live_price(ticker):
    """
    Fetches REAL-TIME price directly from NSE India API.
    Bypasses Google/Yahoo/MarketWatch blocks to fix the 989 vs 1000 issue.
    """
    try:
        # Convert 'HDFCBANK.NS' -> 'HDFCBANK'
        clean_ticker = ticker.replace('.NS', '')
        
        # Get Quote from NSE
        quote = ns.get_quote(clean_ticker)
        
        # Extract Price
        if quote and 'lastPrice' in quote:
            price = float(quote['lastPrice'])
            return price
        else:
            return None
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
    # Only for RSI/SMA history (Yahoo is fine for this)
    print(f"\n📥 Downloading historical context...")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        data = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False, session=session)
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
    
    print(f"   ⚡ Fetching REAL-TIME prices from NSE API...")
    
    for ticker in tickers:
        try:
            # 1. Get Live Price (NSE API)
            live_price = get_live_price(ticker)
            
            # If NSE fails, try Yahoo History as last resort
            if live_price is None:
                if ticker in history_df.columns:
                    live_price = history_df[ticker].iloc[-1]
                else:
                    continue

            # 2. Indicators (From History)
            if ticker in history_df.columns:
                hist_series = history_df[ticker].dropna()
                if len(hist_series) < 50: continue
                
                rsi = calculate_rsi(hist_series).iloc[-1]
                sma_50 = hist_series.rolling(window=50).mean().iloc[-1]
                sma_200 = hist_series.rolling(window=200).mean().iloc[-1]
                
                # Alpha Score Logic
                score = 50
                if live_price > sma_50: score += 10
                if sma_50 > sma_200: score += 10
                if 30 < rsi < 50: score += 20    
                elif rsi > 70: score -= 20       
                elif rsi < 30: score += 10       
                
                score = min(100, max(0, score))
                
                results.append({
                    'Ticker': ticker,
                    'Close': round(live_price, 2),
                    'Alpha_Score': int(score),
                    'RSI': round(rsi, 2),
                    'SMA_50': round(sma_50, 2)
                })
        except:
            continue

    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='Alpha_Score', ascending=False)
        filename = f"{market_name}_rankings.csv"
        df_results.to_csv(filename, index=False)
        top = df_results.iloc[0]
        print(f"✅ Saved {market_name}. Top Pick: {top['Ticker']} @ {top['Close']}")
    else:
        print(f"❌ No results for {market_name}")

if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    tickers_in = get_nifty_tickers()
    analyze_market(tickers_in, "IN")
    print("\n✅ All Tasks Completed.")
