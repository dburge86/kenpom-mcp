# KenPom MCP Server 🏀

[![CI](https://github.com/dburge86/kenpom-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dburge86/kenpom-mcp/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Production-ready async MCP server for KenPom basketball analytics.

> **Note**: Requires a paid KenPom subscription ([kenpom.com](https://kenpom.com)) - email/password login, no API key needed.

## ✨ Project Status: Production Ready

- ✅ **100% Test Coverage** — 61 tests covering all parsers and scraper
- ✅ **CI/CD Pipeline** — GitHub Actions running tests, linting, and formatting
- ✅ **Code Quality** — Pre-commit hooks with ruff enforcement
- ✅ **Network Resilience** — Retry logic with exponential backoff
- ✅ **Dual Transport** — Local (STDIO) and self-hosted HTTP/SSE support

## Features

- 🚀 **Async Architecture** — Built with httpx for non-blocking requests
- ☁️ **Self-Hostable** — Optional HTTP/SSE server for remote access
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

### Remote Mode (Self-Hosted)

If you run the HTTP server on your own infrastructure:

```json
{
  "mcpServers": {
    "kenpom": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-server-url/sse"
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

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

This project uses:
- **pytest** for testing with async support
- **ruff** for linting and formatting
- **pre-commit** for automated quality checks
- **GitHub Actions** for CI/CD

All PRs must pass tests and linting checks.

## 🔒 Security

For security issues, please see [SECURITY.md](SECURITY.md) for responsible disclosure guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **KenPom** ([kenpom.com](https://kenpom.com)) - Ken Pomeroy's advanced basketball analytics
- **FastMCP** ([github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)) - MCP server framework
- **MCP Protocol** ([modelcontextprotocol.io](https://modelcontextprotocol.io)) - Model Context Protocol specification

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/dburge86/kenpom-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dburge86/kenpom-mcp/discussions)
- **Security**: See [SECURITY.md](SECURITY.md)

---

**Made with ❤️ for basketball analytics enthusiasts**
