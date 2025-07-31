# 🧾 SEC Balance Sheet Scraper

This tool fetches the latest 10-Q filing from SEC EDGAR for a given company (e.g., AAPL), extracts the **Condensed Consolidated Balance Sheets (Unaudited)** section, and stores it in a local SQLite database.

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/yourusername/sec-balance-sheet-scraper.git
cd sec-balance-sheet-scraper

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py