import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from niftystocks import ns
from datetime import datetime
import time
import random

# ==========================================
# 1. LIVE PRICE FETCHER (MarketWatch Source)
# ==========================================
def get_marketwatch_price(ticker):
    """
    Scrapes the price from MarketWatch to bypass Yahoo/Google cache.
    """
    try:
        # 1. Clean Ticker: 'HDFCBANK.NS' -> 'hdfcbank'
        symbol = ticker.split('.')[0].lower()
        
        # 2. Construct URL
        url = f"https://www.marketwatch.com/investing/stock/{symbol}?countrycode=in"
        
        # 3. Rotate Headers to look like a Human
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        headers = {"User-Agent": random.choice(user_agents)}
        
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 4. Find the Price (MarketWatch uses <bg-quote class="value">)
        price_tag = soup.find('bg-quote', class_='value')
        
        if price_tag:
            price_text = price_tag.text.replace(",", "")
            return float(price_text)
        else:
            # Fallback for some pages that use a different class
            meta_price = soup.find('meta', {'name': 'price'})
            if meta_price:
                return float(meta_price['content'].replace(",", ""))
                
        return None
    except Exception as e:
        # print(f"   ⚠️ MW scrape error for {ticker}: {e}")
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
    print(f"\n📥 Downloading historical context (Yahoo)...")
    try:
        # We only use Yahoo for the SMA/RSI math, so 1-day lag is acceptable here
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
    
    # 1. Get History (for Math)
    history_df = get_history_batch(tickers)
    results = []
    
    print(f"   ⚡ Fetching REAL-TIME prices from MarketWatch...")
    
    for ticker in tickers:
        try:
            # A. Get Live Price (MarketWatch)
            live_price = get_marketwatch_price(ticker)
            
            # Sanity Check: If MarketWatch failed, try Yahoo History
            if live_price is None:
                if ticker in history_df.columns:
                    live_price = history_df[ticker].iloc[-1]
                else:
                    continue

            # B. Indicators (From History)
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

