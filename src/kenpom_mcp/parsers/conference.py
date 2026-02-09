"""Parser for conference pages: standings, offense, and defense."""

from bs4 import BeautifulSoup


def parse_conference_standings(soup: BeautifulSoup) -> list[dict]:
    """Parse conference standings table (table index 0 on conf page).

    Structure: Row 0 is header (10 visible columns), data rows have 16 cells
    because rank values are interleaved with stat values.
    Columns: Team, Overall, Conf, Proj, NetRtg, NetRtg_Rank, ORtg, ORtg_Rank,
             DRtg, DRtg_Rank, AdjT, AdjT_Rank, ConfSOS, ConfSOS_Rank, NextGame, NextGame_Rank
    """
    tables = soup.find_all("table")
    if not tables:
        return []

    table = tables[0]
    all_rows = table.find_all("tr")
    data_rows = all_rows[1:]  # Skip header row

    results = []
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) < 10:
            continue

        team_link = cells[0].find("a")
        team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

        if team == "Team":
            continue

        row = {
            "Team": team,
            "Overall": cells[1].get_text(strip=True),
            "Conf": cells[2].get_text(strip=True),
            "Proj": cells[3].get_text(strip=True),
            "NetRtg": cells[4].get_text(strip=True),
        }

        # Data rows have interleaved rank cells (16 total)
        if len(cells) >= 16:
            row.update(
                {
                    "NetRtg_Rank": cells[5].get_text(strip=True),
                    "ORtg": cells[6].get_text(strip=True),
                    "ORtg_Rank": cells[7].get_text(strip=True),
                    "DRtg": cells[8].get_text(strip=True),
                    "DRtg_Rank": cells[9].get_text(strip=True),
                    "AdjT": cells[10].get_text(strip=True),
                    "AdjT_Rank": cells[11].get_text(strip=True),
                    "Conf_SOS": cells[12].get_text(strip=True),
                    "Conf_SOS_Rank": cells[13].get_text(strip=True),
                    "Next_Game": cells[14].get_text(strip=True),
                    "Next_Game_Rank": cells[15].get_text(strip=True),
                }
            )

        results.append(row)

    return results


def _parse_conference_stats_table(soup: BeautifulSoup, table_index: int) -> list[dict]:
    """Parse conference offense or defense table.

    Structure: Row 0 is header (10 visible columns), data rows have 19 cells
    (team + 9 stat pairs of value + rank).
    """
    tables = soup.find_all("table")
    if len(tables) <= table_index:
        return []

    table = tables[table_index]
    all_rows = table.find_all("tr")
    if not all_rows:
        return []

    # Get column names from header row
    header_cells = all_rows[0].find_all(["td", "th"])
    header_names = [c.get_text(strip=True) for c in header_cells]
    # First header is "Team", rest are stat names
    stat_names = header_names[1:] if len(header_names) > 1 else []

    data_rows = all_rows[1:]

    results = []
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) < 3:
            continue

        team_link = cells[0].find("a")
        team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

        if team == "Team":
            continue

        row: dict = {"Team": team}

        # Map remaining cells as value+rank pairs for each stat
        cell_idx = 1
        for stat in stat_names:
            if cell_idx < len(cells):
                row[stat] = cells[cell_idx].get_text(strip=True)
                cell_idx += 1
            if cell_idx < len(cells):
                row[f"{stat}_Rank"] = cells[cell_idx].get_text(strip=True)
                cell_idx += 1

        results.append(row)

    return results


def parse_conference_offense(soup: BeautifulSoup) -> list[dict]:
    """Parse conference offensive stats (table index 1).

    Columns: Team, OE, eFG%, TO%, OR%, FTR, 2P%, 3P%, FT%, Tempo
    Each stat has a value and rank (19 cells per data row).
    """
    return _parse_conference_stats_table(soup, table_index=1)


def parse_conference_defense(soup: BeautifulSoup) -> list[dict]:
    """Parse conference defensive stats (table index 2).

    Columns: Team, DE, eFG%, TO%, OR%, FTR, 2P%, 3P%, Blk%, Stl%
    Each stat has a value and rank (19 cells per data row).
    """
    return _parse_conference_stats_table(soup, table_index=2)
