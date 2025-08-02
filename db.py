import sqlite3

DB_NAME = "balance_sheets.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS balance_sheet")

    cur.execute("""
        CREATE TABLE balance_sheet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            label TEXT,
            date_1 TEXT,
            value_1 INTEGER,
            date_2 TEXT,
            value_2 INTEGER
        )
    """)

    conn.commit()
    conn.close()



def insert_balance_sheet_rows(symbol: str, rows: list[dict]):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for row in rows:
        cur.execute("""
            INSERT INTO balance_sheet (symbol, label, date_1, value_1, date_2, value_2)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["symbol"],
            row["label"],
            row["date_1"],
            row["value_1"],
            row["date_2"],
            row["value_2"],
        ))

    conn.commit()
    conn.close()
