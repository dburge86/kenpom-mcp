"""Parser for team stats, player stats, height, and KPOY pages."""

import re
from io import StringIO
from bs4 import BeautifulSoup

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def parse_team_stats(soup: BeautifulSoup, defense: bool = False) -> list[dict]:
    """Parse team stats table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]
        
        # Clean up column names
        df.columns = [re.sub(r"\s+", "_", col) for col in df.columns]
        df = df[df.iloc[:, 1] != df.columns[1]]  # Remove header rows
        
        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(soup)


def parse_player_stats(soup: BeautifulSoup) -> list[dict]:
    """Parse player stats table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]
        
        # Standard player stats columns
        columns = [
            "Rank", "Player", "Team", "Height", "Weight", "Year",
            "Value", "O_Rtg", "Usage", "eFG_Pct", "TS_Pct"
        ]
        df.columns = columns[:len(df.columns)]
        df = df[df["Player"] != "Player"]
        
        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(soup)


def parse_height(soup: BeautifulSoup) -> list[dict]:
    """Parse height/experience table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]
        
        columns = [
            "Rank", "Team", "Conference", "Avg_Hgt", "Avg_Hgt_Rank",
            "Eff_Hgt", "Eff_Hgt_Rank", "Experience", "Exp_Rank",
            "Bench", "Bench_Rank", "Continuity", "Cont_Rank"
        ]
        df.columns = columns[:len(df.columns)]
        df = df[df["Team"] != "Team"]
        
        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(soup)


def parse_kpoy(soup: BeautifulSoup) -> list[list[dict]]:
    """Parse KPOY tables (returns list of tables)."""
    tables = soup.find_all("table")
    results = []

    for table in tables[:2]:  # KPOY and MVP tables
        if HAS_PANDAS:
            df = pd.read_html(StringIO(str(table)))[0]
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join(col).strip() for col in df.columns.values]
            
            df = df[df.iloc[:, 1] != df.columns[1]]
            results.append(df.to_dict(orient="records"))
        else:
            results.append(_parse_table_fallback_simple(table))

    return results


def _parse_table_fallback(soup: BeautifulSoup) -> list[dict]:
    """Pure Python fallback for table parsing."""
    table = soup.find("table")
    return _parse_table_fallback_simple(table) if table else []


def _parse_table_fallback_simple(table) -> list[dict]:
    """Parse a single table without pandas."""
    rows = []
    headers = []
    
    header_row = table.find("tr")
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
    
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["td", "th"])
        if cells:
            row = {}
            for i, cell in enumerate(cells):
                key = headers[i] if i < len(headers) else f"col_{i}"
                row[key] = cell.get_text(strip=True)
            rows.append(row)
    
    return rows
