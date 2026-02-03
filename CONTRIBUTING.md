# Contributing

Thanks for your interest in contributing!

## Quick Start

```bash
git clone https://github.com/dburge86/kenpom-mcp.git
cd kenpom-mcp
uv sync
cp .env.example .env  # Add your KenPom credentials
uv run pytest tests/  # Run tests
```

## Before Submitting a PR

1. Run tests: `uv run pytest tests/`
2. Run linter: `uv run ruff check src/ tests/`
3. Format code: `uv run ruff format src/ tests/`

## Questions?

Open an issue on GitHub.
