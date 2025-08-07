import requests
import time
from bs4 import BeautifulSoup
from parser import parse_balance_sheet_html
import re

HEADERS = {
    "User-Agent": "rizsbosz@atomicmail.io SEC scraper for educational project"
}

TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

def get_cik_from_symbol(symbol: str) -> str:
    response = requests.get(TICKER_CIK_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    for entry in data.values():
        if entry["ticker"].upper() == symbol.upper():
            cik_str = str(entry["cik_str"]).zfill(10)
            return cik_str

    raise ValueError(f"Symbol '{symbol}' not found in SEC database.")

def get_latest_10q_url(cik: str) -> str:
    url = SUBMISSIONS_URL.format(cik=cik)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    for filing in data["filings"]["recent"]["form"]:
        if filing == "10-Q":
            idx = data["filings"]["recent"]["form"].index(filing)
            accession_number = data["filings"]["recent"]["accessionNumber"][idx].replace("-", "")
            return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/index.json"

    raise LookupError("No recent 10-Q filing found.")

def get_10q_html_url(index_url: str, symbol: str) -> str:
    response = requests.get(index_url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    items = data.get("directory", {}).get("item", [])
    symbol_lower = symbol.lower()

    for file in items:
        name = file.get("name", "").lower()
        if re.match(rf"^{symbol_lower}-\d{{8}}\.htm$", name):
            return index_url.replace("index.json", file["name"])

    for file in items:
        name = file.get("name", "").lower()
        if ("10-q" in name or "10q" in name) and name.endswith(".htm"):
            return index_url.replace("index.json", file["name"])

    html_files = [f for f in items if f["name"].lower().endswith(".htm")]
    if html_files:
        largest = max(html_files, key=lambda f: f.get("size", 0))
        return index_url.replace("index.json", largest["name"])

    raise LookupError("No suitable 10-Q HTML file found.")

def extract_balance_sheet_table(html_url: str) -> str:
    response = requests.get(html_url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    tables = soup.find_all("table")

    for i, table in enumerate(tables):
        text = table.get_text(" ", strip=True).lower()
        print(f"Table {i} preview: {text[:100].encode('ascii', errors='ignore').decode()}...")

        if "assets" in text:
            years = set(re.findall(r"\b20\d{2}\b", text))
            if len(years) >= 2:
                print(f"Found candidate balance sheet table at index {i}")
                return table.prettify()

    print("No matching balance sheet table found.")
    return None

def fetch_and_parse_latest_10q(symbol: str):
    cik = get_cik_from_symbol(symbol)
    print(f"Found CIK for {symbol}: {cik}")

    try:
        index_url = get_latest_10q_url(cik)
        print(f"Filing index URL:\n{index_url}")

        html_url = get_10q_html_url(index_url, symbol)
        print(f"\nFound 10-Q HTML document:\n{html_url}")

        html_response = requests.get(html_url, headers=HEADERS)
        html_response.raise_for_status()
        with open("full_10q.html", "w", encoding="utf-8") as f:
            f.write(html_response.text)

        balance_sheet_html = extract_balance_sheet_table(html_url)

        if balance_sheet_html:
            if table_index < len(tables):
                balance_sheet_table = tables[table_index]
                with open("balance_sheet.html", "w", encoding="utf-8") as f:
                    f.write(str(balance_sheet_table))
                print(f"Saved balance sheet table {table_index} to balance_sheet.html")
            else:
                print(f"Error: Table index {table_index} is out of range")

        else:
            print("Skipping save: No balance sheet HTML extracted.")
            return

    except (LookupError, requests.RequestException) as e:
        print(f"Error: {e}")

    time.sleep(0.5)
