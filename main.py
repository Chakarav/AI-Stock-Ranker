import yfinance as yf
import pandas as pd
import numpy as np
import requests
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

warnings.filterwarnings("ignore")

# --- CONFIGURATION ---
# Backup lists ensure the robot NEVER fails even if Wikipedia is down
BACKUP_US = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "CVX", "MRK", "ABBV", "KO", "PEP", "BAC", "COST", "MCD", "DIS", "CSCO", "ACN", "NFLX", "LIN", "AMD"]
BACKUP_UK = ["SHELL.L", "AZN.L", "HSBA.L", "ULVR.L", "BP.L", "DGE.L", "RIO.L", "BATS.L", "GLEN.L", "GSK.L", "REL.L", "LSEG.L", "VOD.L", "LLOY.L", "BARC.L", "NG.L", "PRU.L", "TSCO.L", "STAN.L", "RR.L"]
INDIA_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS", "HINDUNILVR.NS", "LT.NS", "BAJFINANCE.NS", "MARUTI.NS", "AXISBANK.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "KOTAKBANK.NS", "TATASTEEL.NS", "M&M.NS", "ADANIENT.NS", "ADANIPORTS.NS", "NTPC.NS", "ONGC.NS"]

def get_us_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        return [t.replace('.', '-') for t in df['Symbol'].tolist()]
    except:
        print("⚠️ US Scraper Failed. Using Backup List.")
        return BACKUP_US

def get_uk_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/FTSE_100_Index"
        tables = pd.read_html(url)
        # Check tables 3 or 4 for tickers
        for i in range(3, 6):
            if 'Ticker' in tables[i].columns:
                return [f"{t}.L" for t in tables[i]['Ticker'].tolist()]
        raise Exception("Table not found")
    except: 
        print("⚠️ UK Scraper Failed. Using Backup List.")
        return BACKUP_UK

def get_india_tickers():
    return INDIA_TICKERS

# --- SARIMA PREDICTION ---
def run_sarima_forecast(history):
    try:
        # Simplified Model for Speed: AR(1)
        model = SARIMAX(history, order=(1, 1, 0)) 
        model_fit = model.fit(disp=False)
        forecast = model_fit.forecast(steps=5) 
        return round(forecast.iloc[-1], 2)
    except:
        return np.nan

def analyze_market(tickers, region_name):
    print(f"🌍 Analyzing {region_name} Market ({len(tickers)} tickers)...")
    
    if not tickers: 
        print(f"❌ No tickers found for {region_name}")
        return

    # 1. BATCH DOWNLOAD
    data = yf.download(tickers, period="6mo", group_by='ticker', progress=False, threads=True)
    
    candidates = []

    # 2. SCREENING
    print("   > Screening Stocks...")
    for ticker in tickers:
        try:
            # Handle Single Ticker vs Multi Ticker Structure
            if len(tickers) == 1:
                df = data
            else:
                if ticker not in data.columns.levels[0]: continue
                df = data[ticker]
            
            if df.empty or len(df) < 50: continue

            # Technicals
            close_price = float(df['Close'].iloc[-1])
            
            # Fundamentals (Fetching individually)
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                pe = info.get('trailingPE', 50) 
                pb = info.get('priceToBook', 5)
                rev_growth = info.get('revenueGrowth', 0)
            except:
                pe, pb, rev_growth = 50, 5, 0 # Defaults

            # --- BLEND SCORE ---
            score_pe = max(0, 100 - (pe * 2))
            score_pb = max(0, 100 - (pb * 15))
            score_growth = min(100, (rev_growth * 100) * 3)
            
            final_score = (score_pe * 0.4) + (score_pb * 0.3) + (score_growth * 0.3)
            
            if final_score > 30: # Lower threshold to ensure we get results
                candidates.append({
                    "Ticker": ticker,
                    "Close": round(close_price, 2),
                    "PE_Ratio": round(pe, 2),
                    "Blend_Score": round(final_score, 1),
                    "History": df['Close']
                })
        except Exception as e: continue

    # 3. RANKING
    df_candidates = pd.DataFrame(candidates)
    if df_candidates.empty: 
        print(f"⚠️ No candidates found for {region_name}")
        return

    top_picks = df_candidates.sort_values(by="Blend_Score", ascending=False).head(10)
    
    # 4. PREDICTION
    print(f"   > Running AI Prediction on top {len(top_picks)}...")
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
    
    filename = f"{region_name}_rankings.csv"
    top_picks.to_csv(filename, index=False)
    print(f"✅ Saved {filename}")

def main():
    print(" IronGate Global Engine Starting...")
    analyze_market(get_us_tickers(), "US")
    analyze_market(get_india_tickers(), "IN")
    analyze_market(get_uk_tickers(), "UK")
    print("🏁 Analysis Complete.")

if __name__ == "__main__":
    main()
