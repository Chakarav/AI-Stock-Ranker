import pandas as pd
from data_engine import DataEngine

# --- ALPHA STRATEGY ---
def calculate_alpha(df):
    """
    Real Strategy:
    1. Calculate RSI (Relative Strength Index)
    2. Rank stocks: Low RSI = High Alpha (Buying the Dip)
    """
    print("🧠 Running AI Analysis...")
    results = []
    
    for ticker in df['Ticker'].unique():
        try:
            subset = df[df['Ticker'] == ticker].copy()
            subset = subset.sort_values(by="Date")
            
            # Calculate RSI (14-day)
            delta = subset['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            latest = subset.iloc[-1]
            
            results.append({
                "Ticker": ticker,
                "Close": round(latest['Close'], 2),
                "RSI": round(rsi.iloc[-1], 2),
                "Alpha_Score": round(100 - rsi.iloc[-1], 2), # Simple Score
                "Data_Source": "Live"
            })
        except:
            continue
            
    # Sort by Best Opportunity (Highest Alpha Score)
    final_df = pd.DataFrame(results).sort_values(by="Alpha_Score", ascending=False)
    return final_df

# --- PIPELINE ---
def run_pipeline():
    engine = DataEngine()
    
    # 1. INDIA (NIFTY 50)
    print("\n🇮🇳 FETCHING NIFTY 50 LIST...")
    nifty_tickers = engine.get_nifty50_tickers()
    in_data = engine.fetch_data(nifty_tickers, region="IN")
    
    if not in_data.empty:
        ranked_in = calculate_alpha(in_data)
        ranked_in.to_csv("IN_rankings.csv", index=False)
        print("✅ SAVED: IN_rankings.csv")

    # 2. USA (S&P 500)
    print("\n🇺🇸 FETCHING S&P 500 LIST...")
    sp500_tickers = engine.get_sp500_tickers()
    us_data = engine.fetch_data(sp500_tickers, region="US")
    
    if not us_data.empty:
        ranked_us = calculate_alpha(us_data)
        ranked_us.to_csv("US_rankings.csv", index=False)
        print("✅ SAVED: US_rankings.csv")

if __name__ == "__main__":
    run_pipeline()
