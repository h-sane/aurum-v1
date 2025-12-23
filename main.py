import sys
from src.scout import Scout
from src import ledger

def main():
    print("--- Aurum-V1 Pipeline Initiated ---")
    
    # 1. Ingest Data
    scout = Scout()
    result = scout.fetch_price()
    
    if not result.success:
        print(f"⚠️ Ingestion Failed: {result.message}")
        # Exit with 0 to prevent GitHub Action failure (Streak Preservation),
        # but print error so logs show what happened.
        # Ideally, you might want to commit a log file here.
        sys.exit(0) 

    print(f"✅ Data Acquired: ₹{result.price} (10g)")

    # 2. Persist Data (Atomic Write)
    was_saved = ledger.save_transaction(result.price)

    if was_saved:
        print(f"💾 Transaction Saved: {result.timestamp}")
        # Signal to GitHub Actions that we have a Data Update
        print("::set-output name=commit_type::data")
    else:
        print("⏭️  Idempotent Skip: Data for today already exists.")
        # Signal to GitHub Actions that we have no new data
        print("::set-output name=commit_type::skip")

if __name__ == "__main__":
    main()