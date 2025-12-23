# KenPom MCP Server

**God-Tier Edition** — Async MCP server for KenPom basketball analytics with Cloudflare Workers support.

> **Note**: Requires a paid KenPom subscription (email/password login, no API key needed).

## Features

- 🚀 **Async Architecture** — Built with httpx for non-blocking requests
- ☁️ **Cloudflare Workers Ready** — Deploy globally with zero cold starts
- 💾 **Smart Caching** — KV-based caching to reduce scraping frequency
- 🔧 **Dual Transport** — Local (STDIO) and Remote (SSE) support
- 📊 **13+ Data Tools** — Full coverage of KenPom stats

## Quick Start (Local)

```bash
cd /path/to/mcp_kenpom
cp .env.example .env  # Add your credentials
uv sync
uv run kenpom-mcp
```

## Cloud Deployment (Cloudflare Workers)

```bash
# Install workers-py
uv tool install workers-py

# Set secrets
uv run pywrangler secret put KENPOM_EMAIL
uv run pywrangler secret put KENPOM_PASSWORD

# Deploy
uv run pywrangler deploy
```

Your server will be live at: `https://kenpom-mcp.<account>.workers.dev`

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

### Remote Mode (after deployment)

```json
{
  "mcpServers": {
    "kenpom": {
      "command": "npx",
      "args": ["mcp-remote", "https://kenpom-mcp.<account>.workers.dev/sse"]
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
├── server.py          # FastMCP server with 13 tools
├── scraper.py         # Async httpx scraper with caching
└── parsers/           # HTML parsing modules
    ├── ratings.py
    ├── efficiency.py
    ├── stats.py
    ├── fanmatch.py
    └── misc.py
```

## Development

```bash
# Local dev (STDIO)
uv run kenpom-mcp

# Workers dev (SSE)
uv run pywrangler dev

# Test with MCP inspector
npx @modelcontextprotocol/inspector uv --directory . run kenpom-mcp
```

## License

MIT
