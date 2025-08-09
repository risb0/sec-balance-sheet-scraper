import pandas as pd
from bs4 import BeautifulSoup
import os
from datetime import datetime
import math  # for isnan check


def clean_value(val):
    """
    Cleans a raw string value from the balance sheet to a float.
    Handles empty strings, dollar signs, commas, parentheses for negatives, and special spaces.
    Returns None if conversion fails.
    """
    if not val or val.strip() == '':
        return None
    val = val.replace('$', '').replace(',', '').strip()
    # Remove non-breaking spaces and zero-width spaces
    val = val.replace('\xa0', '').replace('\u200b', '')
    # Handle parentheses for negatives
    if val.startswith('(') and val.endswith(')'):
        val = '-' + val[1:-1]
    try:
        fval = float(val)
        # Prevent storing NaN or infinite values
        if math.isnan(fval) or math.isinf(fval):
            return None
        return fval
    except Exception as e:
        print(f"clean_value error on '{val}': {e}")
        return None


def looks_like_date(text):
    """
    Checks if a string looks like a date using common formats.
    Returns True if a parse succeeds, else False.
    """
    if not isinstance(text, str):
        return False
    date_formats = ("%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y ")
    for fmt in date_formats:
        try:
            datetime.strptime(text.strip(), fmt)
            return True
        except Exception:
            continue
    return False


def to_iso_date(h):
    """
    Converts a date string to ISO format (YYYY-MM-DD).
    Returns the original string stripped if parsing fails.
    """
    date_formats = ("%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y ")
    for fmt in date_formats:
        try:
            return datetime.strptime(str(h).strip(), fmt).date().isoformat()
        except Exception:
            continue
    return str(h).strip()


def parse_balance_sheet_html(html_path, symbol, filing_date=None):
    """
    Parses the balance sheet data from an HTML file path.
    Extracts label and multiple date columns with values.
    Returns a list of dicts with 'symbol', 'label', 'values', and optional 'filing_date'.
    """
    print(f"Parsing balance sheet from: {html_path}")

    if not os.path.exists(html_path):
        print(f"HTML file not found: {html_path}")
        return []

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    try:
        tables = pd.read_html(str(soup), header=None)
    except Exception as e:
        print(f"Error reading tables from HTML: {e}")
        return []

    print(f"Found {len(tables)} tables.")

    if not tables:
        print("No tables found in HTML.")
        return []

    # Use the first table as the balance sheet table
    table = tables[0]
    print(f"Raw table preview (first 5 rows):\n{table.head(5)}")

    # Find header row index by detecting a row with multiple date-like columns (excluding label col)
    header_row_idx = None
    max_check_rows = min(5, len(table))
    for i in range(max_check_rows):
        row = table.iloc[i].astype(str).tolist()
        date_like_count = sum(1 for cell in row[1:] if looks_like_date(cell))
        if date_like_count >= 2:
            header_row_idx = i
            break

    if header_row_idx is None:
        print("Could not find header row with date columns, aborting parse.")
        return []

    print(f"Detected header row at index {header_row_idx}: {table.iloc[header_row_idx].tolist()}")

    new_header = table.iloc[header_row_idx]

    # Clean header: convert NaN/empty to None, strip strings
    cleaned_header = []
    for h in new_header:
        if isinstance(h, float) and math.isnan(h):
            cleaned_header.append(None)
        elif isinstance(h, str) and h.strip() == '':
            cleaned_header.append(None)
        else:
            cleaned_header.append(str(h).strip())

    # Identify date columns (valid date headers)
    date_col_indices = [i for i, h in enumerate(cleaned_header) if h is not None and looks_like_date(h)]

    if not date_col_indices:
        print("No valid date columns found in header, aborting parse.")
        return []

    # Identify label column (first column that is NOT a date column)
    label_col_index = next((i for i in range(len(cleaned_header)) if i not in date_col_indices), 0)

    # Convert date headers to ISO format
    date_headers = [to_iso_date(cleaned_header[i]) for i in date_col_indices]

    print(f"Using label column index: {label_col_index}")
    print(f"Parsed date headers: {date_headers}")

    # Use the rows after the header row
    data_rows = table.iloc[header_row_idx + 1 :].copy()

    # Assign cleaned header as columns to keep labels and dates aligned
    data_rows.columns = cleaned_header

    rows = []
    for idx, row in data_rows.iterrows():
        label = row[label_col_index]
        if not label or str(label).strip() == '':
            continue
        # Skip rows containing 'total' in the label (case-insensitive)
        if 'total' in str(label).lower():
            continue

        # Extract only values from the date columns
        values = [row[i] for i in date_col_indices]

        # Debug print raw values before cleaning
        print(f"Raw values for label '{label}': {values}")

        cleaned_values = []
        for val in values:
            val_str = str(val)
            cleaned_val = clean_value(val_str)
            if cleaned_val is None and val_str.strip() != '':
                print(f"Warning: could not clean value '{val_str}' for label '{label}'")
            cleaned_values.append(cleaned_val)

        if not any([v is not None for v in cleaned_values]):
            # Skip rows with no valid values at all
            continue

        # Only include keys with valid non-None values
        values_dict = {
            date_headers[i]: cleaned_values[i]
            for i in range(len(cleaned_values))
            if cleaned_values[i] is not None
        }

        # Defensive check: if values_dict is empty skip row
        if not values_dict:
            continue

        row_dict = {
            "symbol": symbol,
            "label": str(label).strip(),
            "values": values_dict
        }
        if filing_date:
            row_dict["filing_date"] = filing_date

        rows.append(row_dict)

    # DEBUG: print output rows with types
    for r in rows:
        print(f"Label: {r['label']}")
        for d, v in r['values'].items():
            print(f"  {d}: {v} ({type(v)})")

    print(f"Parsed {len(rows)} balance sheet rows.")
    return rows
