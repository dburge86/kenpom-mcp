"""Parser for FanMatch page."""

import re
from io import StringIO

from bs4 import BeautifulSoup

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def parse_fanmatch(soup: BeautifulSoup) -> dict:
    """Parse FanMatch page into structured data."""
    result = {
        "date": None,
        "ppg": None,
        "avg_eff": None,
        "pos_40": None,
        "games": [],
        "statistics": {},
    }

    # Parse page title for date
    title = soup.find("h2")
    if title:
        title_text = title.get_text(strip=True)
        # Extract date from title like "Saturday, December 21st"
        result["date"] = title_text

    # Parse daily stats from content
    content = soup.find(id="content") or soup.find("div", class_="content")
    if content:
        text = content.get_text()

        # Extract stats using regex
        ppg_match = re.search(r"(\d+\.?\d*)\s*ppg", text, re.IGNORECASE)
        if ppg_match:
            result["ppg"] = float(ppg_match.group(1))

        eff_match = re.search(r"efficiency.*?(\d+\.?\d*)", text, re.IGNORECASE)
        if eff_match:
            result["avg_eff"] = float(eff_match.group(1))

    # Parse games table
    table = soup.find("table")
    if table:
        result["games"] = _parse_games_table(table)

    return result


def _parse_games_table(table) -> list[dict]:
    """Parse the FanMatch games table."""
    games = []

    if HAS_PANDAS:
        try:
            df = pd.read_html(StringIO(str(table)))[0]

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join(col).strip() for col in df.columns.values]

            # Basic column mapping
            columns = ["Time", "Game", "Location", "TheLine", "Prediction", "PredMOV", "PredTotal"]
            df.columns = columns[: len(df.columns)]

            # Parse game info from the Game column
            for _, row in df.iterrows():
                game = row.to_dict()
                if game.get("Game") and str(game.get("Game")) != "Game":
                    games.append(game)

            return games
        except Exception:
            pass

    # Fallback: pure Python parsing
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["td", "th"])
        if len(cells) >= 3:
            game = {
                "Time": cells[0].get_text(strip=True) if len(cells) > 0 else "",
                "Game": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                "Location": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                "TheLine": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                "Prediction": cells[4].get_text(strip=True) if len(cells) > 4 else "",
            }
            if game["Game"]:
                games.append(game)

    return games
