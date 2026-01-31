"""
HTTP Server for Cloud Run deployment.

Implements MCP Streamable HTTP transport for remote MCP clients.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from .scraper import KenPomScraper
from .tools import call_tool as call_tool_handler
from .tools import get_all_tools

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


# MCP Tool definitions - Generated from unified registry
TOOLS = [tool.to_mcp_schema() for tool in get_all_tools()]


async def call_tool(name: str, arguments: dict) -> Any:
    """Execute a tool and return its result."""
    scraper = get_scraper()
    return await call_tool_handler(scraper, name, arguments)


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
            return JSONResponse(
                {
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
                }
            )

        elif method == "notifications/initialized":
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {},
                }
            )

        elif method == "tools/list":
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": TOOLS},
                }
            )

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            try:
                result = await call_tool(tool_name, arguments)
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": str(result)}],
                        },
                    }
                )
            except Exception as e:
                logger.exception(f"Tool error: {tool_name}")
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32603, "message": str(e)},
                    }
                )

        # Legacy direct tool call (for backwards compatibility)
        elif method.startswith("get_"):
            result = await call_tool(method, params)
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"data": result},
                }
            )

        else:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
            )

    except Exception as e:
        logger.exception("MCP handler error")
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)},
            },
            status_code=500,
        )


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
                status_code=401,
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
