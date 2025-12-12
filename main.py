import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from niftystocks import ns
from datetime import datetime

# ==========================================
# 1. LIVE PRICE SCRAPER (Google Finance)
# ==========================================
def get_google_price(ticker):
    """
    Scrapes the absolute latest price from Google Finance.
    Bypasses all Yahoo API caches and delays.
    """
    try:
        # Convert Yahoo Ticker (HDFCBANK.NS) to Google Ticker (HDFCBANK:NSE)
        # Logic: Split by '.' and use the first part + :NSE
        symbol = ticker.split('.')[0]
        g_ticker = f"{symbol}:NSE"

        url = f"https://www.google.com/finance/quote/{g_ticker}"
        
        # Fake Browser Headers (Crucial)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # The specific class Google uses for the big stock price
        # This class 'YMlKec fxKbKc' is standard for Google Finance
        price_div = soup.find('div', class_='YMlKec fxKbKc')
        
        if price_div:
            # Remove currency symbol (₹) and commas
            price_text = price_div.text.replace("₹", "").replace("$", "").replace(",", "")
            return float(price_text)
        else:
            print(f"   ⚠️ Could not find price on Google for {ticker}")
            return None
            
    except Exception as e:
        print(f"   ⚠️ Google scrape error for {ticker}: {e}")
        return None

# ==========================================
# 2. DYNAMIC TICKER GENERATORS
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
    # Placeholder for US logic if needed later
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

# ==========================================
# 3. HISTORICAL DATA (For RSI/SMA Only)
# ==========================================
def get_history_batch(tickers):
    # We use Yahoo ONLY for history (SMA/RSI), where 1-day lag is acceptable.
    print(f"\n📥 Downloading historical context for indicators...")
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    try:
        data = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False, session=session)
        if 'Adj Close' in data.columns: return data['Adj Close']
        elif 'Close' in data.columns: return data['Close']
        else: return data.xs('Close', level=0, axis=1, drop_level=False)
    except:
        return pd.DataFrame()

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
    
    # 1. Get History for Math
    history_df = get_history_batch(tickers)
    
    results = []
    print("   ⚡ Fetching REAL-TIME prices from Google Finance...")
    
    for ticker in tickers:
        try:
            # A. Get LIVE Price from Google (The Fix)
            live_price = get_google_price(ticker)
            
            # Fallback: If Google fails, try Yahoo History (Better than crashing)
            if live_price is None:
                if ticker in history_df.columns:
                    live_price = history_df[ticker].iloc[-1]
                else:
                    continue 

            # B. Indicators (Using History)
            if ticker in history_df.columns:
                hist_series = history_df[ticker].dropna()
                if len(hist_series) < 50: continue
                
                rsi = calculate_rsi(hist_series).iloc[-1]
                sma_50 = hist_series.rolling(window=50).mean().iloc[-1]
                sma_200 = hist_series.rolling(window=200).mean().iloc[-1]
                
                # Alpha Score Logic
                score = 50
                if live_price > sma_50: score += 10
                if sma_50 > sma_200: score += 10 # Trend
                if 30 < rsi < 50: score += 20    # Buy zone
                elif rsi > 70: score -= 20       # Overbought
                elif rsi < 30: score += 10       # Oversold
                
                # Cap score
                score = min(100, max(0, score))
                
                results.append({
                    'Ticker': ticker,
                    'Close': round(live_price, 2), # THIS IS REAL TIME
                    'Alpha_Score': int(score),
                    'RSI': round(rsi, 2),
                    'SMA_50': round(sma_50, 2)
                })
        except Exception as e:
            continue

    # Save Results
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values(by='Alpha_Score', ascending=False)
        filename = f"{market_name}_rankings.csv"
        df_results.to_csv(filename, index=False)
        
        # Verify Print
        top = df_results.iloc[0]
        print(f"✅ Saved {market_name}. Top Pick: {top['Ticker']} @ ₹{top['Close']}")
    else:
        print(f"❌ No results for {market_name}")

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🚀 AlphaQuant Engine Starting...")
    tickers_in = get_nifty_tickers()
    analyze_market(tickers_in, "IN")
    print("\n✅ All Tasks Completed.")
