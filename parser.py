from bs4 import BeautifulSoup

import re
from bs4 import BeautifulSoup
from typing import Optional

def parse_balance_sheet_html(html_content: str) -> Optional[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')

    for table in tables:
        table_text = table.get_text(separator=' ', strip=True).lower()

        # Look for common patterns in balance sheet tables
        if (
            "condensed consolidated balance sheets" in table_text
            or "consolidated balance sheets" in table_text
        ):
            print("\nFound a candidate balance sheet table. Preview:\n")
            preview = table_text[:500] + "..." if len(table_text) > 500 else table_text
            print(preview)
            return table.prettify()

    print("No matching balance sheet table found.")
    return None

