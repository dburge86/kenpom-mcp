"""
KenPom MCP Server

Async MCP server with dual transport support:
- STDIO for local use
- SSE/HTTP for Google Cloud Run deployment
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load credentials from .env (find it relative to this package, not CWD)
_package_dir = Path(__file__).parent.parent.parent
load_dotenv(_package_dir / ".env")

from .scraper import KenPomScraper
from .parsers import (
    parse_pomeroy_ratings,
    parse_efficiency,
    parse_four_factors,
    parse_team_stats,
    parse_player_stats,
    parse_height,
    parse_kpoy,
    parse_fanmatch,
    parse_arenas,
    parse_hca,
    parse_game_attrs,
    parse_program_ratings,
    parse_point_distribution,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP("kenpom")

_scraper: KenPomScraper | None = None


def get_scraper(cache: Any = None) -> KenPomScraper:
    """Get or create the scraper singleton."""
    global _scraper
    if _scraper is None:
        email = os.getenv("KENPOM_EMAIL")
        password = os.getenv("KENPOM_PASSWORD")
        if not email or not password:
            raise ValueError(
                "KENPOM_EMAIL and KENPOM_PASSWORD environment variables required"
            )
        _scraper = KenPomScraper(email, password, cache=cache)
    return _scraper


def to_json(data: Any) -> str:
    """Convert data to JSON string."""
    return json.dumps(data, indent=2, default=str)


# =============================================================================
# MCP Tools
# =============================================================================


@mcp.tool()
async def get_ratings(season: str | None = None) -> str:
    """
    Get Pomeroy College Basketball Ratings for all teams.

    Returns team rankings with adjusted efficiency metrics including:
    rank, team name, conference, record, adjusted offensive/defensive efficiency,
    adjusted tempo, and more.

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 1999.

    Returns:
        JSON array of team ratings data.
    """
    scraper = get_scraper()
    soup = await scraper.get_ratings_page(season)
    data = parse_pomeroy_ratings(soup)
    return to_json(data)


@mcp.tool()
async def get_efficiency(season: str | None = None) -> str:
    """
    Get efficiency and tempo stats for all teams.

    Returns the summary efficiency table with offensive/defensive efficiency,
    tempo, and possession length data.

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 1999. Possession length data from 2010.

    Returns:
        JSON array of efficiency data for all teams.
    """
    scraper = get_scraper()
    soup = await scraper.get_efficiency_page(season)
    data = parse_efficiency(soup)
    return to_json(data)


@mcp.tool()
async def get_four_factors(season: str | None = None) -> str:
    """
    Get Four Factors stats for all teams.

    The Four Factors are the key stats that determine team efficiency:
    - eFG% (Effective Field Goal Percentage)
    - TO% (Turnover Percentage)
    - OR% (Offensive Rebound Percentage)
    - FTRate (Free Throw Rate)

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 1999.

    Returns:
        JSON array of Four Factors data for all teams.
    """
    scraper = get_scraper()
    soup = await scraper.get_four_factors_page(season)
    data = parse_four_factors(soup)
    return to_json(data)


@mcp.tool()
async def get_team_stats(defense: bool = False, season: str | None = None) -> str:
    """
    Get miscellaneous team statistics.

    Returns detailed team stats including shooting percentages, blocks,
    steals, assists, and more.

    Args:
        defense: If True, returns defensive stats. If False, returns offensive stats.
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 1999.

    Returns:
        JSON array of team stats (offense or defense based on parameter).
    """
    scraper = get_scraper()
    soup = await scraper.get_team_stats_page(defense=defense, season=season)
    data = parse_team_stats(soup, defense=defense)
    return to_json(data)


@mcp.tool()
async def get_player_stats(
    metric: str = "eFG",
    season: str | None = None,
    conference: str | None = None
) -> str:
    """
    Get player leaders by statistical metric.

    Args:
        metric: Stat to rank players by. Options:
                'ORtg', 'Min', 'eFG', 'Poss', 'Shots', 'OR', 'DR', 'TO',
                'ARate', 'Blk', 'FTRate', 'Stl', 'TS', 'FC40', 'FD40',
                '2P', '3P', 'FT'. Default: 'eFG'.
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 2004.
        conference: Optional conference filter (e.g., 'ACC', 'B10', 'SEC').

    Returns:
        JSON array of player stats ranked by the specified metric.
    """
    scraper = get_scraper()
    soup = await scraper.get_player_stats_page(metric=metric, season=season, conf=conference)
    data = parse_player_stats(soup)
    return to_json(data)


@mcp.tool()
async def get_height(season: str | None = None) -> str:
    """
    Get height and experience data for all teams.

    Returns team rosters data including average height, experience,
    bench minutes, and continuity metrics.

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 2007. Continuity data from 2008.

    Returns:
        JSON array of height/experience data for all teams.
    """
    scraper = get_scraper()
    soup = await scraper.get_height_page(season)
    data = parse_height(soup)
    return to_json(data)


@mcp.tool()
async def get_fanmatch(date: str | None = None) -> str:
    """
    Get FanMatch game predictions for a specific date.

    FanMatch provides predicted scores, spreads, and game information
    for all games on a given date.

    Args:
        date: Date in "YYYY-MM-DD" format (e.g., "2024-12-23").
              Defaults to today's date.

    Returns:
        JSON object with games, predictions, and daily statistics.
    """
    scraper = get_scraper()
    soup = await scraper.get_fanmatch_page(date)
    data = parse_fanmatch(soup)
    return to_json(data)


@mcp.tool()
async def get_arenas(season: str | None = None) -> str:
    """
    Get arena information for all teams.

    Returns arena names, capacities, and attendance data.

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 2010.

    Returns:
        JSON array of arena data.
    """
    scraper = get_scraper()
    soup = await scraper.get_arenas_page(season)
    data = parse_arenas(soup)
    return to_json(data)


@mcp.tool()
async def get_game_attrs(metric: str = "Excitement", season: str | None = None) -> str:
    """
    Get top games ranked by game attributes.

    Args:
        metric: Attribute to rank games by. Options:
                'Excitement', 'Tension', 'Dominance', 'ComeBack',
                'FanMatch', 'Upsets', 'Busts'. Default: 'Excitement'.
                ('FanMatch', 'Upsets', 'Busts' only available after 2010)
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 2010.

    Returns:
        JSON array of top games for the specified attribute.
    """
    scraper = get_scraper()
    soup = await scraper.get_game_attrs_page(metric=metric, season=season)
    data = parse_game_attrs(soup)
    return to_json(data)


@mcp.tool()
async def get_program_ratings() -> str:
    """
    Get historical program ratings.

    Returns the all-time program rankings based on historical performance
    across all available seasons.

    Returns:
        JSON array of program ratings.
    """
    scraper = get_scraper()
    soup = await scraper.get_program_ratings_page()
    data = parse_program_ratings(soup)
    return to_json(data)


@mcp.tool()
async def get_kpoy(season: str | None = None) -> str:
    """
    Get KenPom Player of the Year standings.

    Returns the current KPOY leaderboard and Game MVP leaders.

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 2011. Game MVP table from 2013.

    Returns:
        JSON array with KPOY standings (may include multiple tables).
    """
    scraper = get_scraper()
    soup = await scraper.get_kpoy_page(season)
    data = parse_kpoy(soup)
    return to_json(data)


@mcp.tool()
async def get_point_distribution(season: str | None = None) -> str:
    """
    Get team point distribution breakdown.

    Shows how teams score their points (2-pointers, 3-pointers, free throws)
    and where their points allowed come from.

    Args:
        season: Optional season year (e.g., "2024"). Defaults to current season.
                Earliest available: 1999.

    Returns:
        JSON array of point distribution data for all teams.
    """
    scraper = get_scraper()
    soup = await scraper.get_point_dist_page(season)
    data = parse_point_distribution(soup)
    return to_json(data)


@mcp.tool()
async def get_hca() -> str:
    """
    Get home court advantage data.

    Returns historical home court advantage statistics for all teams.

    Returns:
        JSON array of home court advantage data.
    """
    scraper = get_scraper()
    soup = await scraper.get_hca_page()
    data = parse_hca(soup)
    return to_json(data)


def main():
    """Run the MCP server locally via STDIO."""
    logger.info("Starting KenPom MCP server (local mode)...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
