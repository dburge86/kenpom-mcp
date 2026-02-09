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
    """Parse home court advantage table.

    Structure: 2 header rows, data starts row 2, 14 cells per row.
    Columns: Team (<a>), Conf (<a>), then 6 stat pairs (value + rank):
    HCA, PF, Pts, NST, Blk, Elev
    """
    table = soup.find_all("table")[0]
    all_rows = table.find_all("tr")
    data_rows = all_rows[2:]  # Skip 2 header rows

    results = []
    rank = 1
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 14:
            team_link = cells[0].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

            if team == "Team":
                continue

            row = {
                "Rank": str(rank),
                "Team": team,
                "Conference": cells[1].get_text(strip=True),
                "HCA": cells[2].get_text(strip=True),
                "HCA_Rank": cells[3].get_text(strip=True),
                "PF": cells[4].get_text(strip=True),
                "PF_Rank": cells[5].get_text(strip=True),
                "Pts": cells[6].get_text(strip=True),
                "Pts_Rank": cells[7].get_text(strip=True),
                "NST": cells[8].get_text(strip=True),
                "NST_Rank": cells[9].get_text(strip=True),
                "Blk": cells[10].get_text(strip=True),
                "Blk_Rank": cells[11].get_text(strip=True),
                "Elev": cells[12].get_text(strip=True),
                "Elev_Rank": cells[13].get_text(strip=True),
            }
            results.append(row)
            rank += 1

    return results


def parse_game_attrs(soup: BeautifulSoup) -> list[dict]:
    """Parse game attributes table.

    Structure: 1 header row, data starts row 1, 7 cells per row.
    Columns: Rank, Date (<a>), Game (2 team <a> links), Box links, Location, Conf, Value
    """
    table = soup.find_all("table")[0]
    all_rows = table.find_all("tr")
    data_rows = all_rows[1:]  # Skip 1 header row

    results = []
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 7:
            rank = cells[0].get_text(strip=True)

            # Date cell
            date = cells[1].get_text(strip=True)

            # Game cell has team links
            game_cell = cells[2]
            team_links = game_cell.find_all("a")
            team1 = team_links[0].get_text(strip=True) if len(team_links) >= 1 else ""
            team2 = team_links[1].get_text(strip=True) if len(team_links) >= 2 else ""
            game_text = game_cell.get_text(strip=True)

            # Location cell
            location = cells[4].get_text(strip=True)

            # Conference cell
            conference = cells[5].get_text(strip=True)

            # Value cell
            value = cells[6].get_text(strip=True)

            row = {
                "Rank": rank,
                "Date": date,
                "Game": game_text,
                "Team1": team1,
                "Team2": team2,
                "Location": location,
                "Conference": conference,
                "Value": value,
            }
            results.append(row)

    return results


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
    """Parse point distribution table.

    Structure: 2 header rows, data starts row 2, 14 cells per row.
    Columns: Team (<a>), Conf (<a>), then 6 stat pairs (value + rank):
    Off FT, Off 2P FG, Off 3P FG, Def FT, Def 2P FG, Def 3P FG
    """
    table = soup.find_all("table")[0]
    all_rows = table.find_all("tr")
    data_rows = all_rows[2:]  # Skip 2 header rows

    results = []
    rank = 1
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 14:
            team_link = cells[0].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

            if team == "Team":
                continue

            row = {
                "Rank": str(rank),
                "Team": team,
                "Conference": cells[1].get_text(strip=True),
                "Off_FT": cells[2].get_text(strip=True),
                "Off_FT_Rank": cells[3].get_text(strip=True),
                "Off_2P": cells[4].get_text(strip=True),
                "Off_2P_Rank": cells[5].get_text(strip=True),
                "Off_3P": cells[6].get_text(strip=True),
                "Off_3P_Rank": cells[7].get_text(strip=True),
                "Def_FT": cells[8].get_text(strip=True),
                "Def_FT_Rank": cells[9].get_text(strip=True),
                "Def_2P": cells[10].get_text(strip=True),
                "Def_2P_Rank": cells[11].get_text(strip=True),
                "Def_3P": cells[12].get_text(strip=True),
                "Def_3P_Rank": cells[13].get_text(strip=True),
            }
            results.append(row)
            rank += 1

    return results


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
