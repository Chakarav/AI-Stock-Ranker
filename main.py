import yfinance as yf
import pandas as pd
import numpy as np
import requests
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

warnings.filterwarnings("ignore")

# --- CONFIGURATION & BACKUPS ---
BACKUP_US = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "CVX", "MRK", "ABBV", "KO", "PEP", "BAC", "COST", "MCD", "DIS", "CSCO", "ACN", "NFLX", "LIN", "AMD"]
BACKUP_UK = ["SHELL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L", "DGE.L", "RIO.L", "BATS.L", "GLEN.L", "GSK.L", "REL.L", "LSEG.L", "VOD.L", "LLOY.L", "BARC.L", "NG.L", "PRU.L", "TSCO.L", "STAN.L", "RR.L"]
BACKUP_INDIA = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS", "HINDUNILVR.NS", "LT.NS", "BAJFINANCE.NS", "MARUTI.NS", "AXISBANK.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "KOTAKBANK.NS", "TATASTEEL.NS", "M&M.NS", "ADANIENT.NS", "ADANIPORTS.NS", "NTPC.NS", "ONGC.NS"]

def get_us_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        return [t.replace('.', '-') for t in df['Symbol'].tolist()]
    except:
        return BACKUP_US

def get_uk_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/FTSE_100_Index"
        tables = pd.read_html(url)
        for i in range(3, 6):
            if 'Ticker' in tables[i].columns:
                return [f"{t}.L" for t in tables[i]['Ticker'].tolist()]
        return BACKUP_UK
    except: 
        return BACKUP_UK

def get_india_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/NIFTY_50"
        tables = pd.read_html(url)
        df = tables[1] 
        if 'Symbol' not in df.columns:
            df = tables[2]
        return [f"{t}.NS" for t in df['Symbol'].tolist()]
    except:
        return BACKUP_INDIA

def run_sarima_forecast(history):
    try:
        model = SARIMAX(history, order=(1, 1, 1)) 
        model_fit = model.fit(disp=False)
        forecast = model_fit.forecast(steps=7)
        return forecast.iloc[-1]
    except:
        return np.nan

def analyze_market(tickers, region_name):
    print(f"🌍 Analyzing {region_name} Market ({len(tickers)} tickers)...")
    if not tickers: return

    data = yf.download(tickers, period="1y", group_by='ticker', progress=False, threads=True)
    candidates = []

    for ticker in tickers:
        try:
            if len(tickers) == 1: df = data
            else:
                if ticker not in data.columns.levels[0]: continue
                df = data[ticker]
            
            if df.empty or len(df) < 50: continue

            close_price = float(df['Close'].iloc[-1])
            
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                pe = info.get('trailingPE', 50) 
                pb = info.get('priceToBook', 5)
                rev_growth = info.get('revenueGrowth', 0)
            except:
                pe, pb, rev_growth = 50, 5, 0 

            # --- BLEND SCORE LOGIC (PATCHED FOR NEGATIVE NUMBERS) ---
            
            # 1. PE Score (If PE is negative/loss, score is 0)
            if pe < 0: 
                score_pe = 0
            else:
                score_pe = max(0, 100 - (pe * 2))
            
            # 2. PB Score (If PB is negative, score is 0 - FIX FOR MCD)
            if pb < 0:
                score_pb = 0
            else:
                score_pb = max(0, 100 - (pb * 6)) 
            
            # 3. Growth Score (Strict Cap 100)
            raw_growth = (rev_growth * 100) * 3
            score_growth = min(100, max(0, raw_growth)) 
            
            final_score = (score_pe * 0.4) + (score_pb * 0.3) + (score_growth * 0.3)
            final_score = min(100, max(0, final_score))
            
            if final_score > 30: 
                candidates.append({
                    "Ticker": ticker,
                    "Close": round(close_price, 2),
                    "PE_Ratio": round(pe, 2),
                    "Blend_Score": round(final_score, 1),
                    "History": df['Close']
                })
        except: continue

    df_candidates = pd.DataFrame(candidates)
    if not df_candidates.empty:
        top_picks = df_candidates.sort_values(by="Blend_Score", ascending=False).head(10)
        
        predictions = []
        for index, row in top_picks.iterrows():
            pred_price = run_sarima_forecast(row['History'])
            if pd.notna(pred_price):
                upside = ((pred_price - row['Close']) / row['Close']) * 100
            else:
                upside = 0.0
            predictions.append(round(upside, 2))
        
        top_picks['SARIMA_Forecast_5D'] = predictions
        del top_picks['History']
        
        # Saving as _Market_Data to keep things clean
        filename = f"{region_name}_Market_Data.csv"
        top_picks.to_csv(filename, index=False)
        print(f"✅ Saved New Data: {filename}")

def main():
    analyze_market(get_us_tickers(), "US")
    analyze_market(get_india_tickers(), "IN")
    analyze_market(get_uk_tickers(), "UK")

if __name__ == "__main__":
    main()
