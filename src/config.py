"""
aurum-v1 Configuration
Centralizes constants, URLs, and validation thresholds.
"""
import os

# --- Target Sources ---
SOURCE_URL = "https://www.goodreturns.in/gold-rates/"

# --- Semantic Validation Thresholds (2025 Adjusted) ---
# Safety bounds for 22k Gold (per 10g) in INR.
MIN_PRICE_22K = 80000   
MAX_PRICE_22K = 200000 

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "gold_prices.csv")
STATE_FILE = os.path.join(BASE_DIR, "data", "pipeline_state.json")