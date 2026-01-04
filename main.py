from src import scraper
from src import ledger
from src import prophet
from src import dashboard
from src import sentinel
import sys

def main():
    print("--- Aurum-V1 Pipeline Initiated ---")
    
    # 1. ACQUIRE DATA
    try:
        # Fetch Price
        price_data = scraper.fetch_price()
        
        # Robust check: Did we get a dictionary (price + usd) or just an int?
        if isinstance(price_data, dict):
            price = price_data.get('price')
            usd_inr = price_data.get('usd_inr', 84.0) # Default if missing
        else:
            price = price_data
            usd_inr = 84.0
            
        print(f"✅ Data Acquired: ₹{price} (10g) | USD: {usd_inr}")

    except Exception as e:
        print(f"❌ Error during Acquisition: {e}")
        return

    # 2. SAVE TO LEDGER
    try:
        # We pass both Price and USD_INR to the ledger
        was_saved = ledger.save_transaction(price, usd_inr)
        
        if not was_saved:
            print("⏭️  Idempotent Skip: Data for today already exists.")
            print("::set-output name=commit_type::skip")
            # We exit here because if we didn't add new data, 
            # we don't need to re-train the model or update the dashboard today.
            return

    except Exception as e:
        print(f"❌ Error during Save: {e}")
        return

    # 3. INTELLIGENCE LAYER (Only runs if new data was saved)
    try:
        print("--- 🧠 Starting Intelligence Layer ---")
        
        # A. Sentinel (News)
        s = sentinel.Sentinel()
        s.analyze_market_mood()
        
        # B. Prophet (Prediction)
        prophet.run_oracle()
        
        # C. Dashboard (Display)
        dashboard.generate_readme()
        
    except Exception as e:
        print(f"❌ Error during Intelligence: {e}")

if __name__ == "__main__":
    main()