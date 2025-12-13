import yfinance as yf
import pandas as pd
import requests
import io
import datetime
import numpy as np

class DataEngine:
    def __init__(self):
        print("⚙️ Initializing Institutional Data Engine...")

    # --- 1. DYNAMIC TICKER FETCHING (With Disguise) ---
    def get_sp500_tickers(self):
        print("🔍 Scanning US Market (S&P 500)...")
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            # DISGUISE: Pretend to be Chrome Browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            r = requests.get(url, headers=headers)
            
            # Read HTML from the text response
            tables = pd.read_html(io.StringIO(r.text))
            tickers = tables[0]['Symbol'].tolist()
            
            # Clean Tickers
            clean_tickers = [t.replace('.', '-') for t in tickers]
            print(f"✅ SUCCESS: Found {len(clean_tickers)} US Tickers.")
            return clean_tickers
            
        except Exception as e:
            print(f"❌ S&P 500 SCAN FAILED: {e}")
            print("⚠️ Using Fallback List (5 Stocks Only)")
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

    def get_nifty50_tickers(self):
        print("🔍 Scanning India Market (Nifty 50)...")
        try:
            url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            s = requests.get(url, headers=headers).content
            df = pd.read_csv(io.StringIO(s.decode('utf-8')))
            
            tickers = [f"{x}.NS" for x in df['Symbol'].tolist()]
            print(f"✅ SUCCESS: Found {len(tickers)} India Tickers.")
            return tickers
            
        except Exception as e:
            print(f"❌ NIFTY 50 SCAN FAILED: {e}")
            return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]

    # --- 2. LIVE DATA & FUNDAMENTALS ---
    def fetch_data(self, tickers, region="US"):
        print(f"\n📥 Fetching Analytics for {len(tickers)} tickers ({region})...")
        
        # PROCESSING ALL TICKERS (Unlimited)
        processed_list = []
        
        for t in tickers:
            try:
                stock = yf.Ticker(t)
                
                # Fetch just 3 months to be fast
                hist = stock.history(period="3mo")
                if hist.empty: continue
                
                info = stock.info
                
                # Extract Fundamentals
                pe_ratio = info.get('trailingPE', 0)
                ev_ebitda = info.get('enterpriseToEbitda', 0)
                pb_ratio = info.get('priceToBook', 0)
                margins = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                debt_equity = info.get('debtToEquity', 0)
                
                # RSI Calc
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]

                sentiment = 0.5 
                if current_rsi < 30: sentiment = 0.8
                elif current_rsi > 70: sentiment = 0.2

                # Build Row
                latest = hist.iloc[-1]
                
                df = pd.DataFrame([{
                    "Ticker": t.replace(".NS", ""),
                    "Date": latest.name.strftime('%Y-%m-%d'),
                    "Close": latest['Close'],
                    "RSI": current_rsi,
                    "PE_Ratio": pe_ratio,
                    "EV_EBITDA": ev_ebitda,
                    "PB_Ratio": pb_ratio,
                    "Margins": margins,
                    "ROE": roe,
                    "Debt_Equity": debt_equity,
                    "Sentiment": sentiment,
                    "Alpha_Score": 100 - current_rsi,
                    "Data_Source": "Live_YFinance"
                }])
                
                processed_list.append(df)
                
                # Progress Log
                if len(processed_list) % 20 == 0:
                    print(f"   Processed {len(processed_list)} / {len(tickers)}")

            except Exception as e:
                continue

        if not processed_list: return pd.DataFrame()

        return pd.concat(processed_list, ignore_index=True)
