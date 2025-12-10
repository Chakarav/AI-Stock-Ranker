# src/backtest.py
import pandas as pd
import numpy as np

def run_backtest(market='IN'):
    print(f"--- Running Backtest for {market} Market ---")
    
    file_path = f"data/{market}_processed_data.csv"
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("Error: Data file not found.")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    # STRATEGY LOGIC:
    # Buy if RSI < 30 (Oversold) AND Price > SMA 200 (Uptrend)
    # I changed RSI < 40 to < 30 to be safer
    df['Signal'] = np.where(
        (df['RSI'] < 30) & (df['Close'] > df['SMA_200']), 
        1, 0
    )
    
    df['Strategy_Return'] = df['Signal'] * df['Return_1M']

    # Calculate Cumulative Returns for the Chart
    # Group by Date to get the average return of the portfolio for that day
    daily_data = df.groupby('Date').agg({
        'Return_1M': 'mean',
        'Strategy_Return': 'mean'
    }).reset_index()

    # Calculate Cumulative Sum (Equity Curve)
    daily_data['Market_Cumulative'] = daily_data['Return_1M'].cumsum()
    daily_data['Strategy_Cumulative'] = daily_data['Strategy_Return'].cumsum()

    # Save for Dashboard
    daily_data.to_csv(f"data/{market}_backtest_curve.csv", index=False)
    print("Backtest data saved.")

    total_return = daily_data['Strategy_Cumulative'].iloc[-1]
    print(f"Total Strategy Return: {total_return:.2%}")