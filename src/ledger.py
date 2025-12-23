import csv
import os
from datetime import datetime
from typing import List

# Define paths relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(DATA_DIR, "gold_prices.csv")
TMP_FILE = os.path.join(DATA_DIR, "gold_prices.tmp")

FIELDNAMES = ["Date", "Gold_Price_22k"]

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def _read_existing_rows() -> List[dict]:
    if not os.path.exists(CSV_FILE):
        return []

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_transaction(price: int) -> bool:
    """
    Persist today's gold price using an atomic write.
    Returns:
        True  -> row was added
        False -> idempotent no-op (today already exists)
    """
    _ensure_data_dir()

    today = datetime.now().strftime("%Y-%m-%d")
    rows = _read_existing_rows()

    # --- IDEMPOTENCY CHECK ---
    if rows and rows[-1]["Date"] == today:
        return False

    # --- APPEND NEW ROW IN-MEMORY ---
    rows.append({
        "Date": today,
        "Gold_Price_22k": str(price)
    })

    # --- ATOMIC WRITE ---
    with open(TMP_FILE, mode="w", newline="", encoding="utf-8") as tmp:
        writer = csv.DictWriter(tmp, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

        # Force write to disk
        tmp.flush()
        os.fsync(tmp.fileno())

    # Atomic replace (safe on Linux, macOS, Windows)
    os.replace(TMP_FILE, CSV_FILE)

    return True