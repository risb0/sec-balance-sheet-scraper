# app/mongo_utils.py

import os
from pymongo import MongoClient

_client = None

def init_db():
    global _client
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    _client = MongoClient(mongo_uri)
    print("MongoDB client initialized.")

def insert_balance_sheet_rows(symbol, rows, filing_date):
    if not _client:
        raise RuntimeError("MongoDB client not initialized. Call init_db() first.")

    db = _client["sec_scraper"]
    collection = db["balance_sheets"]

    # Tag each row with the symbol and filing date
    for row in rows:
        row["symbol"] = symbol
        row["filing_date"] = filing_date

    result = collection.insert_many(rows)
    print(f"Inserted {len(result.inserted_ids)} documents for {symbol} into MongoDB.")
