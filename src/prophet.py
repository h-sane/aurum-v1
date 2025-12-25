import pandas as pd
import numpy as np
import json
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import datetime
import warnings

# Suppress statsmodels convergence warnings for cleaner output
warnings.filterwarnings("ignore")

DATA_FILE = "data/gold_prices.csv"
OUTPUT_FILE = "data/dashboard_data.json"

def run_oracle():
    print("--- 🔮 Starting Oracle Prediction Service ---")
    
    # 1. Load Data
    if not os.path.exists(DATA_FILE):
        print("❌ Error: No data found. Run backfill.py first.")
        return

    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Extract purely the price series for modeling
    prices = df['Gold_Price_22k'].values
    dates = df['Date'].dt.strftime('%Y-%m-%d').tolist()
    
    if len(prices) < 15:
        print(f"⚠️ Not enough data to train ML model. Need 15+, have {len(prices)}.")
        return

    # 2. Train Holt-Winters Model (Exponential Smoothing)
    # We use 'additive' trend because gold prices don't grow exponentially in 90 days.
    print(f"🧠 Training Holt-Winters model on {len(prices)} data points...")
    model = ExponentialSmoothing(
        prices, 
        trend='add', 
        damped_trend=False, 
        seasonal=None
    ).fit()
    
    # Forecast T+1 (Tomorrow)
    forecast_value = int(model.forecast(1)[0])
    
    # 3. Calculate Technical Indicators (SMA + RSI)
    series = pd.Series(prices)
    
    # SMA (Simple Moving Average) Crossover
    short_window = 5
    long_window = 14
    sma_short = series.rolling(window=short_window).mean()
    sma_long = series.rolling(window=long_window).mean()
    
    latest_short = sma_short.iloc[-1]
    latest_long = sma_long.iloc[-1]
    
    # Signal Logic
    signal = "NEUTRAL"
    if latest_short > latest_long:
        signal = "BULLISH (Up Trend) 🟢"
    elif latest_short < latest_long:
        signal = "BEARISH (Down Trend) 🔴"
        
    # RSI (Relative Strength Index) - 14 Day
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    # Handle NaN at start of series
    current_rsi = rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0

    # 4. Generate Dashboard Payload
    dashboard_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": int(prices[-1]),
        "forecast_price": forecast_value,
        "price_change": int(prices[-1] - prices[-2]),
        "trend_signal": signal,
        "rsi": round(current_rsi, 2),
        "history": {
            # Take last 30 days for the graph
            "dates": dates[-30:],
            "prices": [int(p) for p in prices[-30:]]
        }
    }
    
    # 5. Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
        
    print(f"✅ Prediction Complete: Tomorrow ₹{forecast_value}")
    print(f"📊 Market Signal: {signal} | RSI: {current_rsi:.1f}")
    print(f"💾 Dashboard Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_oracle()