"""Unified tool registry for KenPom MCP server.

This module defines all KenPom tools in one place, shared by both
STDIO (FastMCP) and HTTP (Starlette) transports.
"""

from collections.abc import Callable
from typing import Any

from .parsers import (
    parse_arenas,
    parse_conference_defense,
    parse_conference_offense,
    parse_conference_standings,
    parse_efficiency,
    parse_fanmatch,
    parse_four_factors,
    parse_game_attrs,
    parse_hca,
    parse_height,
    parse_kpoy,
    parse_player_stats,
    parse_point_distribution,
    parse_pomeroy_ratings,
    parse_program_ratings,
    parse_schedule,
    parse_scouting_report,
    parse_team_stats,
)
from .scraper import KenPomScraper


class ToolDefinition:
    """Definition of a KenPom MCP tool."""

    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        input_schema: dict[str, Any],
        docstring: str | None = None,
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema
        self.docstring = docstring

    def to_mcp_schema(self) -> dict[str, Any]:
        """Convert to MCP tool schema for HTTP transport."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


# Tool handlers - each takes (scraper, arguments) and returns parsed data


async def handle_get_ratings(scraper: KenPomScraper, args: dict) -> list:
    """Get Pomeroy ratings."""
    soup = await scraper.get_ratings_page(args.get("season"))
    return parse_pomeroy_ratings(soup)


async def handle_get_efficiency(scraper: KenPomScraper, args: dict) -> list:
    """Get efficiency stats."""
    soup = await scraper.get_efficiency_page(args.get("season"))
    return parse_efficiency(soup)


async def handle_get_four_factors(scraper: KenPomScraper, args: dict) -> list:
    """Get four factors stats."""
    soup = await scraper.get_four_factors_page(args.get("season"))
    return parse_four_factors(soup)


async def handle_get_team_stats(scraper: KenPomScraper, args: dict) -> list:
    """Get team stats."""
    soup = await scraper.get_team_stats_page(
        defense=args.get("defense", False), season=args.get("season")
    )
    return parse_team_stats(soup, defense=args.get("defense", False))


async def handle_get_player_stats(scraper: KenPomScraper, args: dict) -> list:
    """Get player stats."""
    soup = await scraper.get_player_stats_page(
        metric=args.get("metric", "eFG"),
        season=args.get("season"),
        conf=args.get("conference"),
    )
    return parse_player_stats(soup)


async def handle_get_height(scraper: KenPomScraper, args: dict) -> list:
    """Get height/experience data."""
    soup = await scraper.get_height_page(args.get("season"))
    return parse_height(soup)


async def handle_get_fanmatch(scraper: KenPomScraper, args: dict) -> dict:
    """Get FanMatch predictions."""
    soup = await scraper.get_fanmatch_page(args.get("date"))
    return parse_fanmatch(soup)


async def handle_get_arenas(scraper: KenPomScraper, args: dict) -> list:
    """Get arena information."""
    soup = await scraper.get_arenas_page(args.get("season"))
    return parse_arenas(soup)


async def handle_get_game_attrs(scraper: KenPomScraper, args: dict) -> list:
    """Get top games by attribute."""
    soup = await scraper.get_game_attrs_page(
        metric=args.get("metric", "Excitement"), season=args.get("season")
    )
    return parse_game_attrs(soup)


async def handle_get_program_ratings(scraper: KenPomScraper, args: dict) -> list:
    """Get historical program ratings."""
    soup = await scraper.get_program_ratings_page()
    return parse_program_ratings(soup)


async def handle_get_kpoy(scraper: KenPomScraper, args: dict) -> list:
    """Get KPOY standings."""
    soup = await scraper.get_kpoy_page(args.get("season"))
    return parse_kpoy(soup)


async def handle_get_point_distribution(scraper: KenPomScraper, args: dict) -> list:
    """Get point distribution."""
    soup = await scraper.get_point_dist_page(args.get("season"))
    return parse_point_distribution(soup)


async def handle_get_hca(scraper: KenPomScraper, args: dict) -> list:
    """Get home court advantage data."""
    soup = await scraper.get_hca_page()
    return parse_hca(soup)


async def handle_get_schedule(scraper: KenPomScraper, args: dict) -> list:
    """Get team schedule."""
    team = args.get("team")
    if not team:
        raise ValueError("team parameter is required")
    soup = await scraper.get_team_page(team, args.get("season"))
    return parse_schedule(soup)


async def handle_get_scouting_report(scraper: KenPomScraper, args: dict) -> dict:
    """Get team scouting report."""
    team = args.get("team")
    if not team:
        raise ValueError("team parameter is required")
    soup = await scraper.get_team_page(team, args.get("season"))
    return parse_scouting_report(soup, conference_only=args.get("conference_only", False))


async def handle_get_conference_standings(scraper: KenPomScraper, args: dict) -> list:
    """Get conference standings."""
    conf = args.get("conference")
    if not conf:
        raise ValueError("conference parameter is required")
    soup = await scraper.get_conference_page(conf, args.get("season"))
    return parse_conference_standings(soup)


async def handle_get_conference_offense(scraper: KenPomScraper, args: dict) -> list:
    """Get conference offensive stats."""
    conf = args.get("conference")
    if not conf:
        raise ValueError("conference parameter is required")
    soup = await scraper.get_conference_page(conf, args.get("season"))
    return parse_conference_offense(soup)


async def handle_get_conference_defense(scraper: KenPomScraper, args: dict) -> list:
    """Get conference defensive stats."""
    conf = args.get("conference")
    if not conf:
        raise ValueError("conference parameter is required")
    soup = await scraper.get_conference_page(conf, args.get("season"))
    return parse_conference_defense(soup)


# Tool Registry - Single source of truth for all tools

TOOL_REGISTRY = {
    "get_ratings": ToolDefinition(
        name="get_ratings",
        description="Get Pomeroy College Basketball Ratings for all teams",
        handler=handle_get_ratings,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season. Earliest: 1999.",
                }
            },
        },
        docstring="""
Get Pomeroy College Basketball Ratings for all teams.

Returns team rankings with adjusted efficiency metrics including:
rank, team name, conference, record, adjusted offensive/defensive efficiency,
adjusted tempo, and more.

Args:
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 1999.

Returns:
    JSON array of team ratings data.
""",
    ),
    "get_efficiency": ToolDefinition(
        name="get_efficiency",
        description="Get efficiency and tempo stats for all teams",
        handler=handle_get_efficiency,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                }
            },
        },
        docstring="""
Get efficiency and tempo stats for all teams.

Returns the summary efficiency table with offensive/defensive efficiency,
tempo, and possession length data.

Args:
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 1999. Possession length data from 2010.

Returns:
    JSON array of efficiency data for all teams.
""",
    ),
    "get_four_factors": ToolDefinition(
        name="get_four_factors",
        description="Get Four Factors stats for all teams",
        handler=handle_get_four_factors,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                }
            },
        },
        docstring="""
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
""",
    ),
    "get_team_stats": ToolDefinition(
        name="get_team_stats",
        description="Get miscellaneous team statistics",
        handler=handle_get_team_stats,
        input_schema={
            "type": "object",
            "properties": {
                "defense": {
                    "type": "boolean",
                    "description": "If true, returns defensive stats. If false, returns offensive stats.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
            },
        },
        docstring="""
Get miscellaneous team statistics.

Returns detailed team stats including shooting percentages, blocks,
steals, assists, and more.

Args:
    defense: If True, returns defensive stats. If False, returns offensive stats.
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 1999.

Returns:
    JSON array of team stats (offense or defense based on parameter).
""",
    ),
    "get_player_stats": ToolDefinition(
        name="get_player_stats",
        description="Get player leaders by statistical metric",
        handler=handle_get_player_stats,
        input_schema={
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Stat to rank by (eFG, ORtg, Min, Poss, etc.). Default: eFG.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
                "conference": {
                    "type": "string",
                    "description": "Conference filter (e.g., 'ACC', 'B10', 'SEC').",
                },
            },
        },
        docstring="""
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
""",
    ),
    "get_height": ToolDefinition(
        name="get_height",
        description="Get height and experience data for all teams",
        handler=handle_get_height,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                }
            },
        },
        docstring="""
Get height and experience data for all teams.

Returns team rosters data including average height, experience,
bench minutes, and continuity metrics.

Args:
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 2007. Continuity data from 2008.

Returns:
    JSON array of height/experience data for all teams.
""",
    ),
    "get_fanmatch": ToolDefinition(
        name="get_fanmatch",
        description="Get FanMatch game predictions for a specific date",
        handler=handle_get_fanmatch,
        input_schema={
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (e.g., '2024-12-23'). Defaults to today.",
                }
            },
        },
        docstring="""
Get FanMatch game predictions for a specific date.

FanMatch provides predicted scores, spreads, and game information
for all games on a given date.

Args:
    date: Date in "YYYY-MM-DD" format (e.g., "2024-12-23").
          Defaults to today's date.

Returns:
    JSON object with games, predictions, and daily statistics.
""",
    ),
    "get_arenas": ToolDefinition(
        name="get_arenas",
        description="Get arena information for all teams",
        handler=handle_get_arenas,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                }
            },
        },
        docstring="""
Get arena information for all teams.

Returns arena names, capacities, and attendance data.

Args:
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 2010.

Returns:
    JSON array of arena data.
""",
    ),
    "get_game_attrs": ToolDefinition(
        name="get_game_attrs",
        description="Get top games ranked by game attributes",
        handler=handle_get_game_attrs,
        input_schema={
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Attribute to rank by (Excitement, Tension, Dominance, etc.). Default: Excitement.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
            },
        },
        docstring="""
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
""",
    ),
    "get_program_ratings": ToolDefinition(
        name="get_program_ratings",
        description="Get historical program ratings",
        handler=handle_get_program_ratings,
        input_schema={"type": "object", "properties": {}},
        docstring="""
Get historical program ratings.

Returns the all-time program rankings based on historical performance
across all available seasons.

Returns:
    JSON array of program ratings.
""",
    ),
    "get_kpoy": ToolDefinition(
        name="get_kpoy",
        description="Get KenPom Player of the Year standings",
        handler=handle_get_kpoy,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                }
            },
        },
        docstring="""
Get KenPom Player of the Year standings.

Returns the current KPOY leaderboard and Game MVP leaders.

Args:
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 2011. Game MVP table from 2013.

Returns:
    JSON array with KPOY standings (may include multiple tables).
""",
    ),
    "get_point_distribution": ToolDefinition(
        name="get_point_distribution",
        description="Get team point distribution breakdown",
        handler=handle_get_point_distribution,
        input_schema={
            "type": "object",
            "properties": {
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                }
            },
        },
        docstring="""
Get team point distribution breakdown.

Shows how teams score their points (2-pointers, 3-pointers, free throws)
and where their points allowed come from.

Args:
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 1999.

Returns:
    JSON array of point distribution data for all teams.
""",
    ),
    "get_hca": ToolDefinition(
        name="get_hca",
        description="Get home court advantage data",
        handler=handle_get_hca,
        input_schema={"type": "object", "properties": {}},
        docstring="""
Get home court advantage data.

Returns historical home court advantage statistics for all teams.

Returns:
    JSON array of home court advantage data.
""",
    ),
    "get_schedule": ToolDefinition(
        name="get_schedule",
        description="Get a team's game schedule and results",
        handler=handle_get_schedule,
        input_schema={
            "type": "object",
            "properties": {
                "team": {
                    "type": "string",
                    "description": "Team name (e.g., 'BYU', 'Duke', 'North Carolina'). Required.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
            },
            "required": ["team"],
        },
        docstring="""
Get a team's game schedule and results.

Returns the full schedule with game dates, opponents, results,
rankings, locations, and records.

Args:
    team: Team name (required). Examples: 'BYU', 'Duke', 'North Carolina'.
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 1999.

Returns:
    JSON array of scheduled/completed games.
""",
    ),
    "get_scouting_report": ToolDefinition(
        name="get_scouting_report",
        description="Get detailed scouting report for a team (37 stats with ranks)",
        handler=handle_get_scouting_report,
        input_schema={
            "type": "object",
            "properties": {
                "team": {
                    "type": "string",
                    "description": "Team name (e.g., 'BYU', 'Duke'). Required.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
                "conference_only": {
                    "type": "boolean",
                    "description": "If true, returns conference-only stats. Default: false (full season).",
                },
            },
            "required": ["team"],
        },
        docstring="""
Get detailed scouting report for a team.

Returns 37 stats with national ranks covering efficiency, tempo,
Four Factors, shooting percentages, and point distribution.
Both offensive and defensive sides.

Args:
    team: Team name (required). Examples: 'BYU', 'Duke', 'North Carolina'.
    season: Optional season year (e.g., "2024"). Defaults to current season.
    conference_only: If True, returns conference-only stats. Default: False.

Returns:
    JSON object mapping stat names to {value, rank} objects.
""",
    ),
    "get_conference_standings": ToolDefinition(
        name="get_conference_standings",
        description="Get conference standings with team records and ratings",
        handler=handle_get_conference_standings,
        input_schema={
            "type": "object",
            "properties": {
                "conference": {
                    "type": "string",
                    "description": "Conference code (e.g., 'B12', 'SEC', 'B10', 'ACC'). Required.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
            },
            "required": ["conference"],
        },
        docstring="""
Get conference standings with team records and ratings.

Returns standings with overall/conference records, projected records,
net rating, offensive/defensive ratings, tempo, and conference SOS.

Args:
    conference: Conference code (required). Examples: 'B12', 'SEC', 'B10', 'ACC', 'BE'.
    season: Optional season year (e.g., "2024"). Defaults to current season.
            Earliest available: 1999.

Returns:
    JSON array of conference standings.
""",
    ),
    "get_conference_offense": ToolDefinition(
        name="get_conference_offense",
        description="Get conference offensive stats for all teams",
        handler=handle_get_conference_offense,
        input_schema={
            "type": "object",
            "properties": {
                "conference": {
                    "type": "string",
                    "description": "Conference code (e.g., 'B12', 'SEC', 'B10', 'ACC'). Required.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
            },
            "required": ["conference"],
        },
        docstring="""
Get conference offensive stats for all teams in a conference.

Returns offensive efficiency, eFG%, TO%, OR%, FTR, 2P%, 3P%, FT%, and tempo
for each team in the conference.

Args:
    conference: Conference code (required). Examples: 'B12', 'SEC', 'B10', 'ACC'.
    season: Optional season year (e.g., "2024"). Defaults to current season.

Returns:
    JSON array of conference offensive stats.
""",
    ),
    "get_conference_defense": ToolDefinition(
        name="get_conference_defense",
        description="Get conference defensive stats for all teams",
        handler=handle_get_conference_defense,
        input_schema={
            "type": "object",
            "properties": {
                "conference": {
                    "type": "string",
                    "description": "Conference code (e.g., 'B12', 'SEC', 'B10', 'ACC'). Required.",
                },
                "season": {
                    "type": "string",
                    "description": "Season year (e.g., '2024'). Defaults to current season.",
                },
            },
            "required": ["conference"],
        },
        docstring="""
Get conference defensive stats for all teams in a conference.

Returns defensive efficiency, eFG%, TO%, OR%, FTR, 2P%, 3P%, Blk%, and Stl%
for each team in the conference.

Args:
    conference: Conference code (required). Examples: 'B12', 'SEC', 'B10', 'ACC'.
    season: Optional season year (e.g., "2024"). Defaults to current season.

Returns:
    JSON array of conference defensive stats.
""",
    ),
}


def get_all_tools() -> list[ToolDefinition]:
    """Get all tool definitions."""
    return list(TOOL_REGISTRY.values())


def get_tool(name: str) -> ToolDefinition | None:
    """Get a specific tool definition by name."""
    return TOOL_REGISTRY.get(name)


async def call_tool(scraper: KenPomScraper, name: str, arguments: dict) -> Any:
    """Execute a tool by name with the given arguments."""
    tool = get_tool(name)
    if not tool:
        raise ValueError(f"Unknown tool: {name}")
    return await tool.handler(scraper, arguments)
