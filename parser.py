from bs4 import BeautifulSoup

def parse_balance_sheet_html(filepath: str) -> list[dict]:
    """Parses balance_sheet.html into a list of row dictionaries."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table")
    rows = table.find_all("tr")

    headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
    data_rows = []

    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        values = [cell.get_text(strip=True) for cell in cells]
        if values:
            entry = dict(zip(headers, values))
            data_rows.append(entry)

    return data_rows
