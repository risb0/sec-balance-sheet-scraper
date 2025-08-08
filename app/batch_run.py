from edgar import fetch_and_parse_latest_10q
from parser import parse_balance_sheet_html
from mongo_utils import init_db, insert_balance_sheet_rows

SYMBOLS = ["AAPL", "MSFT", "GOOG"]  # Add more symbols if needed

def process_symbol(symbol):
    print(f"\nProcessing {symbol}...")

    try:
        fetch_and_parse_latest_10q(symbol)

        try:
            with open("balance_sheet.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            print("balance_sheet.html not found.")
            return

        rows = parse_balance_sheet_html("balance_sheet.html", symbol)

        if not rows:
            print("No rows extracted for", symbol)
            return

        insert_balance_sheet_rows(symbol, rows)
        print(f"Inserted {len(rows)} rows into MongoDB for {symbol}")

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

def main():
    init_db()
    for symbol in SYMBOLS:
        process_symbol(symbol)

if __name__ == "__main__":
    main()