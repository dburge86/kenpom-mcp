"""
Cloudflare Worker entry point for KenPom MCP Server.

This file handles HTTP requests and routes them to the MCP server
using SSE transport for remote access.
"""

from workers import WorkerEntrypoint, Response, Request
from js import Object

# Import the MCP server
from kenpom_mcp.server import mcp, get_scraper
from kenpom_mcp.scraper import KenPomScraper


class KenPomMCPWorker(WorkerEntrypoint):
    """Cloudflare Worker for KenPom MCP Server."""

    async def fetch(self, request: Request) -> Response:
        """Handle incoming HTTP requests."""
        url = request.url
        method = request.method

        # Health check endpoint
        if "/health" in url:
            return Response('{"status": "ok", "service": "kenpom-mcp"}')

        # SSE endpoint for MCP
        if "/sse" in url:
            return await self._handle_sse(request)

        # MCP message endpoint
        if "/mcp" in url and method == "POST":
            return await self._handle_mcp_message(request)

        # Default: return info
        return Response(
            '{"name": "KenPom MCP Server", "version": "0.2.0", "endpoints": ["/sse", "/mcp", "/health"]}',
            headers={"Content-Type": "application/json"},
        )

    async def _handle_sse(self, request: Request) -> Response:
        """Handle SSE connection for MCP."""
        # For now, return SSE headers and connection info
        # Full SSE implementation requires the MCP SSE transport
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }

        # Return connection established event
        return Response(
            "event: connected\ndata: {\"status\": \"connected\"}\n\n",
            headers=headers,
        )

    async def _handle_mcp_message(self, request: Request) -> Response:
        """Handle MCP JSON-RPC messages."""
        try:
            body = await request.text()
            # Process through MCP server
            # This is a simplified handler - full implementation needs JSON-RPC routing
            return Response(
                '{"jsonrpc": "2.0", "result": {"status": "received"}, "id": 1}',
                headers={"Content-Type": "application/json"},
            )
        except Exception as e:
            return Response(
                f'{{"jsonrpc": "2.0", "error": {{"code": -32603, "message": "{str(e)}"}}, "id": null}}',
                headers={"Content-Type": "application/json"},
                status=500,
            )


# Export the worker
Default = KenPomMCPWorker
