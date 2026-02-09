# KenPom MCP Server

## Purpose
Production-ready async MCP server that scrapes KenPom basketball analytics and exposes 13 data tools via STDIO (local) and HTTP/SSE (remote) transports.

## Project Status: Production Ready ✅
- 100% test coverage (61 tests)
- Automated CI/CD with GitHub Actions
- Pre-commit hooks enforcing code quality
- Network resilience with retry logic
- Unified tool registry (no code duplication)

## Tech Stack
- **Python 3.12+** with uv package manager
- **FastMCP** framework for STDIO transport
- **Starlette** for HTTP/SSE transport
- **httpx** async HTTP client with retry logic (tenacity)
- **BeautifulSoup4 + lxml** for HTML parsing
- **pytest** with pytest-asyncio and pytest-httpx for testing
- **ruff** for linting and formatting
- **pre-commit** for automated quality checks

## Architecture
```
src/kenpom_mcp/
├── server.py          # FastMCP server (STDIO transport)
├── http_server.py     # Starlette server (HTTP/SSE transport)
├── tools.py           # Unified tool registry (13 tools)
├── scraper.py         # Async scraper with auth + retry logic
└── parsers/           # HTML parsers for each KenPom page type

tests/
├── fixtures/          # 14 HTML fixtures for testing
├── test_fixtures.py   # Fixture loading tests (14 tests)
├── test_parsers.py    # Parser unit tests (33 tests)
└── test_scraper.py    # Scraper integration tests (14 tests)
```

## Key Files
- **src/kenpom_mcp/server.py** - FastMCP server with 13 tools (STDIO)
- **src/kenpom_mcp/http_server.py** - Starlette server (HTTP/SSE)
- **src/kenpom_mcp/tools.py** - Unified tool registry (single source of truth)
- **src/kenpom_mcp/scraper.py** - Async scraper with retry logic
- **src/kenpom_mcp/parsers/** - HTML parsing modules
- **tests/** - Comprehensive test suite (61 tests)
- **pyproject.toml** - Dependencies and project config
- **.pre-commit-config.yaml** - Pre-commit hooks (ruff)
- **.github/workflows/ci.yml** - CI/CD pipeline

## Development Setup
```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env  # Add KENPOM_EMAIL and KENPOM_PASSWORD

# Install pre-commit hooks (recommended)
uv run pre-commit install

# Run tests
uv run pytest tests/

# Run server locally (STDIO)
uv run kenpom-mcp

# Run HTTP server (port 8000)
uv run uvicorn kenpom_mcp.http_server:app --reload

# Test with MCP inspector
npx @modelcontextprotocol/inspector uv --directory . run kenpom-mcp
```

## Testing
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=kenpom_mcp

# Run specific test file
uv run pytest tests/test_parsers.py -v

# Run pre-commit checks
uv run pre-commit run --all-files
```

## Available Tools (13)
1. **get_ratings** - Pomeroy ratings (rank, adj efficiency, tempo)
2. **get_efficiency** - Efficiency and tempo stats
3. **get_four_factors** - Four Factors (eFG%, TO%, OR%, FTRate)
4. **get_team_stats** - Miscellaneous team stats (offense/defense)
5. **get_player_stats** - Player leaders by metric
6. **get_height** - Height/experience data
7. **get_fanmatch** - Game predictions by date
8. **get_arenas** - Arena information
9. **get_game_attrs** - Top games by attribute (excitement, upsets)
10. **get_program_ratings** - Historical program rankings
11. **get_kpoy** - Player of the Year standings
12. **get_point_distribution** - Scoring breakdown by shot type
13. **get_hca** - Home court advantage data

## Common Issues & Solutions
- **Login failures**: Check KENPOM_EMAIL and KENPOM_PASSWORD in .env
- **Network errors**: Scraper has retry logic (3 attempts with exponential backoff)
- **Test failures**: Ensure .env is present or tests will skip auth-required operations
- **Pre-commit failures**: Run `uv run ruff check --fix` and `uv run ruff format`

## Project Journey & Current State

### What We've Accomplished
- ✅ **Built production-ready MCP server** — Async architecture with dual transports (STDIO + HTTP/SSE)
- ✅ **Achieved 100% test coverage** — 61 tests covering all parsers, scraper, and auth flows
- ✅ **Implemented CI/CD pipeline** — GitHub Actions running tests, linting, formatting on every push
- ✅ **Added quality enforcement** — Pre-commit hooks with ruff preventing bad commits
- ✅ **Unified codebase** — Eliminated 222 lines of duplicate code between transports via `tools.py`
- ✅ **Production-grade resilience** — Retry logic with exponential backoff for network failures
- ✅ **Prepared for public release** — Removed all personal infrastructure details, sanitized documentation
- ✅ **Tore down managed infrastructure** — Deleted Google Cloud Run deployment for self-hosted only model

### Current Status
- **Architecture**: 100% local-first, self-hostable HTTP/SSE optional
- **Test Coverage**: 61/61 passing, 100% coverage maintained
- **Code Quality**: Enforced via pre-commit hooks (ruff)
- **CI/CD**: Active and green on every push
- **Dependencies**: Stable, modern Python 3.12+ with async-first design
- **Maintenance**: Low overhead, single source of truth for tool definitions

### Key Decisions & Patterns Established

**Architecture:**
- STDIO as primary interface (FastMCP) — aligns with 95% of MCP ecosystem usage
- HTTP/SSE as optional feature — for users needing remote access or custom integrations
- No managed cloud infrastructure — fully self-hostable on any Python 3.12+ environment

**Code Organization:**
- Unified tool registry in `tools.py` — single definition, used by both transports
- Flexible parser testing — keyword-based field matching to handle KenPom HTML variations
- Custom exception hierarchy — `AuthenticationError` (fail fast) vs `NetworkError` (retry)
- Type annotations — modern Python 3.12+ syntax (`dict[str, Any]` not `Dict`)

**Quality Standards:**
- 100% test coverage as success metric (not a vanity metric)
- Pre-commit hooks prevent bad code from reaching git
- All tests async-first using `pytest-asyncio`
- HTTP mocks for integration tests (no real KenPom calls)

### Next Steps
- [ ] **Optional**: Document self-hosted HTTP deployment guide if users request it
- [ ] **Optional**: Add "Deployment" section to README if self-hosting becomes a common ask
- [ ] **Monitor**: Gather feedback from public users and iterate if needed
- [ ] **Maintain**: Keep dependencies updated, monitor CI/CD health

## Notes for AI Agents
- See `.AI_AGENT_NOTES.md` for detailed development history and lessons learned (not in git)
- All 13 tools use unified registry in `tools.py` - modify there for consistency
- Parser tests use flexible field matching (keyword-based) to handle KenPom HTML variations
- Scraper has custom exceptions: `AuthenticationError` (no retry) vs `NetworkError` (retry enabled)
- Pre-commit hooks run automatically on commit - ensure tests pass first
- This project prioritizes simplicity and production-readiness over premature optimization
