import pandas as pd
from bs4 import BeautifulSoup
import os
from datetime import datetime
import math
import re

def clean_value(val):
    if val is None:
        return None
    val = str(val).strip()
    if val in ('', '-', 'N/A', 'NA'):
        return None
    val = val.replace('$', '').replace(',', '').replace('\xa0', '').replace('\u200b', '')
    if val.startswith('(') and val.endswith(')'):
        val = '-' + val[1:-1]
    try:
        fval = float(val)
        if math.isnan(fval) or math.isinf(fval):
            return None
        return fval
    except Exception:
        return None

def preclean_header_cell(cell):
    if cell is None:
        return None
    text = str(cell).strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('"', '')
    if text.lower().startswith("as of"):
        text = text[5:].strip()
    return text

def looks_like_date(text):
    if not isinstance(text, str):
        return False
    date_formats = ("%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y")
    for fmt in date_formats:
        try:
            datetime.strptime(text.strip(), fmt)
            return True
        except Exception:
            continue
    return False

def to_iso_date(text):
    date_formats = ("%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y")
    for fmt in date_formats:
        try:
            return datetime.strptime(str(text).strip(), fmt).date().isoformat()
        except Exception:
            continue
    return str(text).strip()

def save_debug_html(symbol, filing_date, html_content):
    debug_dir = os.path.join("/app/debug", "balance_sheets")
    os.makedirs(debug_dir, exist_ok=True)
    safe_date = filing_date if filing_date else datetime.now().strftime("%Y%m%d")
    filename = f"{symbol}_{safe_date}.html"
    path = os.path.join(debug_dir, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[DEBUG] Saved HTML copy to {path}")
    except Exception as e:
        print(f"[DEBUG] Failed to save HTML copy: {e}")

# ... all your imports and helper functions remain unchanged ...

def parse_balance_sheet_html(html_path, symbol, filing_date=None):
    print(f"Parsing balance sheet from: {html_path}")
    if not os.path.exists(html_path):
        print(f"HTML file not found: {html_path}")
        return []

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    save_debug_html(symbol, filing_date, html_content)
    soup = BeautifulSoup(html_content, "html.parser")

    table_tag = soup.find("table")
    if not table_tag:
        print("No table found in HTML.")
        return []

    # Detect header row with dates
    header_found = False
    date_headers = []
    label_col_index = 0
    for tr in table_tag.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        header_texts = [preclean_header_cell(c.get_text(" ", strip=True)) for c in cells]
        date_cols = [i for i, txt in enumerate(header_texts) if looks_like_date(txt)]
        if date_cols:
            date_headers = [to_iso_date(header_texts[i]) for i in date_cols]
            label_col_index = next((i for i in range(len(header_texts)) if i not in date_cols), 0)
            header_found = True
            break
    if not header_found:
        print("Could not detect header row with dates.")
        return []

    rows = []
    current_section = None
    current_sub_section = None
    current_category = None
    sub_section_sums = {}
    category_sums = {}

    for tr in table_tag.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue

        # Label extraction: first non-empty cell
        label = next((td.get_text(" ", strip=True) for td in cells if td.get_text(" ", strip=True)), None)
        if not label:
            continue
        label_norm = label.lower().replace(":", "")

        # Skip rows that are already totals in HTML
        if "total" in label_norm:
            continue

        # Update category and section
        if "assets" in label_norm:
            current_category = "Assets"
        elif "liabilities" in label_norm or "equity" in label_norm:
            current_category = "Liabilities and Stockholders’ Equity"

        if re.match(r"^[A-Z\s]+$", label) or any(kw in label_norm for kw in ["assets", "liabilities", "equity"]):
            current_section = label.title()
            current_sub_section = None
            continue

        if any(kw in label_norm for kw in ["current", "non-current", "other current assets", "other assets"]):
            current_sub_section = label.title()
            if current_sub_section not in sub_section_sums:
                sub_section_sums[current_sub_section] = (current_category, current_section, [0.0 for _ in date_headers])
            continue

        # Extract numeric values
        values = []
        for td in cells[label_col_index + 1: label_col_index + 1 + len(date_headers)]:
            ix_val = td.find("ix:nonfraction")
            if ix_val:
                val = clean_value(ix_val.get_text())
            else:
                val = clean_value(td.get_text())
            values.append(val)

        # Skip rows with no numeric values
        if not any(v is not None for v in values):
            continue

        # Update sums
        if current_sub_section:
            cat, sec, sums = sub_section_sums[current_sub_section]
            for i, val in enumerate(values):
                if val is not None:
                    sums[i] += val
            sub_section_sums[current_sub_section] = (cat, sec, sums)

        if current_category:
            if current_category not in category_sums:
                category_sums[current_category] = [0.0 for _ in date_headers]
            for i, val in enumerate(values):
                if val is not None:
                    category_sums[current_category][i] += val

        row_dict = {
            "symbol": symbol,
            "label": label,
            "values": {date_headers[i]: values[i] for i in range(len(values)) if values[i] is not None},
            "category": current_category,
            "section": current_section,
            "sub_section": current_sub_section,
            "path": " / ".join(filter(None, [current_section, current_sub_section])),
            "is_total": False
        }
        if filing_date:
            row_dict["filing_date"] = filing_date

        # DEBUG: print info for each row
        print(f"[DEBUG ROW] label='{label}' | norm='{label_norm}' | values={values} | section='{current_section}' | sub_section='{current_sub_section}' | category='{current_category}'")

        rows.append(row_dict)

    # Append computed sub-section totals
    for sub_section, (cat, sec, sums) in sub_section_sums.items():
        row_dict = {
            "symbol": symbol,
            "label": f"Total {sub_section}",
            "values": {date_headers[i]: sums[i] for i in range(len(sums))},
            "category": cat,
            "section": sec,
            "sub_section": sub_section,
            "path": " / ".join(filter(None, [sec, sub_section])),
            "is_total": True
        }
        if filing_date:
            row_dict["filing_date"] = filing_date
        rows.append(row_dict)

    # Append category totals
    for category, sums in category_sums.items():
        row_dict = {
            "symbol": symbol,
            "label": f"Total {category}",
            "values": {date_headers[i]: sums[i] for i in range(len(sums))},
            "category": category,
            "section": None,
            "sub_section": None,
            "path": category,
            "is_total": True
        }
        if filing_date:
            row_dict["filing_date"] = filing_date
        rows.append(row_dict)

    print(f"Parsed {len(rows)} balance sheet rows with computed totals.")
    return rows

