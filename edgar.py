import requests
import time

HEADERS = {
    "User-Agent": "Your Name your.email@example.com"
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
        filing_url = get_latest_10q_url(cik)
        print(f"Latest 10-Q filing index URL:\n{filing_url}")
    except LookupError as e:
        print(str(e))
    
    # Respect SEC rate limit
    time.sleep(0.5)
