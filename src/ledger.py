import csv
import os
from datetime import datetime
import pandas as pd

FILE_PATH = "data/gold_prices.csv"
# CORRECT HEADER: Must match your actual CSV columns
CSV_HEADER = ["Date", "Gold_Price_22k", "USD_INR"]

def save_transaction(price, usd_inr=84.0):
    """
    Saves the daily price and currency rate to the CSV.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists(FILE_PATH)
    
    # 1. Prepare the Data Row
    new_row = {
        "Date": today,
        "Gold_Price_22k": price,
        "USD_INR": usd_inr
    }

    # 2. Idempotency Check (Prevent Duplicates)
    if file_exists:
        try:
            # We read the CSV to check if today's date exists
            df = pd.read_csv(FILE_PATH)
            # Ensure 'Date' column is treated as string for comparison
            if today in df['Date'].astype(str).values:
                return False # Return False to signal "No new data saved"
        except Exception as e:
            print(f"⚠️ Warning reading CSV: {e}")

    # 3. Write Data
    try:
        # 'a' mode appends to the end of the file
        with open(FILE_PATH, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADER)
            
            # If the file is brand new, write the header first
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(new_row)
            print(f"💾 Saved to Ledger: {today} | ₹{price} | ${usd_inr}")
            return True

    except ValueError as e:
        print(f"❌ Ledger Error: {e}")
        print(f"   Expected columns: {CSV_HEADER}")
        raise e

def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    return pd.DataFrame(columns=CSV_HEADER)