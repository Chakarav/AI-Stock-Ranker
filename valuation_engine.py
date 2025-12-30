import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

# Suppress SARIMA warnings for cleaner output
warnings.filterwarnings("ignore")

class ValuationEngine:
    def __init__(self, ticker, current_price, sector, quarterly_data):
        """
        ticker: Stock Symbol
        current_price: Live Price
        sector: Sector string (e.g., "Financials", "Technology")
        quarterly_data: Pandas Series of quarterly metric (EPS or Book Value) sorted by date
        """
        self.ticker = ticker
        self.current_price = current_price
        self.sector = sector
        self.data = quarterly_data.sort_index()

    def get_sarima_forecast(self, steps=4):
        """
        Uses SARIMA to predict the next 4 quarters of fundamentals.
        Seasonality (s) = 4 because data is Quarterly.
        """
        try:
            # Order (1,1,1) x (1,1,1,4) is a robust default for quarterly financials
            model = SARIMAX(self.data, 
                            order=(1, 1, 1), 
                            seasonal_order=(1, 1, 1, 4),
                            enforce_stationarity=False, 
                            enforce_invertibility=False)
            
            results = model.fit(disp=False)
            forecast = results.get_forecast(steps=steps)
            return forecast.predicted_mean.sum() # Return Annualized Forward Projection
        except Exception as e:
            print(f"SARIMA Error for {self.ticker}: {e}")
            return None

    def analyze(self):
        """
        Main logic router: Decides WHICH metric to use based on Sector.
        """
        # --- SECTOR LOGIC SWITCH ---
        is_financial = self.sector in ["Financial Services", "Banks", "Insurance"]
        
        # 1. Select the Right Metric
        if is_financial:
            # BANKS: Use Price-to-Book (P/B) Logic
            # Note: For banks, 'quarterly_data' passed in should be Book Value Per Share
            metric_name = "Book Value"
            forward_projection = self.get_sarima_forecast()
            
            if not forward_projection or forward_projection <= 0:
                return {"decision": "SKIP", "reason": "Data Error or Negative BV"}
                
            forward_valuation = self.current_price / forward_projection # Forward P/B
            threshold = 2.0 # Banks shouldn't usually trade above 2x Book
            
        else:
            # NON-BANKS: Use Price-to-Earnings (P/E) Logic
            # Note: 'quarterly_data' passed in should be EPS
            metric_name = "EPS"
            forward_projection = self.get_sarima_forecast()
            
            if not forward_projection or forward_projection <= 0:
                return {"decision": "SKIP", "reason": "Negative Earnings Projection"}
                
            forward_valuation = self.current_price / forward_projection # Forward P/E
            threshold = 25.0 # General threshold (can be dynamic)

        # 2. GARP Calculation (Growth At Reasonable Price)
        # Compare Forward Projection vs Trailing (Last 4 Qtrs)
        trailing_metric = self.data.tail(4).sum()
        growth_rate = ((forward_projection - trailing_metric) / trailing_metric) * 100
        
        peg_ratio = 999
        if growth_rate > 0:
            peg_ratio = forward_valuation / growth_rate

        # 3. Final Decision Logic
        decision = "HOLD"
        reason = f"Fair Value. Forward {metric_name}: {round(forward_projection, 2)}"
        
        # BUY CRITERIA: Undervalued (PEG < 1.5) OR Cheap Valuation
        if peg_ratio < 1.5 and growth_rate > 10:
            decision = "BUY"
            reason = f"GARP Opportunity! PEG: {round(peg_ratio, 2)} with {round(growth_rate)}% Growth"
        
        # SELL CRITERIA
        elif forward_valuation > threshold:
            decision = "SELL"
            reason = f"Overvalued. Forward {metric_name} Multiple: {round(forward_valuation, 2)}"

        return {
            "Ticker": self.ticker,
            "Sector": self.sector,
            "Decision": decision,
            "Reason": reason,
            "Projected_Growth": f"{round(growth_rate, 2)}%",
            "Forward_Valuation": round(forward_valuation, 2),
            "Metric_Used": "Forward P/B" if is_financial else "Forward P/E"
        }
