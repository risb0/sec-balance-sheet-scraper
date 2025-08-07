# SEC Balance Sheet Scraper

Scrapes the latest 10-Q balance sheet data from EDGAR and stores it in MongoDB.

## Quick Start

```bash
docker-compose up --build

MongoDB will be available on port 27017 and populated with the latest balance sheet data for AAPL, MSFT, and GOOG.
Data Location

MongoDB database: sec
Collection: balance_sheets