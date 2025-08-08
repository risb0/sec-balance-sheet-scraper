import pandas as pd
from bs4 import BeautifulSoup
import os

def clean_value(val):
    if not val or val.strip() == '':
        return None
    val = val.replace('$', '').replace(',', '').strip()
    try:
        return float(val)
    except:
        return None

def parse_balance_sheet_html(html_path, symbol):
    print(f"Parsing balance sheet from: {html_path}")

    if not os.path.exists(html_path):
        print("HTML file not found.")
        return []

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    tables = pd.read_html(str(soup))
    print(f"Found {len(tables)} tables.")

    if not tables:
        print("No tables found in HTML.")
        return []

    # Only one table should exist in balance_sheet.html
    table = tables[0]

    rows = []
    for idx, row in table.iterrows():
        str_row = [str(cell).strip() for cell in row]
        joined_row = " | ".join(str_row)
        print(f"Row {idx}: {joined_row}")

        label = str_row[0]
        values = str_row[1:]

        if not label or 'total' in label.lower():
            continue

        cleaned_values = [clean_value(val) for val in values]
        if not any(cleaned_values):
            continue

        rows.append({
            "symbol": symbol,
            "label": label,
            "values": cleaned_values
        })

    print(f"Parsed {len(rows)} balance sheet rows.")
    return rows