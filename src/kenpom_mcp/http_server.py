"""
HTTP Server for Cloud Run deployment.

Provides SSE transport for remote MCP clients and a simple REST API.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse, Response
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

# API key for protecting the service
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


async def health(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok", "service": "kenpom-mcp"})


async def tools(request: Request) -> JSONResponse:
    """List available tools."""
    tool_list = [
        {"name": "get_ratings", "description": "Get Pomeroy ratings for all teams"},
        {"name": "get_efficiency", "description": "Get efficiency and tempo stats"},
        {"name": "get_four_factors", "description": "Get Four Factors stats"},
        {"name": "get_team_stats", "description": "Get miscellaneous team stats"},
        {"name": "get_player_stats", "description": "Get player leaders by metric"},
        {"name": "get_height", "description": "Get height/experience data"},
        {"name": "get_fanmatch", "description": "Get game predictions for a date"},
        {"name": "get_arenas", "description": "Get arena information"},
        {"name": "get_game_attrs", "description": "Get top games by attribute"},
        {"name": "get_program_ratings", "description": "Get historical program ratings"},
        {"name": "get_kpoy", "description": "Get KPOY standings"},
        {"name": "get_point_distribution", "description": "Get point distribution"},
        {"name": "get_hca", "description": "Get home court advantage data"},
    ]
    return JSONResponse(tool_list)


async def sse(request: Request) -> StreamingResponse:
    """SSE endpoint for MCP clients."""
    async def event_stream():
        yield 'event: connected\ndata: {"status": "connected", "version": "0.2.0"}\n\n'
        # Keep connection alive
        import asyncio
        while True:
            yield 'event: ping\ndata: {}\n\n'
            await asyncio.sleep(30)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


async def mcp_handler(request: Request) -> JSONResponse:
    """Handle MCP JSON-RPC requests."""
    try:
        body = await request.json()
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id")

        result = await call_tool(method, params)

        return JSONResponse({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id,
        })
    except Exception as e:
        logger.exception("Error handling MCP request")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": None,
        }, status_code=500)


async def call_tool(method: str, params: dict) -> dict:
    """Call a tool by name."""
    scraper = get_scraper()

    if method == "get_ratings":
        soup = await scraper.get_ratings_page(params.get("season"))
        return {"data": parse_pomeroy_ratings(soup)}
    elif method == "get_efficiency":
        soup = await scraper.get_efficiency_page(params.get("season"))
        return {"data": parse_efficiency(soup)}
    elif method == "get_four_factors":
        soup = await scraper.get_four_factors_page(params.get("season"))
        return {"data": parse_four_factors(soup)}
    elif method == "get_team_stats":
        soup = await scraper.get_team_stats_page(
            defense=params.get("defense", False),
            season=params.get("season")
        )
        return {"data": parse_team_stats(soup, defense=params.get("defense", False))}
    elif method == "get_player_stats":
        soup = await scraper.get_player_stats_page(
            metric=params.get("metric", "eFG"),
            season=params.get("season"),
            conf=params.get("conference")
        )
        return {"data": parse_player_stats(soup)}
    elif method == "get_height":
        soup = await scraper.get_height_page(params.get("season"))
        return {"data": parse_height(soup)}
    elif method == "get_fanmatch":
        soup = await scraper.get_fanmatch_page(params.get("date"))
        return {"data": parse_fanmatch(soup)}
    elif method == "get_arenas":
        soup = await scraper.get_arenas_page(params.get("season"))
        return {"data": parse_arenas(soup)}
    elif method == "get_game_attrs":
        soup = await scraper.get_game_attrs_page(
            metric=params.get("metric", "Excitement"),
            season=params.get("season")
        )
        return {"data": parse_game_attrs(soup)}
    elif method == "get_program_ratings":
        soup = await scraper.get_program_ratings_page()
        return {"data": parse_program_ratings(soup)}
    elif method == "get_kpoy":
        soup = await scraper.get_kpoy_page(params.get("season"))
        return {"data": parse_kpoy(soup)}
    elif method == "get_point_distribution":
        soup = await scraper.get_point_dist_page(params.get("season"))
        return {"data": parse_point_distribution(soup)}
    elif method == "get_hca":
        soup = await scraper.get_hca_page()
        return {"data": parse_hca(soup)}
    else:
        raise ValueError(f"Unknown tool: {method}")


# CORS and Auth middleware
async def auth_middleware(request: Request, call_next):
    # Allow OPTIONS for CORS preflight
    if request.method == "OPTIONS":
        return Response(
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, X-API-Key",
            }
        )
    
    # Health check doesn't require auth
    if request.url.path in ["/", "/health"]:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    
    # Check API key if configured
    if API_KEY:
        provided_key = request.headers.get("X-API-Key", "")
        if provided_key != API_KEY:
            return JSONResponse(
                {"error": "Unauthorized. Provide valid X-API-Key header."},
                status_code=401
            )
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


routes = [
    Route("/", health),
    Route("/health", health),
    Route("/tools", tools),
    Route("/sse", sse),
    Route("/mcp", mcp_handler, methods=["POST"]),
]

app = Starlette(routes=routes)
app.middleware("http")(auth_middleware)

