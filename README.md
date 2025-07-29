# 🧾 SEC Balance Sheet Scraper

This tool fetches the latest 10-Q filing from SEC EDGAR for a given company (e.g., AAPL), extracts the **Condensed Consolidated Balance Sheets (Unaudited)** section, and stores it in a local SQLite database.

---

## 🚀 Usage

```bash
python main.py


## 🔍 Example Output

Enter stock symbol (e.g. AAPL): AAPL
Found CIK for AAPL: 0000320193
Latest 10-Q filing index URL:
https://www.sec.gov/Archives/edgar/data/320193/000032019324000066/index.json


---

## 🧪 How to Test

```bash
# Clone and run
git clone https://github.com/yourusername/sec-balance-sheet-scraper.git
cd sec-balance-sheet-scraper
python main.py

✅ You’ll be prompted for a stock symbol
✅ You’ll get back the latest 10-Q index URL from EDGAR