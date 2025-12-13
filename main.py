import pandas as pd
import numpy as np
from data_engine import DataEngine

# --- CONFIGURATION ---
US_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC"]
IN_TICKERS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC"]

# --- ALPHA CALCULATION LOGIC ---
def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_alpha(df):
    """
    Simple ranking logic:
    1. Calculate RSI
    2. Assign Score (Lower RSI = Higher Score, buying the dip)
    """
    print("🧠 Calculating Alpha Scores...")
    scored_tickers = []
    
    # Process each ticker individually
    for ticker in df['Ticker'].unique():
        try:
            subset = df[df['Ticker'] == ticker].copy()
            subset = subset.sort_values(by="Date") # Ensure time order
            
            # Calculate Indicators
            subset['RSI'] = calculate_rsi(subset['Close'])
            
            # Get Latest Values
            latest = subset.iloc[-1]
            rsi_val = latest['RSI']
            close_val = latest['Close']
            
            # Simple Scoring Logic (Example)
            score = 50
            if rsi_val < 30: score += 20 # Oversold (Buy signal)
            elif rsi_val > 70: score -= 20 # Overbought (Sell signal)
            
            scored_tickers.append({
                "Ticker": ticker,
                "Close": close_val,
                "RSI": rsi_val,
                "Alpha_Score": score,
                "Data_Source": "Live_YFinance"
            })
        except Exception as e:
            print(f"⚠️ Error scoring {ticker}: {e}")
            
    return pd.DataFrame(scored_tickers).sort_values(by="Alpha_Score", ascending=False)

# --- MAIN PIPELINE ---
def run_pipeline():
    engine = DataEngine()
    
    # 1. RUN INDIA
    print("\n🇮🇳 STARTING INDIA PIPELINE...")
    in_data = engine.fetch_data(IN_TICKERS, region="IN")
    if not in_data.empty:
        ranked_in = calculate_alpha(in_data)
        ranked_in.to_csv("IN_rankings.csv", index=False)
        print("✅ SAVED: IN_rankings.csv")
        print(ranked_in.head(3)) # Show preview

    # 2. RUN USA
    print("\n🇺🇸 STARTING US PIPELINE...")
    us_data = engine.fetch_data(US_TICKERS, region="US")
    if not us_data.empty:
        ranked_us = calculate_alpha(us_data)
        ranked_us.to_csv("US_rankings.csv", index=False)
        print("✅ SAVED: US_rankings.csv")
        print(ranked_us.head(3)) # Show preview

if __name__ == "__main__":
    run_pipeline()
