# app/mongo_utils.py

import os
from pymongo import MongoClient
from datetime import datetime

_client = None

def init_db():
    """
    Initializes the MongoDB client.
    """
    global _client
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    _client = MongoClient(mongo_uri)
    print(f"MongoDB client initialized at {mongo_uri}")


def insert_balance_sheet_rows(symbol, rows, filing_date):
    """
    Inserts parsed balance sheet rows into MongoDB.
    Each document includes:
        - symbol
        - filing_date
        - section
        - sub_section
        - path
        - label
        - values (date:value mapping)
        - is_total
        - insert_date (timestamp of insertion)
    """
    if not _client:
        raise RuntimeError("MongoDB client not initialized. Call init_db() first.")

    db = _client["sec_scraper"]
    collection = db["balance_sheets"]

    prepared_docs = []
    for row in rows:
        doc = dict(row)  # copy to avoid modifying original
        doc["symbol"] = symbol
        doc["filing_date"] = filing_date
        doc["insert_date"] = datetime.utcnow()  # add current UTC timestamp

        # Ensure section/sub_section/path exist even if parser missed them
        doc["section"] = doc.get("section") or "Unknown"
        doc["sub_section"] = doc.get("sub_section") or None
        doc["path"] = doc.get("path") or doc["section"]

        prepared_docs.append(doc)

    if not prepared_docs:
        print(f"No documents to insert for {symbol} on {filing_date}")
        return

    result = collection.insert_many(prepared_docs)
    print(f"Inserted {len(result.inserted_ids)} documents for {symbol} into MongoDB.")
