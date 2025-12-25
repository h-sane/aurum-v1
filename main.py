import sys
from src.scout import Scout
from src import ledger
from src import prophet
from src.sentinel import Sentinel
from src import dashboard

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
        
        # 3. Analytics (Only run heavy ML/Sentiment if we have NEW data)
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

    else:
        print("⏭️  Idempotent Skip: Data for today already exists.")
        print("::set-output name=commit_type::skip")

    # 4. Publish Dashboard (ALWAYS RUN THIS)
    # We moved this OUTSIDE the 'if' block so the README updates every time.
    try:
        dashboard.generate_readme()
    except Exception as e:
        print(f"⚠️ Dashboard Generation Failed: {e}")

if __name__ == "__main__":
    main()