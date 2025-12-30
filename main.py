import yfinance as yf
import pandas as pd
import numpy as np
import requests

# --- CONFIGURATION ---
US_TICKER_SOURCE = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
# Using a reliable Nifty 50 CSV source (or you can use a fixed list if this link breaks)
INDIA_TICKER_SOURCE = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"

def get_us_tickers():
    """Scrapes S&P 500 tickers from Wikipedia"""
    try:
        tables = pd.read_html(US_TICKER_SOURCE)
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Clean tickers (Change BRK.B to BRK-B for Yahoo)
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except Exception as e:
        print(f"Error fetching US tickers: {e}")
        return []

def get_india_tickers():
    """Fetches Nifty 50 tickers and adds .NS suffix"""
    try:
        # NSE blocks scripts, so we use a standard header or fallback to a hardcoded list if needed
        # For stability in GitHub Actions, we often use a hardcoded list or a mirror. 
        # Here is a robust fallback method using a direct list if scraping fails.
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(INDIA_TICKER_SOURCE, headers=headers)
        
        if response.status_code == 200:
            df = pd.read_csv(INDIA_TICKER_SOURCE)
            tickers = df['Symbol'].tolist()
            return [f"{t}.NS" for t in tickers]
        else:
            raise Exception("NSE Connection Failed")
    except:
        # FALLBACK LIST (Top 10-15 weights) to ensure it never fails entirely
        print("⚠️ Used Fallback Nifty List")
        return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
                "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS", "HINDUNILVR.NS"]

def calculate_rsi(series, period=14):
    """Calculates Relative Strength Index (RSI)"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market(tickers, region_name):
    print(f"🔄 Analyzing {region_name} Market ({len(tickers)} tickers)...")
    
    if not tickers:
        return

    # 1. BATCH DOWNLOAD DATA (Faster than looping)
    data = yf.download(tickers, period="6mo", group_by='ticker', progress=False)
    
    results = []

    for ticker in tickers:
        try:
            # Extract DataFrame for single ticker
            df = data[ticker]
            
            # Check if data exists
            if df.empty or len(df) < 20:
                continue

            # 2. CALCULATE TECHNICALS
            current_close = df['Close'].iloc[-1]
            df['RSI'] = calculate_rsi(df['Close'])
            current_rsi = df['RSI'].iloc[-1]
            
            # 3. GET FUNDAMENTALS (Note: This is slow, so we do it only for valid stocks)
            # Optimization: In a real "Speed" scenario, we might skip this or fetch in bulk.
            # For this project, we fetch info individually.
            stock = yf.Ticker(ticker)
            info = stock.info
            
            pe_ratio = info.get('trailingPE', 999) # Default to high if missing
            margins = info.get('profitMargins', 0)
            
            # 4. ALPHA SCORE LOGIC (The "Secret Sauce")
            # Criteria: 
            # - Low RSI (Oversold) -> Higher Score
            # - Low PE (Cheap) -> Higher Score
            # - High Margins (Quality) -> Higher Score
            
            rsi_score = max(0, (70 - current_rsi)) # Higher if RSI is low
            pe_score = max(0, (50 - pe_ratio))     # Higher if PE is low
            margin_score = margins * 100           # Higher % is better
            
            alpha_score = (rsi_score * 0.4) + (pe_score * 0.3) + (margin_score * 0.3)
            
            results.append({
                "Ticker": ticker,
                "Close": round(current_close, 2),
                "RSI": round(current_rsi, 2),
                "PE_Ratio": round(pe_ratio, 2),
                "Margins": round(margins * 100, 1),
                "Alpha_Score": round(alpha_score, 1)
            })
            
        except Exception:
            continue

    # 5. SORT & SAVE
    if results:
        final_df = pd.DataFrame(results)
        final_df = final_df.sort_values(by="Alpha_Score", ascending=False)
        filename = f"{region_name}_rankings.csv"
        final_df.to_csv(filename, index=False)
        print(f"✅ Saved {filename} with {len(final_df)} stocks.")

def main():
    print("🚀 IronGate Engine Starting...")
    
    # Run US Market
    us_tickers = get_us_tickers()
    analyze_market(us_tickers, "US")
    
    # Run India Market
    india_tickers = get_india_tickers()
    analyze_market(india_tickers, "IN")
    
    print("🏁 Analysis Complete.")

if __name__ == "__main__":
    main()
