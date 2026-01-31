"""Integration tests for KenPom scraper with mocked HTTP responses."""

import pytest
from pytest_httpx import HTTPXMock

from kenpom_mcp.scraper import KenPomScraper, BASE_URL, LOGIN_URL


# =============================================================================
# Mock Cache Implementation
# =============================================================================


class MockCache:
    """Simple in-memory cache for testing."""

    def __init__(self):
        self.store = {}

    async def get(self, key):
        """Get value from cache."""
        return self.store.get(key)

    async def put(self, key, value, options=None):
        """Put value in cache."""
        self.store[key] = value


# =============================================================================
# Test Login Success
# =============================================================================


@pytest.mark.asyncio
async def test_login_success(httpx_mock: HTTPXMock):
    """Test successful login flow."""
    # Mock homepage response (initial cookie fetch)
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html><body>KenPom Homepage</body></html>",
    )

    # Mock login POST response
    httpx_mock.add_response(
        url=LOGIN_URL,
        method="POST",
        html="<html><body>Login submitted</body></html>",
    )

    # Mock homepage after login (should show "Logged in as")
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html><body>Logged in as test@example.com</body></html>",
    )

    # Create scraper and login
    scraper = KenPomScraper("test@example.com", "password123")
    success = await scraper.login()

    assert success is True
    assert scraper._logged_in is True

    # Verify all requests were made
    requests = httpx_mock.get_requests()
    assert len(requests) == 3
    assert requests[0].url == BASE_URL
    assert requests[1].url == LOGIN_URL
    assert requests[2].url == BASE_URL

    await scraper.close()


# =============================================================================
# Test Login Failure
# =============================================================================


@pytest.mark.asyncio
async def test_login_failure(httpx_mock: HTTPXMock):
    """Test failed login (bad credentials)."""
    # Mock homepage response (initial cookie fetch)
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html><body>KenPom Homepage</body></html>",
    )

    # Mock login POST response
    httpx_mock.add_response(
        url=LOGIN_URL,
        method="POST",
        html="<html><body>Login failed</body></html>",
    )

    # Mock homepage after login (no "Logged in as" text)
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html><body>Please log in</body></html>",
    )

    # Create scraper and attempt login
    scraper = KenPomScraper("bad@example.com", "wrongpassword")

    with pytest.raises(Exception) as exc_info:
        await scraper.login()

    assert "Login failed" in str(exc_info.value)
    assert scraper._logged_in is False

    await scraper.close()


# =============================================================================
# Test Fetch Requires Login
# =============================================================================


@pytest.mark.asyncio
async def test_fetch_requires_login(httpx_mock: HTTPXMock):
    """Test that fetch automatically logs in if not authenticated."""
    # Mock login sequence
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html><body>Homepage</body></html>",
    )
    httpx_mock.add_response(
        url=LOGIN_URL,
        method="POST",
        html="<html><body>Login</body></html>",
    )
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html><body>Logged in as test@example.com</body></html>",
    )

    # Mock the actual fetch request
    httpx_mock.add_response(
        url=f"{BASE_URL}/index.php",
        method="GET",
        html="<html><body><table id='ratings-table'></table></body></html>",
    )

    # Create scraper (not logged in yet)
    scraper = KenPomScraper("test@example.com", "password123")
    assert scraper._logged_in is False

    # Fetch should trigger automatic login
    result = await scraper.fetch("index.php")

    assert scraper._logged_in is True
    assert result is not None
    assert "table" in str(result)

    await scraper.close()


# =============================================================================
# Test Fetch with Query Parameters
# =============================================================================


@pytest.mark.asyncio
async def test_fetch_with_params(httpx_mock: HTTPXMock):
    """Test fetch with query parameters."""
    # Mock login
    httpx_mock.add_response(url=BASE_URL, method="GET", html="<html></html>")
    httpx_mock.add_response(url=LOGIN_URL, method="POST", html="<html></html>")
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html>Logged in as test@example.com</html>",
    )

    # Mock fetch with query params
    httpx_mock.add_response(
        url=f"{BASE_URL}/index.php?y=2024",
        method="GET",
        html="<html><body>2024 Season Data</body></html>",
    )

    scraper = KenPomScraper("test@example.com", "password123")
    result = await scraper.fetch("index.php", params={"y": "2024"})

    assert "2024 Season Data" in str(result)

    await scraper.close()


# =============================================================================
# Test Cache Behavior
# =============================================================================


@pytest.mark.asyncio
async def test_fetch_cached_returns_cached(httpx_mock: HTTPXMock):
    """Test that cached results skip HTTP requests."""
    # Allow non-executed mocks since cache hit bypasses login
    httpx_mock.allow_non_mocked_requests = False

    cache = MockCache()

    # Pre-populate cache
    cached_html = "<html><body>Cached ratings data</body></html>"
    await cache.put("ratings:current", cached_html)

    # Mock login (may not be called due to cache implementation)
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html></html>",
        is_optional=True,
    )
    httpx_mock.add_response(
        url=LOGIN_URL,
        method="POST",
        html="<html></html>",
        is_optional=True,
    )
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html>Logged in as test@example.com</html>",
        is_optional=True,
    )

    # Create scraper with cache
    scraper = KenPomScraper("test@example.com", "password123", cache=cache)

    # Fetch cached data - should not make HTTP request to ratings page
    result = await scraper.fetch_cached("ratings:current", "index.php")

    assert "Cached ratings data" in str(result)

    # Verify NO request was made to index.php (cache hit)
    requests = httpx_mock.get_requests()
    ratings_requests = [r for r in requests if "index.php" in str(r.url)]
    assert len(ratings_requests) == 0

    await scraper.close()


@pytest.mark.asyncio
async def test_fetch_cached_misses_fetches_new(httpx_mock: HTTPXMock):
    """Test that cache miss fetches fresh data."""
    cache = MockCache()

    # Mock login
    httpx_mock.add_response(url=BASE_URL, method="GET", html="<html></html>")
    httpx_mock.add_response(url=LOGIN_URL, method="POST", html="<html></html>")
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html>Logged in as test@example.com</html>",
    )

    # Mock fetch (cache miss)
    httpx_mock.add_response(
        url=f"{BASE_URL}/index.php",
        method="GET",
        html="<html><body>Fresh ratings data</body></html>",
    )

    scraper = KenPomScraper("test@example.com", "password123", cache=cache)

    # Cache miss - should fetch from HTTP
    result = await scraper.fetch_cached("ratings:current", "index.php")

    assert "Fresh ratings data" in str(result)

    # Verify cache was populated
    cached = await cache.get("ratings:current")
    assert cached is not None
    assert "Fresh ratings data" in cached

    await scraper.close()


# =============================================================================
# Test Helper Methods
# =============================================================================


@pytest.mark.asyncio
async def test_get_ratings_page(httpx_mock: HTTPXMock):
    """Test get_ratings_page helper method."""
    cache = MockCache()

    # Mock login
    httpx_mock.add_response(url=BASE_URL, method="GET", html="<html></html>")
    httpx_mock.add_response(url=LOGIN_URL, method="POST", html="<html></html>")
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html>Logged in as test@example.com</html>",
    )

    # Mock ratings page
    httpx_mock.add_response(
        url=f"{BASE_URL}/index.php?y=2024",
        method="GET",
        html="<html><table id='ratings-table'><tr><td>Duke</td></tr></table></html>",
    )

    scraper = KenPomScraper("test@example.com", "password123", cache=cache)
    result = await scraper.get_ratings_page(season="2024")

    assert result is not None
    assert "ratings-table" in str(result)
    assert "Duke" in str(result)

    await scraper.close()


@pytest.mark.asyncio
async def test_get_efficiency_page(httpx_mock: HTTPXMock):
    """Test get_efficiency_page helper method."""
    cache = MockCache()

    # Mock login
    httpx_mock.add_response(url=BASE_URL, method="GET", html="<html></html>")
    httpx_mock.add_response(url=LOGIN_URL, method="POST", html="<html></html>")
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html>Logged in as test@example.com</html>",
    )

    # Mock efficiency page
    httpx_mock.add_response(
        url=f"{BASE_URL}/summary.php",
        method="GET",
        html="<html><table><tr><td>Efficiency Data</td></tr></table></html>",
    )

    scraper = KenPomScraper("test@example.com", "password123", cache=cache)
    result = await scraper.get_efficiency_page()

    assert result is not None
    assert "Efficiency Data" in str(result)

    await scraper.close()


@pytest.mark.asyncio
async def test_get_fanmatch_page(httpx_mock: HTTPXMock):
    """Test get_fanmatch_page helper method."""
    cache = MockCache()

    # Mock login
    httpx_mock.add_response(url=BASE_URL, method="GET", html="<html></html>")
    httpx_mock.add_response(url=LOGIN_URL, method="POST", html="<html></html>")
    httpx_mock.add_response(
        url=BASE_URL,
        method="GET",
        html="<html>Logged in as test@example.com</html>",
    )

    # Mock fanmatch page
    httpx_mock.add_response(
        url=f"{BASE_URL}/fanmatch.php?d=2024-01-15",
        method="GET",
        html="<html><h2>Monday, January 15th</h2><table></table></html>",
    )

    scraper = KenPomScraper("test@example.com", "password123", cache=cache)
    result = await scraper.get_fanmatch_page(date="2024-01-15")

    assert result is not None
    assert "January 15th" in str(result)

    await scraper.close()


# =============================================================================
# Test Client Lifecycle
# =============================================================================


@pytest.mark.asyncio
async def test_client_reuse():
    """Test that HTTP client is reused across requests."""
    scraper = KenPomScraper("test@example.com", "password123")

    # Get client twice
    client1 = await scraper._get_client()
    client2 = await scraper._get_client()

    # Should be the same instance
    assert client1 is client2

    await scraper.close()


@pytest.mark.asyncio
async def test_close_cleans_up_client():
    """Test that close() cleans up HTTP client."""
    scraper = KenPomScraper("test@example.com", "password123")

    # Create client
    await scraper._get_client()
    assert scraper._client is not None

    # Close should clean up
    await scraper.close()
    assert scraper._client is None
