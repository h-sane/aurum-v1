import os
import re

CSV_FILE = "data/gold_prices.csv"
JSON_DASHBOARD = "data/dashboard_data.json"
JSON_MOOD = "data/market_mood.json"

def clean_csv():
    print(f"🧹 Cleaning {CSV_FILE}...")
    
    if not os.path.exists(CSV_FILE):
        print("❌ CSV file not found.")
        return

    unique_data = {}
    
    # Regex to match valid data lines: "2025-12-25,127000"
    # It ignores lines like "<<<<<<< HEAD" or "======="
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2},\d+$")

    with open(CSV_FILE, 'r') as f:
        lines = f.readlines()

    # Process header
    header = lines[0] if lines else "Date,Gold_Price_22k\n"
    
    for line in lines:
        line = line.strip()
        if pattern.match(line):
            date, price = line.split(',')
            # Store in dict to automatically remove duplicates (keeps latest price found)
            unique_data[date] = price

    # Sort by date
    sorted_dates = sorted(unique_data.keys())
    
    # Write back clean data
    with open(CSV_FILE, 'w', newline='') as f:
        f.write("Date,Gold_Price_22k\n") # Ensure header is present
        for date in sorted_dates:
            f.write(f"{date},{unique_data[date]}\n")
            
    print(f"✅ CSV repaired! {len(sorted_dates)} valid rows retained.")

def clean_json():
    # It's safer to just delete corrupted JSONs. 
    # main.py will regenerate them fresh on the next run.
    for file in [JSON_DASHBOARD, JSON_MOOD]:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Deleted corrupted JSON: {file}")
            except Exception as e:
                print(f"⚠️ Could not delete {file}: {e}")

if __name__ == "__main__":
    clean_csv()
    clean_json()
    print("✨ Cleanup Complete. You can now run 'python main.py'.")