from curl_cffi import requests
from bs4 import BeautifulSoup
import yfinance as yf
import re

# CONFIG
GOLD_URL = "https://www.goodreturns.in/gold-rates/chennai.html"

def get_usd_inr():
    """Fetches live USD/INR exchange rate."""
    try:
        ticker = yf.Ticker("INR=X")
        data = ticker.history(period="1d")
        if not data.empty:
            return round(data['Close'].iloc[-1], 2)
        return 84.0 
    except Exception as e:
        print(f"⚠️ Forex Error: {e}")
        return 84.0

def fetch_price():
    """
    Fetches the current 22K Gold Price for 10g in Chennai.
    Strategy: Text Mining (Regex) on page content.
    """
    print("--- 🕷️  Scraper: Fetching Live Data (Text Mining Mode) ---")
    
    price_10g = None
    usd_rate = get_usd_inr()

    try:
        # 1. Fetch Page
        response = requests.get(GOLD_URL, impersonate="chrome110", timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 2. Convert entire page to simple text
        # This collapses all <div>, <table>, <p> into one big string
        full_text = soup.get_text(" ", strip=True)
        
        # 3. Regex Patterns to find the price
        # Pattern 1: Matches "₹12,600 per gram for 22 karat" (From your screenshot)
        # We look for the number right before "per gram for 22 karat"
        pattern_text = r"₹\s*([\d,]+)\s*per gram for 22 karat"
        
        match = re.search(pattern_text, full_text, re.IGNORECASE)
        
        if match:
            # We found the 1 gram price (e.g., "12,600")
            price_str = match.group(1).replace(",", "")
            price_1g = int(price_str)
            
            # Convert to 10g Standard
            price_10g = price_1g * 10
            print(f"   ✅ Found 1g Price in text: ₹{price_1g}")
            print(f"   💰 Converted to 10g: ₹{price_10g}")
            
        else:
            # Fallback: Try looking for the "10 gram" table row again using pure text search
            # Pattern: "10 gram" followed eventually by "₹ 1,26,000"
            # This is riskier but good as a backup
            pattern_table = r"22\s*Carat.*?10\s*gram.*?₹\s*([\d,]+)"
            match_table = re.search(pattern_table, full_text, re.IGNORECASE)
            
            if match_table:
                price_str = match_table.group(1).replace(",", "")
                price_10g = int(price_str)
                print(f"   ✅ Found 10g Price in table text: ₹{price_10g}")

        if not price_10g:
            print("❌ Scraper Failed: Regex could not match price in text.")
            return None

    except Exception as e:
        print(f"❌ Scraper Critical Error: {e}")
        return None

    return {
        "price": price_10g,
        "usd_inr": usd_rate
    }

if __name__ == "__main__":
    # Test run
    data = fetch_price()
    print(f"Test Result: {data}")