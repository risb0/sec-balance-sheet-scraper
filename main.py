from edgar import fetch_and_parse_latest_10q
from parser import parse_balance_sheet_html
from db import init_db, insert_balance_sheet_rows

def main():
    symbol = input("Enter stock symbol (e.g. AAPL): ").strip().upper()

    init_db()

    fetch_and_parse_latest_10q(symbol)

    rows = parse_balance_sheet_html("balance_sheet.html")
    print(f"\n✅ Parsed {len(rows)} rows from balance sheet")

    insert_balance_sheet_rows(symbol, rows)
    print("✅ Inserted into database")

if __name__ == "__main__":
    main()
