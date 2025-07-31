import requests
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "rizsbosz@atomicmail.io"
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

        html_url = get_10q_html_url(index_url)
        print(f"\n✅ Found 10-Q HTML document:\n{html_url}")

        balance_sheet_html = extract_balance_sheet_table(html_url)
        with open("balance_sheet.html", "w", encoding="utf-8") as f:
            f.write(balance_sheet_html)
        print("\n✅ Saved extracted table to balance_sheet.html")

    except (LookupError, requests.RequestException) as e:
        print(f"Error: {e}")

    # Respect SEC rate limit
    time.sleep(0.5)

    


def get_10q_html_url(index_url: str) -> str:
    """Extract the main 10-Q filing HTML URL from the index.json."""
    response = requests.get(index_url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    for file in data.get("directory", {}).get("item", []):
        name = file.get("name", "").lower()
        if name.endswith(".htm") and "10q" in name:
            html_url = index_url.replace("index.json", name)
            return html_url

    raise LookupError("10-Q HTML file not found in filing index.")




def extract_balance_sheet_table(html_url: str) -> str:
    """Extract the Condensed Consolidated Balance Sheets table from the 10-Q HTML."""
    response = requests.get(html_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all tables that contain the string "Condensed Consolidated Balance Sheets"
    tables = soup.find_all("table")

    for table in tables:
        if "Condensed Consolidated Balance Sheets" in table.get_text():
            print("\n✅ Found Condensed Consolidated Balance Sheets table")
            return table.prettify()

    raise LookupError("Could not find 'Condensed Consolidated Balance Sheets' table in filing.")