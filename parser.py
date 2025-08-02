import re
from bs4 import BeautifulSoup
from typing import Optional

from bs4 import BeautifulSoup

def parse_balance_sheet_file(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    return parse_balance_sheet_html_string(html)

def parse_balance_sheet_html_string(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    for idx, table in enumerate(tables):
        text = table.get_text(separator=" ", strip=True).lower()

        # Heuristic: Check if both 'assets:' and 'liabilities and shareholders’ equity:' appear
        if "assets:" in text and "liabilities and shareholders" in text:
            print("Found balance sheet table")
            return str(table)

    print("No matching balance sheet table found.")
    return None

def parse_balance_sheet_html(html_path: str, symbol: str):
    from bs4 import BeautifulSoup

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    table = soup.find('table')
    if not table:
        print("No <table> found.")
        return None

    rows = table.find_all('tr')

    # Extract dates from the first row that contains two valid dates
    date_1, date_2 = None, None
    date_pattern = re.compile(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},\s+20\d{2}', re.IGNORECASE)

    for row in rows:
        text = row.get_text(separator=" ", strip=True)
        dates = re.findall(date_pattern, text)
        if len(dates) >= 2:
            full_dates = re.findall(r'[A-Za-z]+\s+\d{1,2},\s+20\d{2}', text)
            if len(full_dates) >= 2:
                date_1 = full_dates[0]
                date_2 = full_dates[1]
                break

    if not date_1 or not date_2:
        print("Couldn't detect balance sheet dates.")
        return None


    balance_rows = []

    for row in rows:
        cells = row.find_all(['td', 'th'])
        text_cells = []

        for cell in cells:
            ix = cell.find('ix:nonfraction')
            if ix:
                text_cells.append(ix.text.strip())
            else:
                text_cells.append(cell.get_text(strip=True))

        # Skip headers, section titles, or empty rows
        if len(text_cells) < 3:
            continue

        # Heuristic: if first cell is a label and last two are values
        label = text_cells[0]
        num_vals = [v for v in text_cells[1:] if v.replace(',', '').replace('(', '').replace(')', '').replace('$', '').isdigit()]

        if len(num_vals) < 2:
            continue

        try:
            value_1 = int(num_vals[0].replace(',', '').replace('(', '-').replace(')', ''))
            value_2 = int(num_vals[1].replace(',', '').replace('(', '-').replace(')', ''))
        except ValueError:
            continue

        balance_rows.append({
            "symbol": symbol,
            "label": label,
            "date_1": date_1,
            "value_1": value_1,
            "date_2": date_2,
            "value_2": value_2,
        })

    if not balance_rows:
        print("Error: Could not parse balance sheet rows.")
        return None

    return balance_rows


