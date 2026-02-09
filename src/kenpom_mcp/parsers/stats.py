"""Parser for team stats, player stats, height, and KPOY pages."""

from bs4 import BeautifulSoup


def parse_team_stats(soup: BeautifulSoup, defense: bool = False) -> list[dict]:
    """Parse miscellaneous team stats table (offense or defense).

    Structure: 1 header row (row 0 with colspans), data starts row 1, 22 cells per row.
    Columns: Team, Conf, then 10 stat pairs (value + rank).
    Offense: 3P%, 2P%, FT%, Blk%, Stl%, NST%, 2P Dist, A%, 3PA%, AdjOE
    Defense: 3P%, 2P%, FT%, Blk%, Stl%, NST%, 2P Dist, A%, 3PA%, AdjDE
    """
    table = soup.find_all("table")[0]
    all_rows = table.find_all("tr")
    data_rows = all_rows[1:]  # Skip 1 header row

    results = []
    rank = 1
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 22:
            team_link = cells[0].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

            if team == "Team":
                continue

            row = {
                "Rank": str(rank),
                "Team": team,
                "Conference": cells[1].get_text(strip=True),
                "3P_Pct": cells[2].get_text(strip=True),
                "3P_Pct_Rank": cells[3].get_text(strip=True),
                "2P_Pct": cells[4].get_text(strip=True),
                "2P_Pct_Rank": cells[5].get_text(strip=True),
                "FT_Pct": cells[6].get_text(strip=True),
                "FT_Pct_Rank": cells[7].get_text(strip=True),
                "Blk_Pct": cells[8].get_text(strip=True),
                "Blk_Pct_Rank": cells[9].get_text(strip=True),
                "Stl_Pct": cells[10].get_text(strip=True),
                "Stl_Pct_Rank": cells[11].get_text(strip=True),
                "NST_Pct": cells[12].get_text(strip=True),
                "NST_Pct_Rank": cells[13].get_text(strip=True),
                "2P_Dist": cells[14].get_text(strip=True),
                "2P_Dist_Rank": cells[15].get_text(strip=True),
                "A_Pct": cells[16].get_text(strip=True),
                "A_Pct_Rank": cells[17].get_text(strip=True),
                "3PA_Pct": cells[18].get_text(strip=True),
                "3PA_Pct_Rank": cells[19].get_text(strip=True),
                "AdjEff": cells[20].get_text(strip=True),
                "AdjEff_Rank": cells[21].get_text(strip=True),
            }
            results.append(row)
            rank += 1

    return results


def parse_player_stats(soup: BeautifulSoup) -> list[dict]:
    """Parse player stats table.

    Structure: Row 0 empty, Row 1 headers, data starts row 2, 7 cells per row.
    Columns: Rk, Player (<a>), Team (<a>), Metric, Ht, Wt, Yr
    The metric column name changes based on the sort parameter (eFG%, ORtg, etc.).
    """
    table = soup.find_all("table")[0]
    all_rows = table.find_all("tr")

    # Get the metric name from header row (row 1)
    metric_name = "Value"
    if len(all_rows) > 1:
        header_cells = all_rows[1].find_all(["td", "th"])
        if len(header_cells) >= 4:
            metric_name = header_cells[3].get_text(strip=True)

    data_rows = all_rows[2:]  # Skip empty row 0 and header row 1

    results = []
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 7:
            player_link = cells[1].find("a")
            player = (
                player_link.get_text(strip=True) if player_link else cells[1].get_text(strip=True)
            )

            team_link = cells[2].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[2].get_text(strip=True)

            if player == "Player":
                continue

            row = {
                "Rank": cells[0].get_text(strip=True),
                "Player": player,
                "Team": team,
                metric_name: cells[3].get_text(strip=True),
                "Height": cells[4].get_text(strip=True),
                "Weight": cells[5].get_text(strip=True),
                "Year": cells[6].get_text(strip=True),
            }
            results.append(row)

    return results


def parse_height(soup: BeautifulSoup) -> list[dict]:
    """Parse height/experience table.

    Structure: 1 header row (row 0 with colspans), data starts row 1, 22 cells per row.
    Columns: Team, Conf, then 10 stat pairs (value + rank):
    Avg Hgt, Eff Hgt, C Hgt, PF Hgt, SF Hgt, SG Hgt, PG Hgt, Experience, Bench, Continuity
    """
    table = soup.find_all("table")[0]
    all_rows = table.find_all("tr")
    data_rows = all_rows[1:]  # Skip 1 header row

    results = []
    rank = 1
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 22:
            team_link = cells[0].find("a")
            team = team_link.get_text(strip=True) if team_link else cells[0].get_text(strip=True)

            if team == "Team":
                continue

            row = {
                "Rank": str(rank),
                "Team": team,
                "Conference": cells[1].get_text(strip=True),
                "Avg_Hgt": cells[2].get_text(strip=True),
                "Avg_Hgt_Rank": cells[3].get_text(strip=True),
                "Eff_Hgt": cells[4].get_text(strip=True),
                "Eff_Hgt_Rank": cells[5].get_text(strip=True),
                "C_Hgt": cells[6].get_text(strip=True),
                "C_Hgt_Rank": cells[7].get_text(strip=True),
                "PF_Hgt": cells[8].get_text(strip=True),
                "PF_Hgt_Rank": cells[9].get_text(strip=True),
                "SF_Hgt": cells[10].get_text(strip=True),
                "SF_Hgt_Rank": cells[11].get_text(strip=True),
                "SG_Hgt": cells[12].get_text(strip=True),
                "SG_Hgt_Rank": cells[13].get_text(strip=True),
                "PG_Hgt": cells[14].get_text(strip=True),
                "PG_Hgt_Rank": cells[15].get_text(strip=True),
                "Experience": cells[16].get_text(strip=True),
                "Experience_Rank": cells[17].get_text(strip=True),
                "Bench": cells[18].get_text(strip=True),
                "Bench_Rank": cells[19].get_text(strip=True),
                "Continuity": cells[20].get_text(strip=True),
                "Continuity_Rank": cells[21].get_text(strip=True),
            }
            results.append(row)
            rank += 1

    return results


def parse_kpoy(soup: BeautifulSoup) -> list[list[dict]]:
    """Parse KPOY tables (returns [kPOY standings, Game MVP leaders]).

    Structure: 2 tables, each with 1 header row (row 0), 3 cells per row.
    Player cell contains <a> links for player name and team name,
    plus a <div class="playerinfo"> with height/weight/year.
    """
    tables = soup.find_all("table")
    results = []

    for table in tables[:2]:
        rows = table.find_all("tr")

        # Get the metric name from header (e.g., "kPOYRating" or "GameMVP's")
        metric_name = "Value"
        if rows:
            header_cells = rows[0].find_all(["td", "th"])
            if len(header_cells) >= 3:
                metric_name = header_cells[2].get_text(strip=True)

        data_rows = rows[1:]  # Skip header
        table_results = []

        for tr in data_rows:
            cells = tr.find_all(["td", "th"])
            if len(cells) >= 3:
                rank_text = cells[0].get_text(strip=True)

                # Parse player cell - first <a> = player name, second <a> = team
                player_cell = cells[1]
                links = player_cell.find_all("a")
                player = links[0].get_text(strip=True) if len(links) >= 1 else ""
                team = links[1].get_text(strip=True) if len(links) >= 2 else ""

                if player == "Player":
                    continue

                row = {
                    "Rank": rank_text,
                    "Player": player,
                    "Team": team,
                    metric_name: cells[2].get_text(strip=True),
                }
                table_results.append(row)

        results.append(table_results)

    return results
