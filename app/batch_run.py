from edgar import fetch_and_parse_latest_10q
from parser import parse_balance_sheet_html
from mongo_utils import init_db, insert_balance_sheet_rows

SYMBOLS = ["AAPL", "MSFT", "GOOG"]  # Add more symbols if needed

def process_symbol(symbol):
    print(f"\nProcessing {symbol}...")

    try:
        result = fetch_and_parse_latest_10q(symbol)
        if not result:
            print(f"Failed to fetch and parse latest 10-Q for {symbol}")
            return
        html_path, filing_date = result  # unpack safely now

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"{html_path} not found.")
            return

        rows = parse_balance_sheet_html(html_path, symbol, filing_date)


        if not rows:
            print("No rows extracted for", symbol)
            return

        insert_balance_sheet_rows(symbol, rows, filing_date)
        print(f"Inserted {len(rows)} rows into MongoDB for {symbol}")

    except Exception as e:
        print(f"Error processing {symbol}: {e}")



def main():
    init_db()
    for symbol in SYMBOLS:
        process_symbol(symbol)

if __name__ == "__main__":
    main()