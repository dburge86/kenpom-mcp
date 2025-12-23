"""
KenPom client wrapper for MCP server.
Handles authentication and data fetching using kenpompy.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class KenPomClient:
    """Client for interacting with KenPom via kenpompy web scraping."""

    def __init__(self):
        load_dotenv()
        self._browser = None
        self._email = os.getenv("KENPOM_EMAIL")
        self._password = os.getenv("KENPOM_PASSWORD")

        if not self._email or not self._password:
            raise ValueError(
                "KENPOM_EMAIL and KENPOM_PASSWORD environment variables are required. "
                "Copy .env.example to .env and fill in your credentials."
            )

    def _ensure_logged_in(self):
        """Ensure we have an authenticated browser session."""
        if self._browser is None:
            from kenpompy.utils import login
            logger.info("Logging in to KenPom...")
            self._browser = login(self._email, self._password)
            logger.info("Successfully logged in to KenPom")
        return self._browser

    def _df_to_json(self, df: pd.DataFrame) -> str:
        """Convert a pandas DataFrame to JSON string for MCP response."""
        if df is None or df.empty:
            return json.dumps({"error": "No data available"})
        return df.to_json(orient="records", indent=2)

    def _format_result(self, data: Any) -> str:
        """Format any data type for MCP response."""
        if isinstance(data, pd.DataFrame):
            return self._df_to_json(data)
        elif isinstance(data, list):
            if all(isinstance(item, pd.DataFrame) for item in data):
                return json.dumps([json.loads(self._df_to_json(df)) for df in data], indent=2)
            return json.dumps(data, indent=2)
        elif isinstance(data, dict):
            return json.dumps(data, indent=2)
        return str(data)

    def get_ratings(self, season: str | None = None) -> str:
        """Get Pomeroy ratings for all teams."""
        from kenpompy.misc import get_pomeroy_ratings

        browser = self._ensure_logged_in()
        if season:
            df = get_pomeroy_ratings(browser, season=season)
        else:
            df = get_pomeroy_ratings(browser)
        return self._df_to_json(df)

    def get_efficiency(self, season: str | None = None) -> str:
        """Get efficiency and tempo stats."""
        from kenpompy.summary import get_efficiency

        browser = self._ensure_logged_in()
        if season:
            df = get_efficiency(browser, season=season)
        else:
            df = get_efficiency(browser)
        return self._df_to_json(df)

    def get_four_factors(self, season: str | None = None) -> str:
        """Get Four Factors stats (eFG%, TO%, OR%, FTRate)."""
        from kenpompy.summary import get_fourfactors

        browser = self._ensure_logged_in()
        if season:
            df = get_fourfactors(browser, season=season)
        else:
            df = get_fourfactors(browser)
        return self._df_to_json(df)

    def get_team_stats(self, defense: bool = False, season: str | None = None) -> str:
        """Get miscellaneous team stats."""
        from kenpompy.summary import get_teamstats

        browser = self._ensure_logged_in()
        if season:
            df = get_teamstats(browser, defense=defense, season=season)
        else:
            df = get_teamstats(browser, defense=defense)
        return self._df_to_json(df)

    def get_player_stats(
        self,
        metric: str = "eFG",
        season: str | None = None,
        conf: str | None = None
    ) -> str:
        """Get player leaders by metric."""
        from kenpompy.summary import get_playerstats

        browser = self._ensure_logged_in()
        kwargs = {"metric": metric}
        if season:
            kwargs["season"] = season
        if conf:
            kwargs["conf"] = conf

        result = get_playerstats(browser, **kwargs)
        return self._format_result(result)

    def get_height(self, season: str | None = None) -> str:
        """Get height/experience data for teams."""
        from kenpompy.summary import get_height

        browser = self._ensure_logged_in()
        if season:
            df = get_height(browser, season=season)
        else:
            df = get_height(browser)
        return self._df_to_json(df)

    def get_fanmatch(self, date: str | None = None) -> str:
        """Get game predictions for a specific date."""
        from kenpompy.FanMatch import FanMatch

        browser = self._ensure_logged_in()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        fm = FanMatch(browser, date)

        result = {
            "date": fm.date,
            "ppg": fm.ppg,
            "avg_eff": fm.avg_eff,
            "pos_40": fm.pos_40,
            "games": json.loads(self._df_to_json(fm.fm_df)) if fm.fm_df is not None else [],
            "lines_of_night": fm.lines_o_night,
            "record_favs": fm.record_favs,
            "expected_record_favs": fm.expected_record_favs,
        }
        return json.dumps(result, indent=2)

    def get_arenas(self, season: str | None = None) -> str:
        """Get arena information."""
        from kenpompy.misc import get_arenas

        browser = self._ensure_logged_in()
        if season:
            df = get_arenas(browser, season=season)
        else:
            df = get_arenas(browser)
        return self._df_to_json(df)

    def get_game_attrs(self, metric: str = "Excitement", season: str | None = None) -> str:
        """Get game attributes (excitement, upsets, etc.)."""
        from kenpompy.misc import get_gameattribs

        browser = self._ensure_logged_in()
        kwargs = {"metric": metric}
        if season:
            kwargs["season"] = season

        df = get_gameattribs(browser, **kwargs)
        return self._df_to_json(df)

    def get_program_ratings(self) -> str:
        """Get historical program ratings."""
        from kenpompy.misc import get_program_ratings

        browser = self._ensure_logged_in()
        df = get_program_ratings(browser)
        return self._df_to_json(df)

    def get_kpoy(self, season: str | None = None) -> str:
        """Get Kenpom Player of the Year standings."""
        from kenpompy.summary import get_kpoy

        browser = self._ensure_logged_in()
        if season:
            dfs = get_kpoy(browser, season=season)
        else:
            dfs = get_kpoy(browser)
        return self._format_result(dfs)

    def get_point_distribution(self, season: str | None = None) -> str:
        """Get team point distribution breakdown."""
        from kenpompy.summary import get_pointdist

        browser = self._ensure_logged_in()
        if season:
            df = get_pointdist(browser, season=season)
        else:
            df = get_pointdist(browser)
        return self._df_to_json(df)

    def get_hca(self) -> str:
        """Get home court advantage data."""
        from kenpompy.misc import get_hca

        browser = self._ensure_logged_in()
        df = get_hca(browser)
        return self._df_to_json(df)
