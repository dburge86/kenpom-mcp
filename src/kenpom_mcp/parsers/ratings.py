"""Parser for Pomeroy ratings page."""

import re
from io import StringIO
from bs4 import BeautifulSoup

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def parse_pomeroy_ratings(soup: BeautifulSoup) -> list[dict]:
    """Parse Pomeroy ratings table into list of dicts."""
    table = soup.find("table", {"id": "ratings-table"})
    if not table:
        table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]
        
        # Rename columns to standard names
        df.columns = [
            "Rank", "Team", "Conference", "Record", "AdjEM", "AdjO", "AdjO_Rank",
            "AdjD", "AdjD_Rank", "AdjT", "AdjT_Rank", "Luck", "Luck_Rank",
            "SOS_AdjEM", "SOS_AdjEM_Rank", "SOS_OppO", "SOS_OppO_Rank",
            "SOS_OppD", "SOS_OppD_Rank", "NCSOS_AdjEM", "NCSOS_AdjEM_Rank"
        ][:len(df.columns)]
        
        # Remove header rows that got parsed as data
        df = df[df["Team"] != "Team"]
        
        return df.to_dict(orient="records")
    else:
        # Pure Python fallback for Workers
        rows = []
        for tr in table.find_all("tr")[1:]:  # Skip header
            cells = tr.find_all(["td", "th"])
            if len(cells) >= 5:
                row = {
                    "Rank": cells[0].get_text(strip=True),
                    "Team": cells[1].get_text(strip=True),
                    "Conference": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    "Record": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                    "AdjEM": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                }
                if row["Team"] and row["Team"] != "Team":
                    rows.append(row)
        return rows
