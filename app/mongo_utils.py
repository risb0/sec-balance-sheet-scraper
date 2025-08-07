from pymongo import MongoClient
import os

MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "sec_data")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "balance_sheets")

client = None

def init_db():
    global client
    if not client:
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    return client[MONGO_DB][MONGO_COLLECTION]

def insert_balance_sheet_rows(symbol, rows):
    collection = init_db()
    collection.delete_many({"symbol": symbol})  # Avoid duplicates
    collection.insert_many(rows)
    print(f"Inserted {len(rows)} rows into MongoDB for {symbol}")
