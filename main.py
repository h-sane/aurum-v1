import sys
from src.scout import Scout
from src import ledger
from src import prophet
from src.sentinel import Sentinel
from src import dashboard  # <--- Import Dashboard

def main():
    print("--- Aurum-V1 Pipeline Initiated ---")
    
    # 1. Ingest
    scout = Scout()
    result = scout.fetch_price()
    
    if not result.success:
        print(f"⚠️ Ingestion Failed: {result.message}")
        sys.exit(0) 

    print(f"✅ Data Acquired: ₹{result.price} (10g)")

    # 2. Persist
    was_saved = ledger.save_transaction(result.price)

    if was_saved:
        print(f"💾 Transaction Saved: {result.timestamp}")
        print("::set-output name=commit_type::data")
        
        # 3. Analytics
        print("--- Triggering Analytics ---")
        try:
            prophet.run_oracle()
            
            try:
                bot = Sentinel()
                bot.analyze_market_mood()
            except Exception as e:
                print(f"⚠️ Sentinel Failed (Non-Critical): {e}")
                
        except Exception as e:
            print(f"⚠️ Oracle Failed: {e}")

        # 4. Publish Dashboard (Runs only on new data)
        try:
            dashboard.generate_readme()
        except Exception as e:
            print(f"⚠️ Dashboard Generation Failed: {e}")
            
    else:
        print("⏭️  Idempotent Skip: Data for today already exists.")
        print("::set-output name=commit_type::skip")
        
        # DEBUG: Force update README even if no new data (Good for testing)
        dashboard.generate_readme()

if __name__ == "__main__":
    main()