import sqlite3

DB_NAME = "balance_sheets.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS balance_sheet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            label TEXT,
            value_1 TEXT,
            value_2 TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_balance_sheet_rows(symbol: str, rows: list[dict]):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for row in rows:
        values = list(row.values())
        label = values[0] if values else ""
        value_1 = values[1] if len(values) > 1 else None
        value_2 = values[2] if len(values) > 2 else None

        cur.execute("""
            INSERT INTO balance_sheet (symbol, label, value_1, value_2)
            VALUES (?, ?, ?, ?)
        """, (symbol, label, value_1, value_2))

    conn.commit()
    conn.close()
