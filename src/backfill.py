import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np

# CONFIG
CSV_PATH = "data/gold_prices.csv"
TARGET_PRICE_10G_TODAY = 127650 # Based on your last successful run (Anchor Point)

def run_backfill():
    print("--- ⏳ Starting Proxy Backfill (Yahoo Finance) ---")
    print("    Reason: Direct scraping is blocked. Switching to Global Proxy.")

    # 1. Download Global Data (5 Years)
    # GC=F : Gold Futures (USD per Ounce)
    # INR=X : USD to INR Exchange Rate
    print("📡 Fetching Global Market Data...")
    tickers = ["GC=F", "INR=X"]
    data = yf.download(tickers, period="5y", progress=False)
    
    # Handle MultiIndex headers (yfinance update)
    if isinstance(data.columns, pd.MultiIndex):
        df = data['Close'].reset_index()
    else:
        df = data.reset_index()

    # 2. Clean & Merge
    # We need 'Date', 'GC=F', 'INR=X'
    df['Date'] = df['Date'].dt.date
    df = df.rename(columns={"GC=F": "Gold_USD_Oz", "INR=X": "USD_INR"})
    
    # Forward fill missing data (weekends/holidays)
    df = df.ffill().bfill()

    # 3. The "Proxy Formula"
    # Step A: Convert Oz to Grams (1 Troy Oz = 31.1035 grams)
    # Step B: Convert USD to INR
    # Step C: Calculate "Raw" Gold Price per 10g in INR
    
    # Raw_INR_10g = (Price_USD_Oz / 31.1035) * USD_INR * 10
    df['Raw_INR_10g'] = (df['Gold_USD_Oz'] / 31.1035) * df['USD_INR'] * 10

    # 4. Calibration (The "Chennai Premium")
    # We compare the 'Raw' price today with your 'Real' price (₹127,650)
    # and find the "Import Duty + Premium" factor.
    
    latest_raw = df['Raw_INR_10g'].iloc[-1]
    calibration_factor = TARGET_PRICE_10G_TODAY / latest_raw
    
    print(f"🧮 Calibration Factor: {calibration_factor:.4f} (Implies Taxes + Premium)")
    
    # Apply Factor to entire history to get "Synthetic Chennai Prices"
    df['Gold_Price_22k'] = (df['Raw_INR_10g'] * calibration_factor).astype(int)

    # 5. Final Cleanup
    final_df = df[['Date', 'Gold_Price_22k', 'USD_INR']]
    final_df = final_df.sort_values("Date")
    
    # Save
    final_df.to_csv(CSV_PATH, index=False)
    
    print(f"✅ Generated {len(final_df)} days of Synthetic History.")
    print(f"💾 Saved to {CSV_PATH}")
    print("📊 Sample Data:")
    print(final_df.tail(3))

if __name__ == "__main__":
    run_backfill()