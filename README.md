# KenPom MCP Server

Async MCP server for KenPom basketball analytics with Google Cloud Run support.

> **Note**: Requires a paid KenPom subscription (email/password login, no API key needed).

## Features

- 🚀 **Async Architecture** — Built with httpx for non-blocking requests
- ☁️ **Google Cloud Run Ready** — Deploy globally with zero cold starts
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
