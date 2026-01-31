"""
Async KenPom scraper engine.
Handles authentication, session management, and HTTP requests using httpx.
"""

import logging
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://kenpom.com"
LOGIN_URL = f"{BASE_URL}/handlers/login_handler.php"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class KenPomScraper:
    """Async scraper for kenpom.com with session management."""

    def __init__(self, email: str, password: str, cache: Any = None):
        self._email = email
        self._password = password
        self._cache = cache
        self._client: httpx.AsyncClient | None = None
        self._logged_in = False

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True,
                timeout=30.0,
            )
        return self._client

    async def login(self) -> bool:
        """Authenticate with KenPom using email/password."""
        client = await self._get_client()

        # First hit the homepage to get cookies
        await client.get(BASE_URL)

        # Submit login form
        form_data = {
            "email": self._email,
            "password": self._password,
            "submit": "Login!",
        }

        await client.post(LOGIN_URL, data=form_data)

        # Verify login by checking homepage
        response = await client.get(BASE_URL)
        if "Logged in as" in response.text:
            self._logged_in = True
            logger.info("Successfully logged in to KenPom")
            return True
        else:
            logger.error("Login failed - check credentials")
            raise Exception("Login failed - check your KenPom credentials")

    async def _ensure_logged_in(self):
        """Ensure we have an authenticated session."""
        if not self._logged_in:
            await self.login()

    async def fetch(self, path: str, params: dict | None = None) -> BeautifulSoup:
        """Fetch a page and return parsed BeautifulSoup."""
        await self._ensure_logged_in()
        client = await self._get_client()

        url = f"{BASE_URL}/{path}"
        response = await client.get(url, params=params)
        response.raise_for_status()

        return BeautifulSoup(response.text, "lxml")

    async def fetch_cached(
        self, cache_key: str, path: str, params: dict | None = None, ttl: int = 300
    ) -> BeautifulSoup:
        """Fetch with caching support (used in Workers with KV)."""
        if self._cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit: {cache_key}")
                return BeautifulSoup(cached, "lxml")

        soup = await self.fetch(path, params)

        if self._cache:
            await self._cache.put(cache_key, str(soup), {"expirationTtl": ttl})
            logger.debug(f"Cached: {cache_key} (TTL: {ttl}s)")

        return soup

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    # =========================================================================
    # Data fetching methods (return raw BeautifulSoup for parsers)
    # =========================================================================

    async def get_ratings_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch Pomeroy ratings page."""
        params = {"y": season} if season else None
        cache_key = f"ratings:{season or 'current'}"
        return await self.fetch_cached(cache_key, "index.php", params, ttl=300)

    async def get_efficiency_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch efficiency summary page."""
        params = {"y": season} if season else None
        cache_key = f"efficiency:{season or 'current'}"
        return await self.fetch_cached(cache_key, "summary.php", params, ttl=300)

    async def get_four_factors_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch four factors page."""
        params = {"y": season} if season else None
        cache_key = f"four_factors:{season or 'current'}"
        return await self.fetch_cached(cache_key, "stats.php", params, ttl=300)

    async def get_team_stats_page(
        self, defense: bool = False, season: str | None = None
    ) -> BeautifulSoup:
        """Fetch team stats page."""
        params = {}
        if season:
            params["y"] = season
        if defense:
            params["s"] = "RankOppeFG_Pct"
        cache_key = f"team_stats:{'def' if defense else 'off'}:{season or 'current'}"
        return await self.fetch_cached(cache_key, "teamstats.php", params, ttl=300)

    async def get_player_stats_page(
        self, metric: str = "eFG", season: str | None = None, conf: str | None = None
    ) -> BeautifulSoup:
        """Fetch player stats page."""
        params = {"s": f"Rank{metric}"}
        if season:
            params["y"] = season
        if conf:
            params["c"] = conf
        cache_key = f"player_stats:{metric}:{conf or 'all'}:{season or 'current'}"
        return await self.fetch_cached(cache_key, "playerstats.php", params, ttl=300)

    async def get_height_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch height/experience page."""
        params = {"y": season} if season else None
        cache_key = f"height:{season or 'current'}"
        return await self.fetch_cached(cache_key, "height.php", params, ttl=300)

    async def get_fanmatch_page(self, date: str | None = None) -> BeautifulSoup:
        """Fetch FanMatch page for a specific date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        params = {"d": date}
        cache_key = f"fanmatch:{date}"
        # Shorter TTL for live games
        return await self.fetch_cached(cache_key, "fanmatch.php", params, ttl=60)

    async def get_arenas_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch arenas page."""
        params = {"y": season} if season else None
        cache_key = f"arenas:{season or 'current'}"
        return await self.fetch_cached(cache_key, "arenas.php", params, ttl=3600)

    async def get_hca_page(self) -> BeautifulSoup:
        """Fetch home court advantage page."""
        cache_key = "hca"
        return await self.fetch_cached(cache_key, "hca.php", ttl=3600)

    async def get_game_attrs_page(
        self, metric: str = "Excitement", season: str | None = None
    ) -> BeautifulSoup:
        """Fetch game attributes page."""
        metric_map = {
            "Excitement": "EMR",
            "Tension": "Tension",
            "Dominance": "Dom",
            "ComeBack": "Come",
            "FanMatch": "FMRank",
            "Upsets": "Upsets",
            "Busts": "Busts",
        }
        params = {"s": metric_map.get(metric, "EMR")}
        if season:
            params["y"] = season
        cache_key = f"game_attrs:{metric}:{season or 'current'}"
        return await self.fetch_cached(cache_key, "game_attrs.php", params, ttl=300)

    async def get_program_ratings_page(self) -> BeautifulSoup:
        """Fetch program ratings page."""
        cache_key = "program_ratings"
        return await self.fetch_cached(cache_key, "programs.php", ttl=3600)

    async def get_kpoy_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch KPOY page."""
        params = {"y": season} if season else None
        cache_key = f"kpoy:{season or 'current'}"
        return await self.fetch_cached(cache_key, "kpoy.php", params, ttl=300)

    async def get_point_dist_page(self, season: str | None = None) -> BeautifulSoup:
        """Fetch point distribution page."""
        params = {"y": season} if season else None
        cache_key = f"point_dist:{season or 'current'}"
        return await self.fetch_cached(cache_key, "pointdist.php", params, ttl=300)
