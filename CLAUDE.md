# KenPom MCP Server

## Purpose
Async MCP server that scrapes KenPom basketball analytics and exposes 13+ data tools via STDIO (local) and SSE (remote) transports. Deployed on Google Cloud Run for global access.

## Tech Stack
- Python 3.12+ (uv package manager)
- FastMCP framework
- httpx (async HTTP client)
- BeautifulSoup4 + lxml (HTML parsing)
- Uvicorn + Starlette (HTTP server)

## Current Status
- Production deployment: https://kenpom-mcp-965342935330.us-central1.run.app
- Requires paid KenPom subscription (email/password)
- Smart caching with KV store to reduce scraping

## Key Files
- `src/kenpom_mcp/server.py` - FastMCP server with 13 tools
- `src/kenpom_mcp/scraper.py` - Async scraper with auth
- `src/kenpom_mcp/parsers/` - HTML parsing modules
- `pyproject.toml` - Dependencies and project config

## How to Run
```bash
# Local (STDIO)
uv sync && uv run kenpom-mcp

# Remote (SSE dev)
uv run pywrangler dev

# Test with inspector
npx @modelcontextprotocol/inspector uv --directory . run kenpom-mcp
```
