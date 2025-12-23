"""
HTTP Server for Cloud Run deployment.

Implements MCP Streamable HTTP transport for remote MCP clients.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.requests import Request

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

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY", "")

_scraper: KenPomScraper | None = None


def get_scraper() -> KenPomScraper:
    """Get or create the scraper singleton."""
    global _scraper
    if _scraper is None:
        email = os.getenv("KENPOM_EMAIL")
        password = os.getenv("KENPOM_PASSWORD")
        if not email or not password:
            raise ValueError("KENPOM_EMAIL and KENPOM_PASSWORD required")
        _scraper = KenPomScraper(email, password)
    return _scraper


# MCP Tool definitions
TOOLS = [
    {
        "name": "get_ratings",
        "description": "Get Pomeroy ratings for all teams",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year (e.g., '2024')"}
            },
        },
    },
    {
        "name": "get_efficiency",
        "description": "Get efficiency and tempo stats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year"}
            },
        },
    },
    {
        "name": "get_four_factors",
        "description": "Get Four Factors stats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year"}
            },
        },
    },
    {
        "name": "get_team_stats",
        "description": "Get miscellaneous team stats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "defense": {"type": "boolean", "description": "If true, get defensive stats"},
                "season": {"type": "string", "description": "Season year"},
            },
        },
    },
    {
        "name": "get_player_stats",
        "description": "Get player leaders by metric",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "Metric to rank by (eFG, ORtg, etc.)"},
                "season": {"type": "string", "description": "Season year"},
                "conference": {"type": "string", "description": "Conference filter"},
            },
        },
    },
    {
        "name": "get_height",
        "description": "Get height/experience data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year"}
            },
        },
    },
    {
        "name": "get_fanmatch",
        "description": "Get game predictions for a date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
            },
        },
    },
    {
        "name": "get_arenas",
        "description": "Get arena information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year"}
            },
        },
    },
    {
        "name": "get_game_attrs",
        "description": "Get top games by attribute",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "Attribute (Excitement, Tension, etc.)"},
                "season": {"type": "string", "description": "Season year"},
            },
        },
    },
    {
        "name": "get_program_ratings",
        "description": "Get historical program ratings",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_kpoy",
        "description": "Get KPOY standings",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year"}
            },
        },
    },
    {
        "name": "get_point_distribution",
        "description": "Get point distribution",
        "inputSchema": {
            "type": "object",
            "properties": {
                "season": {"type": "string", "description": "Season year"}
            },
        },
    },
    {
        "name": "get_hca",
        "description": "Get home court advantage data",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


async def call_tool(name: str, arguments: dict) -> Any:
    """Execute a tool and return its result."""
    scraper = get_scraper()

    if name == "get_ratings":
        soup = await scraper.get_ratings_page(arguments.get("season"))
        return parse_pomeroy_ratings(soup)
    elif name == "get_efficiency":
        soup = await scraper.get_efficiency_page(arguments.get("season"))
        return parse_efficiency(soup)
    elif name == "get_four_factors":
        soup = await scraper.get_four_factors_page(arguments.get("season"))
        return parse_four_factors(soup)
    elif name == "get_team_stats":
        soup = await scraper.get_team_stats_page(
            defense=arguments.get("defense", False),
            season=arguments.get("season")
        )
        return parse_team_stats(soup, defense=arguments.get("defense", False))
    elif name == "get_player_stats":
        soup = await scraper.get_player_stats_page(
            metric=arguments.get("metric", "eFG"),
            season=arguments.get("season"),
            conf=arguments.get("conference")
        )
        return parse_player_stats(soup)
    elif name == "get_height":
        soup = await scraper.get_height_page(arguments.get("season"))
        return parse_height(soup)
    elif name == "get_fanmatch":
        soup = await scraper.get_fanmatch_page(arguments.get("date"))
        return parse_fanmatch(soup)
    elif name == "get_arenas":
        soup = await scraper.get_arenas_page(arguments.get("season"))
        return parse_arenas(soup)
    elif name == "get_game_attrs":
        soup = await scraper.get_game_attrs_page(
            metric=arguments.get("metric", "Excitement"),
            season=arguments.get("season")
        )
        return parse_game_attrs(soup)
    elif name == "get_program_ratings":
        soup = await scraper.get_program_ratings_page()
        return parse_program_ratings(soup)
    elif name == "get_kpoy":
        soup = await scraper.get_kpoy_page(arguments.get("season"))
        return parse_kpoy(soup)
    elif name == "get_point_distribution":
        soup = await scraper.get_point_dist_page(arguments.get("season"))
        return parse_point_distribution(soup)
    elif name == "get_hca":
        soup = await scraper.get_hca_page()
        return parse_hca(soup)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def health(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "service": "kenpom-mcp"})


async def tools_list(request: Request) -> JSONResponse:
    """List available tools (simple REST endpoint)."""
    return JSONResponse([{"name": t["name"], "description": t["description"]} for t in TOOLS])


async def mcp_handler(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC 2.0 requests (Streamable HTTP transport)."""
    try:
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id")

        logger.info(f"MCP request: {method}")

        # Handle MCP protocol methods
        if method == "initialize":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": {
                        "name": "kenpom-mcp",
                        "version": "0.2.0",
                    },
                },
            })

        elif method == "notifications/initialized":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {},
            })

        elif method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": TOOLS},
            })

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            try:
                result = await call_tool(tool_name, arguments)
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": str(result)}
                        ],
                    },
                })
            except Exception as e:
                logger.exception(f"Tool error: {tool_name}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": str(e)},
                })

        # Legacy direct tool call (for backwards compatibility)
        elif method.startswith("get_"):
            result = await call_tool(method, params)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"data": result},
            })

        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })

    except Exception as e:
        logger.exception("MCP handler error")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": str(e)},
        }, status_code=500)


# Auth and CORS middleware
async def auth_middleware(request: Request, call_next):
    # CORS preflight
    if request.method == "OPTIONS":
        return Response(
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, X-API-Key, Authorization",
            }
        )

    # Health check - no auth
    if request.url.path in ["/", "/health"]:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    # API key check
    if API_KEY:
        provided_key = request.headers.get("X-API-Key", "")
        # Also check query param for SSE clients
        if not provided_key:
            provided_key = request.query_params.get("api_key", "")
        if provided_key != API_KEY:
            return JSONResponse(
                {"error": "Unauthorized. Provide valid X-API-Key header or api_key query param."},
                status_code=401
            )

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


routes = [
    Route("/", health),
    Route("/health", health),
    Route("/tools", tools_list),
    Route("/mcp", mcp_handler, methods=["POST"]),
]

app = Starlette(routes=routes)
app.middleware("http")(auth_middleware)
