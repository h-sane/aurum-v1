from curl_cffi import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://www.goodreturns.in/gold-rates/"

HEADERS = {
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def fetch_html(url: str) -> str:
    response = requests.get(
        url,
        impersonate="chrome120",
        timeout=20,
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.text


def debug_22k_table(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # ---- 1. Find heading containing "22" ----
    headings = soup.find_all(["h1", "h2", "h3", "div"])
    anchor = None

    for tag in headings:
        text = tag.get_text(" ", strip=True).lower()
        if "22" in text and "carat" in text:
            anchor = tag
            print(f"\n✅ Found Heading Anchor:\n{text}\n")
            break

    if not anchor:
        print("❌ No heading containing '22 carat' found.")
        print("Available headings:")
        for tag in headings:
            print("-", tag.get_text(" ", strip=True))
        return

    # ---- 2. Find the next table ----
    table = anchor.find_next("table")
    if not table:
        print("❌ No table found after the heading.")
        return

    print("✅ Table found. Dumping rows:\n")

    # ---- 3. Dump every row and cell ----
    rows = table.find_all("tr")

    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        cell_texts = [cell.get_text(" ", strip=True) for cell in cells]
        print(f"Row {i}: " + " | ".join(cell_texts))


if __name__ == "__main__":
    html = fetch_html(TARGET_URL)
    debug_22k_table(html)
