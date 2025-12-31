import yfinance as yf
import pandas as pd
import numpy as np
import requests
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

# Suppress warnings for cleaner logs
warnings.filterwarnings("ignore")

# --- CONFIGURATION ---
US_SOURCE = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
UK_SOURCE = "https://en.wikipedia.org/wiki/FTSE_100_Index"
# Nifty 50 Fallback list (Reliable)
INDIA_TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LICI.NS", "HINDUNILVR.NS", "LT.NS", "BAJFINANCE.NS", "MARUTI.NS", "AXISBANK.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "KOTAKBANK.NS", "TATASTEEL.NS"]

def get_us_tickers():
    try:
        table = pd.read_html(US_SOURCE)[0]
        return [t.replace('.', '-') for t in table['Symbol'].tolist()]
    except: return []

def get_uk_tickers():
    try:
        # FTSE 100 tickers usually need '.L' for Yahoo Finance
        table = pd.read_html(UK_SOURCE)[4] # Table index varies, usually 3 or 4
        # Fallback if table fetch fails or structure changes
        if 'Ticker' not in table.columns:
            table = pd.read_html(UK_SOURCE)[3]
        
        tickers = table['Ticker'].tolist()
        return [f"{t}.L" for t in tickers]
    except: 
        print("⚠️ Used Fallback UK List")
        return ["HSBA.L", "SHEL.L", "AZN.L", "BP.L", "ULVR.L", "RIO.L", "GSK.L", "DGE.L", "BATS.L", "GLEN.L"]

def get_india_tickers():
    return INDIA_TICKERS

# --- SARIMA PREDICTION MODEL ---
def run_sarima_forecast(history):
    """
    Runs a simplified SARIMA model on the last 6 months of data.
    Returns the predicted price for the next trading day.
    """
    try:
        # We use a fixed order (1,1,1) to keep it fast for GitHub Actions
        # A full auto_arima search would take hours for 20 stocks.
        model = SARIMAX(history, order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))
        model_fit = model.fit(disp=False)
        forecast = model_fit.forecast(steps=5) # Predict next 5 days
        return round(forecast.iloc[-1], 2) # Return the 5-day target
    except:
        return np.nan

def analyze_market(tickers, region_name):
    print(f"🌍 Analyzing {region_name} Market...")
    
    if not tickers: return

    # 1. BATCH DOWNLOAD (1 Year data for SARIMA)
    data = yf.download(tickers, period="1y", group_by='ticker', progress=False)
    
    candidates = []

    # 2. SCREENING PHASE (The "Blend" Strategy)
    print("   > Running Fundamental & Technical Screen...")
    for ticker in tickers:
        try:
            df = data[ticker]
            if df.empty or len(df) < 50: continue

            # Technicals
            close_price = df['Close'].iloc[-1]
            
            # Fundamentals (Fetching individually is slow, but necessary for P/B & Revenue)
            # To speed up, we accept that some fields might be missing
            stock = yf.Ticker(ticker)
            info = stock.info
            
            pe = info.get('trailingPE', 100) # High default = bad
            pb = info.get('priceToBook', 10) # High default = bad
            eps = info.get('trailingEps', 0)
            rev_growth = info.get('revenueGrowth', 0)
            
            # --- BLEND SCORE LOGIC ---
            # Value: Low PE (<25 is good), Low PB (<3 is good)
            # Growth: High Rev Growth, Positive EPS
            
            # Score 0-100 (Higher is better)
            score_pe = max(0, 100 - (pe * 2))      # PE 20 = 60pts, PE 50 = 0pts
            score_pb = max(0, 100 - (pb * 10))     # PB 2 = 80pts, PB 10 = 0pts
            score_growth = min(100, (rev_growth * 100) * 2) # 10% growth = 20pts
            
            final_score = (score_pe * 0.4) + (score_pb * 0.3) + (score_growth * 0.3)
            
            # Basic Filter: Only keep "decent" stocks to run SARIMA on
            if final_score > 40:
                candidates.append({
                    "Ticker": ticker,
                    "Close": float(close_price),
                    "PE_Ratio": round(pe, 2),
                    "PB_Ratio": round(pb, 2),
                    "Rev_Growth": round(rev_growth * 100, 1),
                    "Blend_Score": round(final_score, 1),
                    "History": df['Close'] # Keep history for SARIMA
                })
                
        except: continue

    # 3. RANKING & SELECTION
    df_candidates = pd.DataFrame(candidates)
    if df_candidates.empty: return

    # Sort by Blend Score and take Top 15 Finalists
    top_picks = df_candidates.sort_values(by="Blend_Score", ascending=False).head(15)
    
    # 4. PREDICTION PHASE (SARIMA)
    print(f"   > Running SARIMA AI Models on top {len(top_picks)} picks...")
    
    predictions = []
    for index, row in top_picks.iterrows():
        # Run heavy math only on finalists
        predicted_price = run_sarima_forecast(row['History'])
        upside = ((predicted_price - row['Close']) / row['Close']) * 100
        
        predictions.append(round(upside, 2))
    
    top_picks['SARIMA_Forecast_5D'] = predictions
    
    # Final cleanup (Remove history column to save CSV space)
    del top_picks['History']
    
    # Save Top 10
    filename = f"{region_name}_rankings.csv"
    top_picks.head(10).to_csv(filename, index=False)
    print(f"✅ Saved Top 10 for {region_name} to {filename}")

def main():
    print("🚀 IronGate Global Engine Starting...")
    
    analyze_market(get_us_tickers(), "US")
    analyze_market(get_india_tickers(), "IN")
    analyze_market(get_uk_tickers(), "UK")
    
    print("🏁 Global Analysis Complete.")

if __name__ == "__main__":
    main()
