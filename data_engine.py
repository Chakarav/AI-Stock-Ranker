import yfinance as yf
import pandas as pd
import requests
import io
import datetime
import numpy as np

class DataEngine:
    def __init__(self):
        print("⚙️ Initializing Institutional Data Engine...")

    # --- 1. DYNAMIC TICKER FETCHING ---
    def get_sp500_tickers(self):
        print("🔍 Scanning US Market (S&P 500)...")
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            tickers = tables[0]['Symbol'].tolist()
            return [t.replace('.', '-') for t in tickers]
        except:
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    def get_nifty50_tickers(self):
        print("🔍 Scanning India Market (Nifty 50)...")
        try:
            url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
            headers = {'User-Agent': 'Mozilla/5.0'}
            s = requests.get(url, headers=headers).content
            df = pd.read_csv(io.StringIO(s.decode('utf-8')))
            return [f"{x}.NS" for x in df['Symbol'].tolist()]
        except:
            return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]

    # --- 2. LIVE DATA & FUNDAMENTALS ---
    def fetch_data(self, tickers, region="US"):
        print(f"\n📥 Fetching Deep Analytics for {len(tickers)} tickers ({region})...")
        
        # LIMIT for speed (Fetching fundamentals is slow)
        # We process top 30 tickers to keep GitHub Actions from timing out.
        tickers = tickers[:30] 

        processed_list = []
        
        for t in tickers:
            try:
                # 1. Get History (Price)
                stock = yf.Ticker(t)
                hist = stock.history(period="1y")
                
                if hist.empty: continue
                
                # 2. Get Fundamentals (The "Dashboard Data")
                info = stock.info
                
                # Extract Dashboard-Specific Metrics (Safe Get with default 0)
                pe_ratio = info.get('trailingPE', 0)
                ev_ebitda = info.get('enterpriseToEbitda', 0)
                pb_ratio = info.get('priceToBook', 0)
                margins = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                debt_equity = info.get('debtToEquity', 0)
                
                # 3. Calculate RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]

                # 4. Sentiment (Simulated for visualization)
                sentiment = 0.5 
                if current_rsi < 30: sentiment = 0.8 # Bullish
                elif current_rsi > 70: sentiment = 0.2 # Bearish

                # 5. Build Row
                latest = hist.iloc[-1]
                
                df = pd.DataFrame([{
                    "Ticker": t.replace(".NS", ""),
                    "Date": latest.name.strftime('%Y-%m-%d'),
                    "Close": latest['Close'],
                    "RSI": current_rsi,
                    # --- DASHBOARD COLUMNS (Restored!) ---
                    "PE_Ratio": pe_ratio,
                    "EV_EBITDA": ev_ebitda,
                    "PB_Ratio": pb_ratio,
                    "Margins": margins,
                    "ROE": roe,
                    "Debt_Equity": debt_equity,
                    "Sentiment": sentiment,
                    "Alpha_Score": 100 - current_rsi, # Strategy Score
                    "Data_Source": "Live_YFinance"
                }])
                
                processed_list.append(df)
                print(f"✅ Processed: {t}")

            except Exception as e:
                print(f"⚠️ Failed: {t} - {e}")
                continue

        if not processed_list: return pd.DataFrame()

        return pd.concat(processed_list, ignore_index=True)
