from curl_cffi import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import re
import src.config as config

@dataclass
class ScrapeResult:
    """Standardized return object for the Ingestion Service."""
    success: bool
    price: Optional[int] = None
    message: str = ""
    timestamp: str = ""

class Scout:
    def __init__(self):
        self.url = config.SOURCE_URL

    def fetch_price(self) -> ScrapeResult:
        now_ts = datetime.now().isoformat()
        
        try:
            # 1. Fetch HTML
            response = requests.get(self.url, impersonate="chrome120", timeout=15)
            if response.status_code != 200:
                return ScrapeResult(success=False, message=f"HTTP Error {response.status_code}", timestamp=now_ts)

            soup = BeautifulSoup(response.text, 'html.parser')

            # 2. Strict Anchor Strategy
            target_keywords = ["today", "22", "gram"]
            anchor_tag = None
            
            candidates = soup.find_all(["h1", "h2", "h3", "h4", "div", "span"])
            for tag in candidates:
                text = tag.get_text(" ", strip=True).lower()
                if all(k in text for k in target_keywords) and len(text) < 150:
                    anchor_tag = tag
                    break
            
            if not anchor_tag:
                return ScrapeResult(success=False, message="Strict Anchor (Today+22+Gram) Not Found", timestamp=now_ts)

            # 3. Find the associated table
            table = anchor_tag.find_next("table")
            if not table:
                return ScrapeResult(success=False, message="Table not found after heading", timestamp=now_ts)

            # 4. Find the '1' Row (Flexible Match)
            found_price = None
            rows = table.find_all("tr")
            
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2: continue
                
                label_text = cells[0].get_text(strip=True).lower()
                
                if re.search(r"^1\s*(g|gram|gms)?$", label_text):
                    raw_price = cells[1].get_text(strip=True)
                    digits = re.sub(r"[^\d]", "", raw_price)
                    if digits:
                        # NORMALIZE: Convert 1g price to 10g standard
                        found_price = int(digits) * 10
                        break
            
            if not found_price:
                 return ScrapeResult(success=False, message="Price row (1/1g) not found in table", timestamp=now_ts)

            # 5. Semantic Validation (Check against 10g limits)
            if not (config.MIN_PRICE_22K <= found_price <= config.MAX_PRICE_22K):
                 return ScrapeResult(success=False, message=f"Validation Failed: {found_price} (Out of 10g bounds)", timestamp=now_ts)

            return ScrapeResult(success=True, price=found_price, message="Ingestion Successful", timestamp=now_ts)

        except Exception as e:
            return ScrapeResult(success=False, message=f"System Error: {str(e)}", timestamp=now_ts)

if __name__ == "__main__":
    scout = Scout()
    print(scout.fetch_price())