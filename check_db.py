import sqlite3

def print_sample_rows(symbol='AAPL'):
    conn = sqlite3.connect("balance_sheets.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM balance_sheet
        WHERE symbol = ?
        LIMIT 10
    """, (symbol.upper(),))

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(row)

if __name__ == "__main__":
    print_sample_rows()