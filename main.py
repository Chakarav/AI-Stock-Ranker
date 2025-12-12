import yfinance as yf
import pandas as pd
import requests
from niftystocks import ns
from datetime import datetime

# ==========================================
# 1. LIVE PRICE FETCHER (The "Info" Method)
# ==========================================
def get_live_price(ticker):
    """
    Fetches live price using yfinance .info['currentPrice'].
    This endpoint works better on US Servers (GitHub) than NSE scraping.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Method A: Try the 'currentPrice' field (Most accurate)
        if 'currentPrice' in stock.info and stock.info['currentPrice'] is not None:
            return float(stock.info['currentPrice'])
            
        # Method B: Try 'regularMarketPrice'
        if 'regularMarketPrice' in stock.info and stock.info['regularMarketPrice'] is not None:
            return float(stock.info['regularMarketPrice'])
            
        # Method C: Fast Info (Backup)
        return float(stock.fast_info['last_price'])

    except Exception as e:
        # print(f"   ⚠️ Could not fetch live price for {ticker}: {e}")
        return None

# ==========================================
# 2. CONFIGURATION
# ==========================================
def get_nifty_tickers():
    print("🔄 Fetching Nifty 50 tickers...")
    try:
        # Try to fetch dynamic list
        tickers = ns.get_nifty50()
        tickers = [t + '.NS' for t in tickers]
        return tickers
    except:
        # Fallback list if NSE blocks the list fetch
        return [
            'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'TCS.NS', 'ICICIBANK.NS',
            'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'LICI.NS', 'HINDUNILVR.NS',
            'TATAMOTORS.NS', 'LT.NS', 'BAJFINANCE.NS', 'HCLTECH.NS', 'MARUTI.NS',
            'SUNPHARMA.NS', 'TITAN.NS', 'M&M.NS', 'ULTRACEMCO.NS', 'ASIANPAINT.NS'
        ]

# ==========================================
# 3. ANALYSIS ENGINE
# ==========================================
def get_history_batch(tickers):
    print(f"\n📥 Downloading historical context (Yahoo)...")
    try:
        # History is ONLY for math (RSI/SMA), not for the displayed price.
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
    
    print(f"   ⚡ Fetching REAL-TIME prices (Strict Mode)...")
    
    for ticker in tickers:
        try:
            # 1. Get Live Price
            live_price = get_live_price(ticker)
            
            # STRICT MODE: If live price fails, SKIP THE STOCK.
            # Do NOT fallback to old history. This prevents the "989" error.
            if live_price is None:
                continue

            # 2. Indicators (From History)
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
                elif rsi < 30: score += 10       
                
                score = min(100, max(0, score))
                
                results.append({
                    'Ticker': ticker,
                    'Close': round(live_price, 2), # THIS MUST BE LIVE
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
        top = df_results.iloc[0]
        print(f"✅ Saved {market_name}. Top Pick: {top['Ticker']} @ {top['Close']}")
    else:
        print(f"❌ No results for {market_name}")

if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    tickers_in = get_nifty_tickers()
    analyze_market(tickers_in, "IN")
    print("\n✅ All Tasks Completed.")
