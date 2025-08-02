import sqlite3

DB_NAME = "balance_sheets.db"

def inspect(symbol: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT label, date_1, value_1, date_2, value_2
        FROM balance_sheet
        WHERE symbol = ?
    """, (symbol,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"No rows found for {symbol}.")
        return

    print(f"Found {len(rows)} balance sheet rows for {symbol}:\n")
    for row in rows:
        label, d1, v1, d2, v2 = row
        print(f"{label[:50]:<50} | {d1} | {v1:,} | {d2} | {v2:,}")

if __name__ == "__main__":
    inspect("AAPL")
