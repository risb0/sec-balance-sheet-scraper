SEC Balance Sheet Scraper

This tool scrapes the "Condensed Consolidated Balance Sheets" from the latest 10-Q SEC filings for a given stock symbol.
It saves the data to a local SQLite database and lets you inspect the results via the command line.
Quickstart

    Clone the repository:

    git clone https://github.com/yourusername/sec-balance-sheet-scraper.git
    cd sec-balance-sheet-scraper

    (Optional) Create and activate a virtual environment:

    python -m venv venv
    venv\Scripts\activate (on Windows)
    source venv/bin/activate (on Unix/macOS)

    Install dependencies:

    pip install -r requirements.txt

    If requirements.txt is missing, create it manually with these contents:

     beautifulsoup4
     requests

    Then run the install command again.

How to Use

Step 1: Initialize the database

python db.py

This will create a file named balance_sheets.db.

Step 2: Scrape the 10-Q balance sheet

python main.py

You'll be prompted to enter a stock symbol:

Enter stock symbol (e.g. AAPL): AAPL

If successful, you'll see:

Parsed 27 rows from balance sheet
Inserted into database

Step 3: Inspect the stored data

python inspect_db.py

You should see a table-like display of the balance sheet data, e.g.:

Cash and cash equivalents        | June 28, 2025 | 36,269 | September 28, 2024 | 29,943
Marketable securities            | June 28, 2025 | 19,103 | September 28, 2024 | 35,228
...
Total liabilities and equity     | June 28, 2025 | 331,495 | September 28, 2024 | 364,980

Project Files

main.py - Main script to fetch and parse 10-Q filings
edgar.py - Handles CIK lookup, filing search, and HTML extraction
parser.py - Extracts table data from the HTML
db.py - Creates the SQLite database and inserts data
inspect_db.py - Displays parsed data from the database in terminal