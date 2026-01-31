"""Parser for misc pages: arenas, HCA, game attrs, program ratings, point distribution."""

from io import StringIO

from bs4 import BeautifulSoup

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def parse_arenas(soup: BeautifulSoup) -> list[dict]:
    """Parse arenas table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        df = df[df.iloc[:, 1] != df.columns[1]]
        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def parse_hca(soup: BeautifulSoup) -> list[dict]:
    """Parse home court advantage table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        columns = [
            "Rank",
            "Team",
            "Conference",
            "HCA",
            "HCA_Rank",
            "PF",
            "PF_Rank",
            "Home_Record",
            "Pts_Diff",
        ]
        df.columns = columns[: len(df.columns)]
        df = df[df["Team"] != "Team"]

        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def parse_game_attrs(soup: BeautifulSoup) -> list[dict]:
    """Parse game attributes table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        columns = ["Rank", "Date", "Game", "Box", "Location", "Conf_Matchup", "Value"]
        df.columns = columns[: len(df.columns)]

        # Drop Box column and parse Location/Arena
        if "Box" in df.columns:
            df = df.drop("Box", axis=1)

        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def parse_program_ratings(soup: BeautifulSoup) -> list[dict]:
    """Parse program ratings table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        columns = [
            "Rank",
            "Team",
            "Conference",
            "Rating",
            "Best_Rank",
            "Best_Season",
            "Worst_Rank",
            "Worst_Season",
            "Median_Rank",
            "Top10",
            "Top25",
            "Top50",
            "NCAA_Champs",
            "NCAA_F4",
            "NCAA_S16",
            "NCAA_R1",
            "Change",
        ]
        df.columns = columns[: len(df.columns)]
        df = df[df["Team"] != "Team"]

        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def parse_point_distribution(soup: BeautifulSoup) -> list[dict]:
    """Parse point distribution table."""
    table = soup.find_all("table")[0]

    if HAS_PANDAS:
        df = pd.read_html(StringIO(str(table)))[0]

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(col).strip() for col in df.columns.values]

        df = df[df.iloc[:, 1] != df.columns[1]]
        return df.to_dict(orient="records")
    else:
        return _parse_table_fallback(table)


def _parse_table_fallback(table) -> list[dict]:
    """Pure Python table parsing fallback."""
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
