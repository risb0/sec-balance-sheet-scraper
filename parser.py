import pandas as pd
from bs4 import BeautifulSoup
import os
import re

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

    # We'll assume table 14 is the balance sheet as previously found
    try:
        table = tables[14]
        print(f"Found candidate balance sheet table at index 14")
    except IndexError:
        print("Could not find table 14.")
        return []

    rows = []
    for idx, row in table.iterrows():
        # Convert all row values to string
        str_row = [str(cell).strip() for cell in row]
        joined_row = " | ".join(str_row)
        print(f"Row {idx}: {joined_row}")

        # Expect first cell to be a label and rest to be values
        label = str_row[0]
        values = str_row[1:]

        if not label or 'total' in label.lower():
            continue

        cleaned_values = [clean_value(val) for val in values]
        if not any(cleaned_values):  # skip empty/invalid rows
            continue

        rows.append({
            "symbol": symbol,
            "label": label,
            "values": cleaned_values
        })

    print(f"Parsed {len(rows)} balance sheet rows.")
    return rows
