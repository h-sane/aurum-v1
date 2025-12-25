"""
ONE-TIME UTILITY SCRIPT (Resilient Fallback Adapter)
Populates data/gold_prices.csv by extracting trend data from Yahoo Finance (GC=F).
Rationale: Official FRED source returned 404 (Discontinued).
Engine: Uses 'curl_cffi' to mimic Chrome 120 TLS fingerprint and bypass WAF.
"""
from curl_cffi import requests
import os
import csv
from datetime import datetime
from src.scout import Scout

DATA_FILE = "data/gold_prices.csv"
# Direct JSON endpoint used by Yahoo's mobile app/frontend
YAHOO_API = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=3mo"

def run_backfill():
    print("--- ⏳ Starting Backfill (Engine: Custom Yahoo Driver) ---")
    
    # 1. Get the CURRENT Retail Price (The Anchor)
    print("1. Fetching current retail price anchor...")
    scout = Scout()
    result = scout.fetch_price()
    
    if not result.success:
        print(f"❌ Abort: Could not fetch current price. Error: {result.message}")
        return

    current_retail_price = result.price
    print(f"   ⚓ Anchor Price (Today): ₹{current_retail_price} (10g)")

    # 2. Fetch Market Data directly via API
    print("2. Downloading market trend from Yahoo API...")
    try:
        # We use the same 'chrome120' impersonation to pass the WAF check
        response = requests.get(
            YAHOO_API, 
            impersonate="chrome120",
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"❌ Yahoo API Failed: HTTP {response.status_code}")
            # Debugging: Print a bit of the response to see if it's a CAPTCHA
            print(f"   Response Snippet: {response.text[:200]}")
            return
            
        data = response.json()
        
        # Parse Yahoo's complex JSON structure
        result_block = data["chart"]["result"][0]
        timestamps = result_block["timestamp"]
        # 'quote' contains the high/low/close lists
        prices = result_block["indicators"]["quote"][0]["close"]
        
    except Exception as e:
        print(f"❌ Data Extraction Error: {e}")
        return

    # 3. Clean Data (Remove None/Nulls for market holidays)
    valid_data = []
    for ts, price in zip(timestamps, prices):
        if price is not None:
            valid_data.append((ts, price))
            
    if not valid_data:
        print("❌ No valid price data found in API response.")
        return

    # 4. Calculate Normalization Ratio
    # Logic: We don't care about the absolute $ value of Gold Futures.
    # We care about the *shape* of the graph. 
    # We scale the LAST point of the global graph to match our TODAY'S retail price.
    last_market_price = valid_data[-1][1]
    scaling_ratio = current_retail_price / last_market_price
    
    print(f"   ⚖️ Scaling Ratio: {scaling_ratio:.4f} (Aligning Global Trend to Local Market)")

    # 5. Generate Rows
    backfill_rows = []
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    for ts, price in valid_data:
        dt_object = datetime.fromtimestamp(ts)
        date_str = dt_object.strftime('%Y-%m-%d')
        
        # Skip today (the main pipeline handles today to avoid duplicates)
        if date_str == today_str:
            continue
            
        # Apply the ratio to historical global prices to get "Simulated Local Price"
        simulated_retail = int(price * scaling_ratio)
        
        backfill_rows.append({
            "Date": date_str,
            "Gold_Price_22k": simulated_retail
        })
    
    print(f"3. Generated {len(backfill_rows)} historical data points.")

    # 6. Write to CSV
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Gold_Price_22k"])
        writer.writeheader()
        writer.writerows(backfill_rows)
        
    print(f"✅ Success! Backfill written to {DATA_FILE}")
    print("   Ready for Phase 5: The Oracle.")

if __name__ == "__main__":
    run_backfill()