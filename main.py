import yfinance as yf
import pandas as pd
from valuation_engine import ValuationEngine  # Import our new brain

# 1. Define your watchlist
# Ensure you have a mix of sectors to test the logic
tickers = [
    "HDFCBANK.NS",  # Bank (Should use P/B)
    "TCS.NS",       # Tech (Should use P/E)
    "TATAMOTORS.NS",# Auto (Should use P/E)
    "SBIN.NS",      # Bank (Should use P/B)
    "INFY.NS"       # Tech (Should use P/E)
]

print("--- STARTING AI INVESTMENT ANALYSIS ---")
print("Loading SARIMA models and Sector Logic...\n")

results_list = []

for symbol in tickers:
    try:
        print(f"Analyzing {symbol}...")
        stock = yf.Ticker(symbol)
        
        # A. Fetch Basic Info
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPreviousClose', 0))
        sector = info.get('sector', 'Unknown')
        
        # B. Data Extraction Strategy
        quarterly_data = None
        
        # CHECK: Is it a Bank?
        if sector in ["Financial Services", "Banks", "Insurance", "Banking"]:
            # STRATEGY: Get Book Value
            # We approximate Book Value per Share roughly as: (Total Equity) / (Shares Outstanding)
            bs = stock.quarterly_balance_sheet
            
            # Different APIs label equity differently, check for common names
            equity_row = None
            if "Total Stockholder Equity" in bs.index:
                equity_row = bs.loc["Total Stockholder Equity"]
            elif "Stockholders Equity" in bs.index:
                equity_row = bs.loc["Stockholders Equity"]
            elif "Total Equity Gross Minority Interest" in bs.index:
                 equity_row = bs.loc["Total Equity Gross Minority Interest"]
                 
            if equity_row is not None:
                shares = info.get('sharesOutstanding', 1)
                # Calculate Book Value Per Share (BVPS) series
                quarterly_data = equity_row / shares
                
        else:
            # STRATEGY: Get EPS
            fin = stock.quarterly_financials
            if "Basic EPS" in fin.index:
                quarterly_data = fin.loc["Basic EPS"]
            elif "Diluted EPS" in fin.index:
                quarterly_data = fin.loc["Diluted EPS"]

        # C. Run the Engine
        if quarterly_data is not None and not quarterly_data.empty:
            # Clean data: Remove NaNs and ensure float
            quarterly_data = quarterly_data.astype(float).dropna()
            
            # Initialize Engine
            engine = ValuationEngine(symbol, current_price, sector, quarterly_data)
            report = engine.analyze()
            results_list.append(report)
        else:
            print(f"-> Skipped {symbol}: Could not retrieve clean quarterly data.")

    except Exception as e:
        print(f"-> Error analyzing {symbol}: {e}")

# --- DISPLAY RESULTS ---
print("\n" + "="*50)
print("FINAL INVESTMENT REPORT")
print("="*50)

# Convert to DataFrame for a nice table display
if results_list:
    df_results = pd.DataFrame(results_list)
    # Reorder columns for readability
    cols = ["Ticker", "Decision", "Reason", "Projected_Growth", "Forward_Multiple", "Metric_Type"]
    print(df_results[cols].to_string(index=False))
else:
    print("No results generated.")
