from edgar import fetch_and_parse_latest_10q

def main():
    symbol = input("Enter stock symbol (e.g. AAPL): ").strip().upper()
    fetch_and_parse_latest_10q(symbol)

if __name__ == "__main__":
    main()
