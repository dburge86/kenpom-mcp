# Contributing to KenPom MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/kenpom-mcp.git
   cd kenpom-mcp
   ```
3. **Set up the development environment**:
   ```bash
   uv sync
   cp .env.example .env  # Add your KenPom credentials
   uv run pre-commit install
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🧪 Development Workflow

### Running Tests
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=kenpom_mcp

# Run specific test file
uv run pytest tests/test_parsers.py -v

# Run tests matching a pattern
uv run pytest tests/ -k "test_login"
```

### Code Quality
```bash
# Run linter
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check src/ tests/ --fix

# Format code
uv run ruff format src/ tests/

# Run pre-commit checks manually
uv run pre-commit run --all-files
```

### Running Servers
```bash
# Local STDIO server
uv run kenpom-mcp

# HTTP dev server (port 8000)
uv run uvicorn kenpom_mcp.http_server:app --reload

# Test with MCP inspector
npx @modelcontextprotocol/inspector uv --directory . run kenpom-mcp
```

## 📝 Coding Standards

### Python Style
- **Python Version**: 3.12+
- **Linter**: ruff (configured in `pyproject.toml`)
- **Formatter**: ruff format
- **Line Length**: 100 characters
- **Type Hints**: Use modern syntax (`dict[str, Any]` not `Dict[str, Any]`)
- **Async**: Use `async`/`await` throughout (httpx is async)

### Code Organization
```python
# Good: Modern type hints
async def parse_data(html: str) -> list[dict[str, Any]]:
    ...

# Bad: Old-style type hints
from typing import Dict, List
async def parse_data(html: str) -> List[Dict[str, Any]]:
    ...
```

### Naming Conventions
- **Functions**: `snake_case` (e.g., `get_ratings`, `parse_html`)
- **Classes**: `PascalCase` (e.g., `KenPomScraper`, `ToolDefinition`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `TOOL_REGISTRY`, `BASE_URL`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

## 🧪 Testing Requirements

### Test Coverage
- All new features must include tests
- Aim for 100% coverage of new code
- Use pytest fixtures from `tests/conftest.py`

### Test Types
1. **Unit Tests** (`tests/test_parsers.py`): Test parser functions with HTML fixtures
2. **Integration Tests** (`tests/test_scraper.py`): Test scraper with HTTP mocking
3. **Fixtures** (`tests/fixtures/`): Add HTML samples for new parsers

### Writing Tests
```python
import pytest
from bs4 import BeautifulSoup
from kenpom_mcp.parsers import parse_new_data

@pytest.mark.asyncio
async def test_parse_new_data(new_data_html: BeautifulSoup):
    """Test parsing new data endpoint"""
    result = parse_new_data(new_data_html)

    # Verify structure
    assert isinstance(result, list)
    assert len(result) > 0

    # Verify fields (use flexible matching for KenPom HTML variations)
    first_item = result[0]
    assert any("Team" in key for key in first_item.keys())
    assert any("Rank" in key for key in first_item.keys())
```

## 🔧 Adding a New Tool

Follow these steps to add a new KenPom data tool:

### 1. Add Parser Function
Create or update a file in `src/kenpom_mcp/parsers/`:
```python
# src/kenpom_mcp/parsers/your_parser.py
from bs4 import BeautifulSoup

def parse_new_data(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Parse new data from KenPom page"""
    # Implementation here
    return results
```

### 2. Add to Tool Registry
Update `src/kenpom_mcp/tools.py`:
```python
async def handle_get_new_data(arguments: dict) -> list[dict]:
    """Handler for get_new_data tool"""
    season = arguments.get("season", "2026")
    html = await scraper.get_new_data_page(season)
    return parse_new_data(html)

TOOL_REGISTRY["get_new_data"] = ToolDefinition(
    name="get_new_data",
    description="Get new data from KenPom",
    handler=handle_get_new_data,
    input_schema={
        "type": "object",
        "properties": {
            "season": {"type": "string", "description": "Season year"}
        },
    },
)
```

### 3. Add Scraper Method
Update `src/kenpom_mcp/scraper.py`:
```python
async def get_new_data_page(self, season: str = "2026") -> BeautifulSoup:
    """Fetch new data page from KenPom"""
    url = f"{self.BASE_URL}/newdata.php?s={season}"
    return await self._fetch(url, f"newdata:{season}", ttl=1800)
```

### 4. Add FastMCP Decorator
Update `src/kenpom_mcp/server.py`:
```python
@mcp.tool()
async def get_new_data(season: str = "2026") -> list[dict]:
    """Get new data from KenPom"""
    return await call_tool_handler("get_new_data", {"season": season})
```

### 5. Add Tests
Add HTML fixture in `tests/fixtures/new_data.html`, then:
```python
# tests/conftest.py
@pytest.fixture
def new_data_html() -> BeautifulSoup:
    return load_fixture("new_data.html")

# tests/test_parsers.py
def test_parse_new_data(new_data_html):
    result = parse_new_data(new_data_html)
    assert len(result) > 0
    # Add assertions

# tests/test_scraper.py
@pytest.mark.asyncio
async def test_get_new_data(httpx_mock):
    # Add mock and test
```

## 📋 Pull Request Process

1. **Update tests** for any changed functionality
2. **Run the full test suite**: `uv run pytest tests/`
3. **Ensure linting passes**: `uv run ruff check src/ tests/`
4. **Update documentation** if needed (README.md, CLAUDE.md)
5. **Write a clear PR description**:
   - What problem does this solve?
   - What changes were made?
   - How was it tested?
6. **Link related issues** (if applicable)

### Commit Message Format
```
type: brief description

Longer explanation of what changed and why.

Changes:
- Bullet list of specific changes
- Keep technical but readable

Co-Authored-By: Your Name <your.email@example.com>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `test`: Add or update tests
- `refactor`: Code restructuring without behavior change
- `docs`: Documentation updates
- `chore`: Build/tooling changes

### PR Checklist
- [ ] Tests pass locally (`uv run pytest tests/`)
- [ ] Linting passes (`uv run ruff check src/ tests/`)
- [ ] Formatting is correct (`uv run ruff format src/ tests/`)
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow format
- [ ] No secrets or credentials added
- [ ] Pre-commit hooks installed and passing

## 🐛 Reporting Bugs

Use GitHub Issues to report bugs. Include:
- **Description**: What went wrong?
- **Steps to Reproduce**: Minimal steps to trigger the bug
- **Expected Behavior**: What should happen?
- **Actual Behavior**: What actually happened?
- **Environment**: Python version, OS, deployment type (local/Cloud Run)
- **Logs**: Relevant error messages or stack traces

## 💡 Feature Requests

Use GitHub Issues to suggest features. Include:
- **Use Case**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives Considered**: Other ways to solve it?
- **Additional Context**: Screenshots, examples, etc.

## 🔒 Security Issues

**Do not open public issues for security vulnerabilities.**

See [SECURITY.md](SECURITY.md) for how to report security issues responsibly.

## 📚 Project Resources

- **README.md**: User documentation
- **CLAUDE.md**: Project context for AI agents
- **docs/adrs/**: Architectural Decision Records
- **docs/sessions/**: Development session logs
- **.AI_AGENT_NOTES.md**: Detailed development notes (not in repo)

## 🤝 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept criticism gracefully

### Not Acceptable
- Harassment or discriminatory behavior
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## ❓ Questions?

- **General Questions**: Open a GitHub Discussion
- **Bug Reports**: Open a GitHub Issue
- **Security Issues**: See [SECURITY.md](SECURITY.md)

## 🙏 Thank You!

Every contribution helps make this project better. We appreciate your time and effort!

---

**Happy Contributing!** 🎉
