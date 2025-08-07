import sqlite3
import csv

DB_NAME = "balance_sheets.db"
CSV_FILE = "balance_sheets.csv"

def export_to_csv():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol, label, date_1, value_1, date_2, value_2
        FROM balance_sheet
    """)

    rows = cur.fetchall()
    headers = ["symbol", "label", "date_1", "value_1", "date_2", "value_2"]

    with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ Exported {len(rows)} rows to {CSV_FILE}")

if __name__ == "__main__":
    export_to_csv()
