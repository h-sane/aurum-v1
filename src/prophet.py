import pandas as pd
import numpy as np
import json
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

DATA_FILE = "data/gold_prices.csv"
OUTPUT_FILE = "data/dashboard_data.json"
PREDICTION_LOG = "data/prediction_log.json"

def load_prediction_log():
    if os.path.exists(PREDICTION_LOG):
        with open(PREDICTION_LOG, 'r') as f:
            return json.load(f)
    return {}

def save_prediction_log(log):
    with open(PREDICTION_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def run_oracle():
    print("--- 🔮 Starting Advanced Oracle ---")
    
    if not os.path.exists(DATA_FILE):
        print("❌ Error: No data found.")
        return

    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    prices = df['Gold_Price_22k'].values
    dates = df['Date'].dt.strftime('%Y-%m-%d').tolist()
    
    if len(prices) < 15:
        return

    # --- 1. PREDICTION (Holt-Winters) ---
    model = ExponentialSmoothing(prices, trend='add', damped_trend=False).fit()
    forecast_value = int(model.forecast(1)[0])
    
    # --- 2. ACCURACY TRACKING (Corrected) ---
    pred_log = load_prediction_log()
    today_str = datetime.now().strftime('%Y-%m-%d')
    # Calculate yesterday's date
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    accuracy_metric = "N/A (Tracking Started)" 
    error_diff = None 
    
    # CRITICAL FIX: Compare ACTUAL TODAY vs PREDICTED YESTERDAY
    if yesterday_str in pred_log:
        predicted_yesterday = pred_log[yesterday_str]
        actual_today = prices[-1]
        
        # Error = Actual - Predicted
        error_diff = actual_today - predicted_yesterday
        accuracy_metric = f"₹{abs(error_diff)}"
        
        print(f"🎯 Accuracy Check: Predicted (Yest) ₹{predicted_yesterday} vs Actual ₹{actual_today} (Diff: {error_diff})")
    else:
        print(f"⚠️ No prediction found for {yesterday_str}. First run?")

    # Log TOMORROW'S prediction for future checking
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    pred_log[tomorrow_str] = forecast_value
    save_prediction_log(pred_log)

    # --- 3. ADVANCED STATS ---
    # Volatility (Standard Deviation of last 7 days)
    last_7_days = prices[-7:]
    volatility = np.std(last_7_days)
    volatility_status = "High ⚡" if volatility > 500 else "Stable 🌊"
    
    # Performance
    price_today = prices[-1]
    price_yesterday = prices[-2]
    day_change = price_today - price_yesterday
    day_pct = (day_change / price_yesterday) * 100
    
    price_week_ago = prices[-7] if len(prices) >= 7 else prices[0]
    week_pct = ((price_today - price_week_ago) / price_week_ago) * 100

    # --- 4. SIGNALS (SMA & RSI) ---
    series = pd.Series(prices)
    sma_short = series.rolling(window=5).mean().iloc[-1]
    sma_long = series.rolling(window=14).mean().iloc[-1]
    
    signal = "NEUTRAL"
    if sma_short > sma_long: signal = "BULLISH 🟢"
    elif sma_short < sma_long: signal = "BEARISH 🔴"
        
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0

    # Payload
    dashboard_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": int(price_today),
        "yesterday_price": int(price_yesterday),
        "forecast_price": forecast_value,
        "accuracy_last_error": error_diff, # How off we were today
        "volatility_status": volatility_status,
        "day_change": int(day_change),
        "day_pct": round(day_pct, 2),
        "week_pct": round(week_pct, 2),
        "trend_signal": signal,
        "rsi": round(current_rsi, 2),
        "history": {
            "dates": dates[-30:],
            "prices": [int(p) for p in prices[-30:]]
        }
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
        
    print(f"✅ Advanced Analysis Complete.")

if __name__ == "__main__":
    run_oracle()