# KenPom MCP Server Polish Plan

## Overview
This plan addresses gaps identified in the engineering audit. The server is functional and deployed but lacks test coverage, CI, and has duplicate code between transport implementations.

**Current state:** Beta-ready, deployed on Cloud Run
**Target state:** Production-ready with test coverage and CI

---

## Task 1: Create pytest fixtures with sample KenPom HTML
**Priority:** High | **Effort:** M

Create test fixtures directory with sample HTML responses from KenPom pages. These enable testing parsers without hitting live servers.

### Steps
1. Create `tests/fixtures/` directory
2. Add sample HTML files for each page type:
   - `ratings.html` (Pomeroy ratings page)
   - `efficiency.html` (efficiency summary)
   - `four_factors.html`
   - `team_stats_offense.html`
   - `team_stats_defense.html`
   - `player_stats.html`
   - `height.html`
   - `fanmatch.html`
   - `arenas.html`
   - `hca.html`
   - `game_attrs.html`
   - `program_ratings.html`
   - `kpoy.html`
   - `point_dist.html`
3. Create `tests/conftest.py` with pytest fixtures that load these HTML files as BeautifulSoup objects

### Acceptance criteria
- [ ] All 14 HTML fixtures exist with realistic table structures
- [ ] `conftest.py` provides `@pytest.fixture` for each page type
- [ ] Fixtures return BeautifulSoup objects ready for parser functions

---

## Task 2: Add unit tests for all 13 parsers
**Priority:** High | **Effort:** M

Write unit tests for each parser function using the HTML fixtures.

### Steps
1. Create `tests/test_parsers.py`
2. Add test functions for each parser:
   - `test_parse_pomeroy_ratings()`
   - `test_parse_efficiency()`
   - `test_parse_four_factors()`
   - `test_parse_team_stats_offense()`
   - `test_parse_team_stats_defense()`
   - `test_parse_player_stats()`
   - `test_parse_height()`
   - `test_parse_fanmatch()`
   - `test_parse_arenas()`
   - `test_parse_hca()`
   - `test_parse_game_attrs()`
   - `test_parse_program_ratings()`
   - `test_parse_kpoy()`
   - `test_parse_point_distribution()`
3. Each test should verify:
   - Returns list/dict (correct type)
   - Contains expected fields
   - Handles edge cases (empty table, missing columns)

### Acceptance criteria
- [ ] All 13 parser functions have corresponding tests
- [ ] Tests pass with `uv run pytest tests/test_parsers.py`
- [ ] Edge cases covered (empty input, malformed HTML)

---

## Task 3: Add integration test for scraper auth flow
**Priority:** High | **Effort:** S

Test the authentication flow with mocked HTTP responses.

### Steps
1. Create `tests/test_scraper.py`
2. Use `pytest-httpx` or `respx` to mock httpx requests
3. Add to dev dependencies: `pytest-httpx>=0.30.0`
4. Test cases:
   - `test_login_success()` - mock successful login response
   - `test_login_failure()` - mock failed login (no "Logged in as" text)
   - `test_fetch_requires_login()` - verify login called before fetch
   - `test_fetch_cached_returns_cached()` - verify cache hit skips HTTP

### Acceptance criteria
- [ ] Auth flow tested without hitting real KenPom servers
- [ ] Login success/failure paths covered
- [ ] Cache behavior verified

---

## Task 4: Create GitHub Actions CI workflow
**Priority:** High | **Effort:** S

Add automated testing on push/PR.

### Steps
1. Create `.github/workflows/ci.yml`
2. Configure workflow:
   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: astral-sh/setup-uv@v4
         - run: uv sync --dev
         - run: uv run pytest
         - run: uv run ruff check src/
   ```
3. Add branch protection requiring CI pass (manual step)

### Acceptance criteria
- [ ] CI runs on every push and PR
- [ ] Tests and lint must pass
- [ ] Badge added to README (optional)

---

## Task 5: Add ruff lint config to pyproject.toml
**Priority:** Medium | **Effort:** S

Configure ruff for linting and formatting.

### Steps
1. Add ruff to dev dependencies in `pyproject.toml`:
   ```toml
   [dependency-groups]
   dev = [
       "pytest>=8.0.0",
       "ruff>=0.8.0",
   ]
   ```
2. Add ruff config to `pyproject.toml`:
   ```toml
   [tool.ruff]
   target-version = "py312"
   line-length = 100

   [tool.ruff.lint]
   select = ["E", "F", "I", "UP", "B"]
   ignore = ["E501"]  # line length handled by formatter

   [tool.ruff.format]
   quote-style = "double"
   ```
3. Run `uv run ruff check src/ --fix` to auto-fix issues
4. Run `uv run ruff format src/` to format code

### Acceptance criteria
- [ ] `uv run ruff check src/` passes with no errors
- [ ] `uv run ruff format src/ --check` shows no changes needed

---

## Task 6: Unify tool definitions between server.py and http_server.py
**Priority:** High | **Effort:** M

Eliminate duplicate tool definitions and dispatch logic.

### Steps
1. Create `src/kenpom_mcp/tools.py` with shared tool registry
2. Define tools once with metadata:
   ```python
   TOOL_REGISTRY = {
       "get_ratings": {
           "description": "Get Pomeroy ratings for all teams",
           "params": {"season": {"type": "string", "description": "Season year"}},
           "handler": lambda scraper, args: ...,
       },
       # ... etc
   }
   ```
3. Refactor `server.py` to use FastMCP decorators that reference registry
4. Refactor `http_server.py` to generate TOOLS list from registry
5. Single `call_tool()` function shared by both

### Acceptance criteria
- [ ] Tool definitions exist in one place only
- [ ] Both STDIO and HTTP servers use same definitions
- [ ] Adding a new tool requires changes to one file only

---

## Task 7: Add retry/backoff to scraper login
**Priority:** Medium | **Effort:** S

Handle transient network failures gracefully.

### Steps
1. Add `tenacity` to dependencies or implement simple retry loop
2. Modify `scraper.py` login method:
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential

   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
   async def login(self) -> bool:
       ...
   ```
3. Add specific exception types for auth failures vs network errors
4. Log retry attempts

### Acceptance criteria
- [x] Login retries up to 3 times on network errors
- [x] Auth failures (bad credentials) fail immediately without retry
- [x] Retry attempts logged at WARNING level

---

## Task 8: Add pre-commit hooks config
**Priority:** Low | **Effort:** S

Automate lint/format checks before commits.

### Steps
1. Create `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.8.0
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format
   ```
2. Add pre-commit to dev dependencies
3. Document setup in README:
   ```bash
   uv run pre-commit install
   ```

### Acceptance criteria
- [x] `uv run pre-commit run --all-files` passes
- [x] Hooks run automatically on `git commit`

---

## Execution Order

```
Task 1 (fixtures) ─┬─> Task 2 (parser tests) ─┬─> Task 4 (CI)
                   │                          │
Task 3 (scraper)  ─┘                          │
                                              │
Task 5 (ruff) ────────────────────────────────┤
                                              │
Task 6 (unify tools) ─────────────────────────┤
                                              │
Task 7 (retry) ───────────────────────────────┤
                                              │
Task 8 (pre-commit) ──────────────────────────┘
```

**Recommended order:** 1 → 2 → 3 → 5 → 4 → 6 → 7 → 8

Tasks 1-3 establish test coverage first. Task 5 adds linting. Task 4 creates CI that runs tests + lint. Tasks 6-8 are improvements that can be done in any order after CI exists.
