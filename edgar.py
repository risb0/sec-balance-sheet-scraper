import requests
import time
from bs4 import BeautifulSoup
from parser import parse_balance_sheet_html
import re
from parser import parse_balance_sheet_html_string

HEADERS = {
    "User-Agent": "rizsbosz@atomicmail.io SEC scraper for educational project"
}

TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

def get_cik_from_symbol(symbol: str) -> str:
    """Convert ticker symbol to padded 10-digit CIK string."""
    response = requests.get(TICKER_CIK_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    
    for entry in data.values():
        if entry["ticker"].upper() == symbol.upper():
            cik_str = str(entry["cik_str"]).zfill(10)
            return cik_str
    
    raise ValueError(f"Symbol '{symbol}' not found in SEC database.")

def get_latest_10q_url(cik: str) -> str:
    """Get the latest 10-Q filing URL for a given CIK."""
    url = SUBMISSIONS_URL.format(cik=cik)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    
    for filing in data["filings"]["recent"]["form"]:
        if filing == "10-Q":
            idx = data["filings"]["recent"]["form"].index(filing)
            accession_number = data["filings"]["recent"]["accessionNumber"][idx].replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/index.json"
            return filing_url
    
    raise LookupError("No recent 10-Q filing found.")

def fetch_and_parse_latest_10q(symbol: str):
    cik = get_cik_from_symbol(symbol)
    print(f"Found CIK for {symbol}: {cik}")

    try:
        index_url = get_latest_10q_url(cik)
        print(f"Filing index URL:\n{index_url}")

        html_url = get_10q_html_url(index_url, symbol)
        print(f"\nFound 10-Q HTML document:\n{html_url}")

        # Save full 10-Q HTML for reference
        html_response = requests.get(html_url, headers=HEADERS)
        html_response.raise_for_status()
        with open("full_10q.html", "w", encoding="utf-8") as f:
            f.write(html_response.text)

        # Extract just the balance sheet section as HTML
        balance_sheet_html = extract_balance_sheet_table(html_url)

        if balance_sheet_html:
            with open("balance_sheet.html", "w", encoding="utf-8") as f:
                f.write(balance_sheet_html)
            print("Saved balance sheet HTML to balance_sheet.html")
        else:
            print("Skipping save: No balance sheet HTML extracted.")
            return

    except (LookupError, requests.RequestException) as e:
        print(f"Error: {e}")

    time.sleep(0.5)  # Respect SEC rate limit




    


def get_10q_html_url(index_url: str, symbol: str) -> str:
    """Return the most likely 10-Q HTML document URL from the index."""
    response = requests.get(index_url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    items = data.get("directory", {}).get("item", [])
    symbol_lower = symbol.lower()

    # Priority 1: Match pattern like "aapl-20250329.htm"
    for file in items:
        name = file.get("name", "").lower()
        if re.match(rf"^{symbol_lower}-\d{{8}}\.htm$", name):
            return index_url.replace("index.json", file["name"])

    # Priority 2: Fall back to first .htm file with '10-q' or '10q'
    for file in items:
        name = file.get("name", "").lower()
        if "10-q" in name or "10q" in name and name.endswith(".htm"):
            return index_url.replace("index.json", file["name"])

    # Priority 3: Fall back to largest .htm file
    html_files = [f for f in items if f["name"].lower().endswith(".htm")]
    if html_files:
        largest = max(html_files, key=lambda f: f.get("size", 0))
        return index_url.replace("index.json", largest["name"])

    raise LookupError("No suitable 10-Q HTML file found.")





def extract_balance_sheet_table(html_url: str) -> str:
    """Extracts the Balance Sheet section from the 10-Q HTML."""
    response = requests.get(html_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    tables = soup.find_all("table")

    for i, table in enumerate(tables):
        text = table.get_text(" ", strip=True).lower()
        print(f"Table {i} preview: {text[:100].encode('ascii', errors='ignore').decode()}...")

        # Heuristic: Balance sheet likely contains "assets" and two distinct 4-digit years
        if "assets" in text:
            years = set(re.findall(r"\b20\d{2}\b", text))
            if len(years) >= 2:
                print(f"Found candidate balance sheet table at index {i}")
                return table.prettify()

    print("No matching balance sheet table found.")
    return None
