"""Parser for team pages: schedule and scouting report."""

import re

from bs4 import BeautifulSoup


def parse_schedule(soup: BeautifulSoup) -> list[dict]:
    """Parse team schedule table (table index 1 on team page).

    Structure: Row 0 is header (10 cells), data rows have 11 cells.
    Columns: Date, TeamRk, OppRk, Opponent, Result, Possessions, ?, Location, Record, ConfRecord, ?
    """
    tables = soup.find_all("table")
    if len(tables) < 2:
        return []

    table = tables[1]
    all_rows = table.find_all("tr")
    data_rows = all_rows[1:]  # Skip header row

    results = []
    for tr in data_rows:
        cells = tr.find_all(["td", "th"])
        if len(cells) < 8:
            continue

        date = cells[0].get_text(strip=True)
        if not date or date == "Date":
            continue

        # Team rank on that date
        team_rank = cells[1].get_text(strip=True)

        # Opponent rank and name
        opp_rank = cells[2].get_text(strip=True)
        opp_link = cells[3].find("a")
        opponent = opp_link.get_text(strip=True) if opp_link else cells[3].get_text(strip=True)

        # Result (e.g., "W, 71-66")
        result = cells[4].get_text(strip=True)

        # Possessions
        possessions = cells[5].get_text(strip=True) if len(cells) > 5 else ""

        # Location (Home, Away, Neutral)
        location = cells[7].get_text(strip=True) if len(cells) > 7 else ""

        # Record
        record = cells[8].get_text(strip=True) if len(cells) > 8 else ""

        # Conference record (may be empty for non-conference games)
        conf_record = cells[9].get_text(strip=True) if len(cells) > 9 else ""

        row = {
            "Date": date,
            "Team_Rank": team_rank,
            "Opp_Rank": opp_rank,
            "Opponent": opponent,
            "Result": result,
            "Possessions": possessions,
            "Location": location,
            "Record": record,
            "Conf_Record": conf_record,
        }
        results.append(row)

    return results


def parse_scouting_report(soup: BeautifulSoup, conference_only: bool = False) -> dict:
    """Parse scouting report from inline JavaScript on team page.

    The team page embeds stat data in a <script> tag that sets values
    via jQuery. Two branches exist: conference-only (checkbox checked)
    and full-season (else/tableStart branch).

    Returns dict mapping stat names to {value, rank} dicts.
    """
    scripts = soup.find_all("script")

    # Find the script containing scouting report data
    script_text = ""
    for s in scripts:
        text = s.string or ""
        if "td#OE" in text and "tableStart" in text:
            script_text = text
            break

    if not script_text:
        return {}

    # Choose the right branch: conference-only or full-season
    if conference_only:
        # Conference data is in the 'if (checked)' branch
        branch_start = script_text.find("if (checked)")
        # The branch ends at "else tableStart" or "else {"
        branch_end = script_text.find("else tableStart", branch_start)
        if branch_end < 0:
            branch_end = script_text.find("else {", branch_start)
        if branch_start < 0 or branch_end < 0:
            return {}
        branch = script_text[branch_start:branch_end]
    else:
        # Full-season data is in the 'tableStart()' function
        branch_start = script_text.find("function tableStart()")
        if branch_start < 0:
            return {}
        branch = script_text[branch_start:]

    # Extract all stat values: pattern is td#STAT_ID with value and rank
    # Example: $("td#OE").html("<a href=\"...\">125.7</a> <span class=\"seed\">10</span>");
    # Or:      $("td#OE").html("125.7 <span class=\"seed\">10</span>");
    stat_ids = [
        "OE",
        "DE",
        "Tempo",
        "APLO",
        "APLD",
        "eFG",
        "DeFG",
        "TOPct",
        "DTOPct",
        "ORPct",
        "DORPct",
        "FTR",
        "DFTR",
        "3Pct",
        "D3Pct",
        "2Pct",
        "D2Pct",
        "FTPct",
        "DFTPct",
        "BlockPct",
        "DBlockPct",
        "StlRate",
        "DStlRate",
        "NSTRate",
        "DNSTRate",
        "ShotDist",
        "DShotDist",
        "3PARate",
        "D3PARate",
        "ARate",
        "DARate",
        "PD3",
        "DPD3",
        "PD2",
        "DPD2",
        "PD1",
        "DPD1",
    ]

    # Human-readable names for the stat IDs
    stat_names = {
        "OE": "Adj_OE",
        "DE": "Adj_DE",
        "Tempo": "Adj_Tempo",
        "APLO": "Avg_Poss_Length_Off",
        "APLD": "Avg_Poss_Length_Def",
        "eFG": "eFG_Pct",
        "DeFG": "Def_eFG_Pct",
        "TOPct": "TO_Pct",
        "DTOPct": "Def_TO_Pct",
        "ORPct": "OR_Pct",
        "DORPct": "Def_OR_Pct",
        "FTR": "FT_Rate",
        "DFTR": "Def_FT_Rate",
        "3Pct": "3P_Pct",
        "D3Pct": "Def_3P_Pct",
        "2Pct": "2P_Pct",
        "D2Pct": "Def_2P_Pct",
        "FTPct": "FT_Pct",
        "DFTPct": "Def_FT_Pct",
        "BlockPct": "Blk_Pct",
        "DBlockPct": "Def_Blk_Pct",
        "StlRate": "Stl_Rate",
        "DStlRate": "Def_Stl_Rate",
        "NSTRate": "NST_Rate",
        "DNSTRate": "Def_NST_Rate",
        "ShotDist": "2P_Dist",
        "DShotDist": "Def_2P_Dist",
        "3PARate": "3PA_Rate",
        "D3PARate": "Def_3PA_Rate",
        "ARate": "Ast_Rate",
        "DARate": "Def_Ast_Rate",
        "PD3": "Pts_Dist_3P",
        "DPD3": "Def_Pts_Dist_3P",
        "PD2": "Pts_Dist_2P",
        "DPD2": "Def_Pts_Dist_2P",
        "PD1": "Pts_Dist_FT",
        "DPD1": "Def_Pts_Dist_FT",
    }

    report = {}
    for stat_id in stat_ids:
        # Find the .html() call for this stat.
        # Content contains escaped quotes (\"), so we can't use [^"]+.
        # Match from .html(" to the next ");
        pattern = rf'td#{re.escape(stat_id)}"\)\.html\("(.*?)"\);'
        match = re.search(pattern, branch)
        if not match:
            continue

        html_content = match.group(1)

        # Extract the numeric value (may be inside an <a> tag or plain text)
        # Escaped quotes in the JS: \" appears as \" in the string
        value_match = re.search(r">([0-9.]+)<", html_content)
        if not value_match:
            value_match = re.search(r"^([0-9.]+)", html_content)
        value = value_match.group(1) if value_match else ""

        # Extract rank from <span class=\"seed\"> (escaped quotes in JS)
        rank_match = re.search(r'seed\\">(\d+)<', html_content)
        if not rank_match:
            rank_match = re.search(r'seed">(\d+)<', html_content)
        rank = rank_match.group(1) if rank_match else ""

        name = stat_names.get(stat_id, stat_id)
        report[name] = {"value": value, "rank": rank}

    return report
