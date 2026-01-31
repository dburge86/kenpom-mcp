"""Parser for efficiency and four factors pages."""

from io import StringIO

from bs4 import BeautifulSoup

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def parse_efficiency(soup: BeautifulSoup) -> list[dict]:
    """Parse efficiency summary table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        # Standard column names
        columns = [
            "Rank",
            "Team",
            "Conference",
            "AdjT",
            "AdjT_Rank",
            "RawT",
            "RawT_Rank",
            "Avg_Poss_Len_Off",
            "Avg_Poss_Len_Off_Rank",
            "Avg_Poss_Len_Def",
            "Avg_Poss_Len_Def_Rank",
            "AdjOE",
            "AdjOE_Rank",
            "RawOE",
            "RawOE_Rank",
            "AdjDE",
            "AdjDE_Rank",
            "RawDE",
            "RawDE_Rank",
        ]
        df.columns = columns[: len(df.columns)]
        df = df[df["Team"] != "Team"]

        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def parse_four_factors(soup: BeautifulSoup) -> list[dict]:
    """Parse four factors table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        columns = [
            "Rank",
            "Team",
            "Conference",
            "AdjOE",
            "AdjDE",
            "Off_eFG_Pct",
            "Off_eFG_Pct_Rank",
            "Off_TO_Pct",
            "Off_TO_Pct_Rank",
            "Off_OR_Pct",
            "Off_OR_Pct_Rank",
            "Off_FTRate",
            "Off_FTRate_Rank",
            "Def_eFG_Pct",
            "Def_eFG_Pct_Rank",
            "Def_TO_Pct",
            "Def_TO_Pct_Rank",
            "Def_OR_Pct",
            "Def_OR_Pct_Rank",
            "Def_FTRate",
            "Def_FTRate_Rank",
        ]
        df.columns = columns[: len(df.columns)]
        df = df[df["Team"] != "Team"]

        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def _parse_table_fallback(table) -> list[dict]:
    """Pure Python table parsing fallback."""
    rows = []
    headers = []

    # Get headers
    header_row = table.find("tr")
    if header_row:
        headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

    # Get data rows
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["td", "th"])
        if cells:
            row = {}
            for i, cell in enumerate(cells):
                key = headers[i] if i < len(headers) else f"col_{i}"
                row[key] = cell.get_text(strip=True)
            if row.get("Team") and row.get("Team") != "Team":
                rows.append(row)

    return rows
