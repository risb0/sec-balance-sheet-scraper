from pymongo import MongoClient
from collections import defaultdict

MONGO_URI = "mongodb://mongodb:27017"
DB_NAME = "sec_scraper"

BALANCE_SHEET_COLLECTION = "balance_sheets"
METRICS_COLLECTION = "balance_sheet_metrics"


def compute_metrics_for_symbol(symbol: str):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    bs_col = db[BALANCE_SHEET_COLLECTION]
    metrics_col = db[METRICS_COLLECTION]

    # Group rows by filing_date
    filings = defaultdict(list)
    for doc in bs_col.find({"symbol": symbol}):
        filing_date = doc.get("filing_date")
        if filing_date:
            filings[filing_date].append(doc)

    for filing_date, rows in filings.items():
        totals = {
            "current_assets": 0.0,
            "current_liabilities": 0.0,
            "total_assets": 0.0,
            "total_liabilities": 0.0,
        }

        for row in rows:
            label = row.get("label", "").lower()
            values = row.get("values", {})

            # Take the single value for this filing
            if not values:
                continue
            value = list(values.values())[0]
            if value is None:
                continue

            if label == "total current assets":
                totals["current_assets"] = value
            elif label == "total current liabilities":
                totals["current_liabilities"] = value
            elif label == "total assets":
                totals["total_assets"] = value
            elif label == "total liabilities":
                totals["total_liabilities"] = value

        # Compute derived metrics
        current_assets = totals["current_assets"]
        current_liabilities = totals["current_liabilities"]

        working_capital = None
        current_ratio = None

        if current_assets and current_liabilities and current_liabilities != 0:
            working_capital = current_assets - current_liabilities
            current_ratio = current_assets / current_liabilities

        metrics_doc = {
            "symbol": symbol,
            "filing_date": filing_date,
            "metrics": {
                "current_assets": current_assets,
                "current_liabilities": current_liabilities,
                "working_capital": working_capital,
                "current_ratio": current_ratio,
                "total_assets": totals["total_assets"],
                "total_liabilities": totals["total_liabilities"],
            },
        }

        metrics_col.replace_one(
            {"symbol": symbol, "filing_date": filing_date},
            metrics_doc,
            upsert=True,
        )

        print(f"[METRICS] Stored metrics for {symbol} {filing_date}")

    client.close()


if __name__ == "__main__":
    compute_metrics_for_symbol("AAPL")
