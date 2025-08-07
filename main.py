from edgar import fetch_and_parse_latest_10q
from parser import parse_balance_sheet_html
from mongo_utils import init_db, insert_balance_sheet_rows

def main():
    symbol = input("Enter stock symbol (e.g. AAPL): ").strip().upper()

    init_db()

    fetch_and_parse_latest_10q(symbol)

    try:
        with open("balance_sheet.html", "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print("Error: balance_sheet.html not found. Exiting.")
        return

    rows = parse_balance_sheet_html("balance_sheet.html", symbol)

    if not rows:
        print("Error: Could not parse balance sheet rows.")
        return

    print(f"\nParsed {len(rows)} rows from balance sheet")

    insert_balance_sheet_rows(symbol, rows)
    print("Inserted into MongoDB")

if __name__ == "__main__":
    main()
