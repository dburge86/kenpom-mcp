# KenPom MCP Server

[![CI](https://github.com/dburge86/kenpom-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dburge86/kenpom-mcp/actions/workflows/ci.yml)

Production-ready async MCP server for KenPom basketball analytics with Google Cloud Run support.

> **Note**: Requires a paid KenPom subscription (email/password login, no API key needed).

## Project Status: Production Ready ✅

- ✅ **100% Test Coverage** — 61 tests covering all parsers and scraper
- ✅ **CI/CD Pipeline** — GitHub Actions running tests, linting, and formatting
- ✅ **Code Quality** — Pre-commit hooks with ruff enforcement
- ✅ **Network Resilience** — Retry logic with exponential backoff
- ✅ **Cloud Deployed** — Running on Google Cloud Run with free tier protection

## Features

- 🚀 **Async Architecture** — Built with httpx for non-blocking requests
- ☁️ **Google Cloud Run Ready** — Deploy globally with zero cold starts
- 💾 **Smart Caching** — KV-based caching to reduce scraping frequency
- 🔧 **Dual Transport** — Local (STDIO) and Remote (SSE) support
- 📊 **13+ Data Tools** — Full coverage of KenPom stats
- 🔄 **Retry Logic** — Automatic retry with backoff for network failures
- 🧪 **Well Tested** — Comprehensive unit and integration tests

## Quick Start (Local)

```bash
cd /path/to/mcp_kenpom
cp .env.example .env  # Add your credentials
uv sync
uv run kenpom-mcp
```

## Cloud Deployment (Google Cloud Run)

The service is deployed at:

```
https://kenpom-mcp-965342935330.us-central1.run.app
```

**Free Tier Protection:**

- Min instances: 0 (scales to zero when idle)
- Max instances: 1 (prevents runaway scaling)
- Memory: 256Mi
- CPU: 1

### Test the deployment:

```bash
# Health check (no auth required)
curl https://kenpom-mcp-965342935330.us-central1.run.app/health

# List tools (requires API key)
curl -H "X-API-Key: YOUR_API_KEY" \
  https://kenpom-mcp-965342935330.us-central1.run.app/tools

# Call a tool
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"method": "get_fanmatch", "params": {}, "id": 1}' \
  https://kenpom-mcp-965342935330.us-central1.run.app/mcp
```

## MCP Client Configuration

### Local Mode

```json
{
  "mcpServers": {
    "kenpom": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp_kenpom", "run", "kenpom-mcp"]
    }
  }
}
```

### Remote Mode (Cloud Run)

```json
{
  "mcpServers": {
    "kenpom": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://kenpom-mcp-965342935330.us-central1.run.app/sse"
      ]
    }
  }
}
```

## Available Tools

| Tool                     | Description                                   |
| ------------------------ | --------------------------------------------- |
| `get_ratings`            | Pomeroy ratings (rank, adj efficiency, tempo) |
| `get_efficiency`         | Efficiency and tempo stats                    |
| `get_four_factors`       | eFG%, TO%, OR%, FTRate                        |
| `get_team_stats`         | Miscellaneous team stats (offense/defense)    |
| `get_player_stats`       | Player leaders by metric                      |
| `get_height`             | Height/experience data                        |
| `get_fanmatch`           | Game predictions by date                      |
| `get_arenas`             | Arena information                             |
| `get_game_attrs`         | Top games by attribute (excitement, upsets)   |
| `get_program_ratings`    | Historical program rankings                   |
| `get_kpoy`               | Player of the Year standings                  |
| `get_point_distribution` | Scoring breakdown by shot type                |
| `get_hca`                | Home court advantage data                     |

## Architecture

```
src/kenpom_mcp/
├── server.py          # FastMCP server with 13 tools (STDIO transport)
├── http_server.py     # Starlette server (HTTP/SSE transport)
├── tools.py           # Unified tool registry (single source of truth)
├── scraper.py         # Async httpx scraper with retry logic
└── parsers/           # HTML parsing modules
    ├── ratings.py     # Pomeroy ratings
    ├── efficiency.py  # Efficiency and tempo stats
    ├── stats.py       # Team and player stats
    ├── fanmatch.py    # Game predictions
    └── misc.py        # Arena, HCA, program ratings, KPOY

tests/
├── conftest.py        # Pytest fixtures
├── fixtures/          # 14 HTML sample files
├── test_fixtures.py   # Fixture loading tests
├── test_parsers.py    # 33 parser unit tests
└── test_scraper.py    # 14 scraper integration tests
```

## Development

### Setup

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env  # Add your KenPom credentials

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install
```

### Running

```bash
# Local dev (STDIO)
uv run kenpom-mcp

# HTTP dev server (port 8000)
uv run uvicorn kenpom_mcp.http_server:app --reload

# Test with MCP inspector
npx @modelcontextprotocol/inspector uv --directory . run kenpom-mcp
```

### Testing & Quality

```bash
# Run all tests
uv run pytest tests/

# Run tests with coverage
uv run pytest tests/ --cov=kenpom_mcp

# Run specific test file
uv run pytest tests/test_parsers.py -v

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

## Contributing

This project uses:
- **pytest** for testing with async support
- **ruff** for linting and formatting
- **pre-commit** for automated quality checks
- **GitHub Actions** for CI/CD

All PRs must pass tests and linting checks.

## License

MIT
