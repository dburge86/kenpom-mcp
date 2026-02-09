"""Parser for efficiency and four factors pages."""

from bs4 import BeautifulSoup


def parse_efficiency(soup: BeautifulSoup) -> list[dict]:
    """Parse efficiency summary table."""
    table = soup.find_all("table")[0]

    # Use direct parsing instead of pandas (more reliable for KenPom's complex headers)
    return _parse_efficiency_direct(table)


def parse_four_factors(soup: BeautifulSoup) -> list[dict]:
    """Parse four factors table."""
    table = soup.find_all("table")[0]

    # Use direct parsing instead of pandas (more reliable for KenPom's complex headers)
    return _parse_four_factors_direct(table)


def _parse_efficiency_direct(table) -> list[dict]:
    """Direct parser for efficiency table that handles KenPom's multi-row headers."""
    rows = []

    # Skip header rows (first 2 rows) and parse data rows directly
    all_rows = table.find_all("tr")
    data_rows = all_rows[2:]  # Skip both header rows

    rank = 1
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 18:  # Ensure we have all expected columns
            # Extract team name from the <a> tag
            team_link = cells[0].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

            # Skip header rows that might appear mid-table
            if team == "Team":
                continue

            row = {
                "Rank": str(rank),
                "Team": team,
                "Conference": cells[1].get_text(strip=True),
                "AdjT": cells[2].get_text(strip=True),
                "AdjT_Rank": cells[3].get_text(strip=True),
                "RawT": cells[4].get_text(strip=True),
                "RawT_Rank": cells[5].get_text(strip=True),
                "Avg_Poss_Len_Off": cells[6].get_text(strip=True),
                "Avg_Poss_Len_Off_Rank": cells[7].get_text(strip=True),
                "Avg_Poss_Len_Def": cells[8].get_text(strip=True),
                "Avg_Poss_Len_Def_Rank": cells[9].get_text(strip=True),
                "AdjOE": cells[10].get_text(strip=True),
                "AdjOE_Rank": cells[11].get_text(strip=True),
                "RawOE": cells[12].get_text(strip=True),
                "RawOE_Rank": cells[13].get_text(strip=True),
                "AdjDE": cells[14].get_text(strip=True),
                "AdjDE_Rank": cells[15].get_text(strip=True),
                "RawDE": cells[16].get_text(strip=True),
                "RawDE_Rank": cells[17].get_text(strip=True),
            }
            rows.append(row)
            rank += 1

    return rows


def _parse_four_factors_direct(table) -> list[dict]:
    """Direct parser for four factors table that handles KenPom's multi-row headers."""
    rows = []

    # Skip header rows (first 2 rows) and parse data rows directly
    all_rows = table.find_all("tr")
    data_rows = all_rows[2:]  # Skip both header rows

    rank = 1
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 24:  # Ensure we have all expected columns (24 total)
            # Extract team name from the <a> tag
            team_link = cells[0].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

            # Skip header rows that might appear mid-table
            if team == "Team":
                continue

            row = {
                "Rank": str(rank),
                "Team": team,
                "Conference": cells[1].get_text(strip=True),
                "AdjTempo": cells[2].get_text(strip=True),
                "AdjTempo_Rank": cells[3].get_text(strip=True),
                "AdjOE": cells[4].get_text(strip=True),
                "AdjOE_Rank": cells[5].get_text(strip=True),
                "Off_eFG_Pct": cells[6].get_text(strip=True),
                "Off_eFG_Pct_Rank": cells[7].get_text(strip=True),
                "Off_TO_Pct": cells[8].get_text(strip=True),
                "Off_TO_Pct_Rank": cells[9].get_text(strip=True),
                "Off_OR_Pct": cells[10].get_text(strip=True),
                "Off_OR_Pct_Rank": cells[11].get_text(strip=True),
                "Off_FTRate": cells[12].get_text(strip=True),
                "Off_FTRate_Rank": cells[13].get_text(strip=True),
                "AdjDE": cells[14].get_text(strip=True),
                "AdjDE_Rank": cells[15].get_text(strip=True),
                "Def_eFG_Pct": cells[16].get_text(strip=True),
                "Def_eFG_Pct_Rank": cells[17].get_text(strip=True),
                "Def_TO_Pct": cells[18].get_text(strip=True),
                "Def_TO_Pct_Rank": cells[19].get_text(strip=True),
                "Def_OR_Pct": cells[20].get_text(strip=True),
                "Def_OR_Pct_Rank": cells[21].get_text(strip=True),
                "Def_FTRate": cells[22].get_text(strip=True),
                "Def_FTRate_Rank": cells[23].get_text(strip=True),
            }
            rows.append(row)
            rank += 1

    return rows


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
