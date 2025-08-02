# 🧾 SEC Balance Sheet Scraper

This tool fetches the latest 10-Q filing from SEC EDGAR for a given company (e.g., AAPL), extracts the **Condensed Consolidated Balance Sheets (Unaudited)** section, and stores it in a local SQLite database.

## 🛠 Install and Run

```bash
git clone https://github.com/yourusername/sec-balance-sheet-scraper
cd sec-balance-sheet-scraper

# Install dependencies
pip install -r requirements.txt

# Run the program
python main.py
