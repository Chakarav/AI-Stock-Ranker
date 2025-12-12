import yfinance as yf
import pandas as pd
import requests
import time
from niftystocks import ns  # <--- The module you wanted
from datetime import datetime

# ==========================================
# 1. DYNAMIC TICKER GENERATORS
# ==========================================
def get_nifty_tickers():
    print("🔄 Fetching Nifty 50 tickers using niftystocks module...")
    try:
        # Get list of Nifty 50 tickers
        tickers = ns.get_nifty50()
        # Add '.NS' extension for Yahoo Finance
        tickers = [t + '.NS' for t in tickers]
        print(f"✅ Loaded {len(tickers)} IN stocks.")
        return tickers
    except Exception as e:
        print(f"❌ Error fetching Nifty tickers: {e}")
        # Fallback list just in case module fails
        return ['RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'TCS.NS']

def get_sp500_tickers():
    print("🔄 Fetching S&P 500 tickers from Wikipedia...")
    try:
        # Scrape Wikipedia for the latest S&P 500 list
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Fix tickers (Yahoo uses '-' instead of '.' for stocks like BRK.B)
        tickers = [t.replace('.', '-') for t in tickers]
        print(f"✅ Loaded {len(tickers)} US stocks.")
        return tickers
    except Exception as e:
        print(f"❌ Error fetching S&P 500 tickers: {e}")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

# ==========================================
# 2. ROBUST DATA DOWNLOADER (STEALTH MODE)
# ==========================================
def get_stock_data(tickers):
    """
    Downloads data using a fake 'User-Agent' to prevent Yahoo blocks.
    """
    print(f"\n📥 Downloading data for {len(tickers)} stocks in Stealth Mode...")
    
    # Fake a Browser Session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    data = pd.DataFrame()
    
    # Retry Logic (3 Attempts)
    for attempt in range(3):
        try:
            # Download in batches is sometimes safer, but let's try all at once first
            data = yf.download(
                tickers, 
                period="1y", 
                interval="1d", 
                auto_adjust=False, 
                progress=False,
                session=session
            )
            if not data.empty:
                break
            else:
                print(f"   ⚠️ Attempt {attempt+1}: Empty data. Retrying...")
                time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    
    if data.empty:
        print("❌ CRITICAL ERROR: Could not download data.")
        return None

    # Handle Multi-Index Columns
    try:
        if 'Adj Close' in data.columns:
            data = data['Adj Close']
        elif 'Close' in data.columns:
            data = data['Close']
        else:
            data = data.xs('Close', level=0, axis=1, drop_level=False)
    except Exception as e:
        pass

    # Remove failed columns
    data = data.dropna(axis=1, how='all')
    
    # --- DATE CHECK ---
    if not data.empty:
        last_date = data.index[-1]
        today_date = pd.Timestamp.now().date()
        print(f"📅 DATA DATE: {last_date.date()} (Today: {today_date})")
    
    return data

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
    print(f"\n⚙️ Running Analysis for {market_name}...")
    
    prices = get_stock_data(tickers)
    if prices is None:
        return
    
    results = []
    
    for ticker in prices.columns:
        try:
            close_prices = prices[ticker].dropna()
            if len(close_prices) < 50: continue 
            
            current_price = close_prices.iloc[-1]
            
            # --- CALCULATIONS ---
            rsi = calculate_rsi(close_prices).iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            sma_200 = close_prices.rolling(window=200).mean().iloc[-1]
            returns_1w = (current_price - close_prices.iloc[-5]) / close_prices.iloc[-5] * 100
            
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
                'Close': round(current_price, 2),
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
        print(f"✅ Saved {len(df_results)} stocks to {filename}")
    else:
        print(f"❌ No results generated for {market_name}")

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    
    # 1. Fetch Dynamic Tickers
    tickers_in = get_nifty_tickers()
    tickers_us = get_sp500_tickers()
    
    # 2. Run Analysis
    analyze_market(tickers_in, "IN")
    analyze_market(tickers_us, "US")
    
    print("\n✅ All Tasks Completed.")
