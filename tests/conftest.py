"""Pytest fixtures for KenPom MCP tests."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> BeautifulSoup:
    """Load an HTML fixture and return BeautifulSoup object."""
    filepath = FIXTURES_DIR / filename
    with open(filepath) as f:
        return BeautifulSoup(f.read(), "lxml")


@pytest.fixture
def ratings_page():
    """Pomeroy ratings page HTML."""
    return load_fixture("ratings.html")


@pytest.fixture
def efficiency_page():
    """Efficiency summary page HTML."""
    return load_fixture("efficiency.html")


@pytest.fixture
def four_factors_page():
    """Four Factors page HTML."""
    return load_fixture("four_factors.html")


@pytest.fixture
def team_stats_offense_page():
    """Team stats (offense) page HTML."""
    return load_fixture("team_stats_offense.html")


@pytest.fixture
def team_stats_defense_page():
    """Team stats (defense) page HTML."""
    return load_fixture("team_stats_defense.html")


@pytest.fixture
def player_stats_page():
    """Player stats page HTML."""
    return load_fixture("player_stats.html")


@pytest.fixture
def height_page():
    """Height/experience page HTML."""
    return load_fixture("height.html")


@pytest.fixture
def fanmatch_page():
    """FanMatch page HTML."""
    return load_fixture("fanmatch.html")


@pytest.fixture
def arenas_page():
    """Arenas page HTML."""
    return load_fixture("arenas.html")


@pytest.fixture
def hca_page():
    """Home court advantage page HTML."""
    return load_fixture("hca.html")


@pytest.fixture
def game_attrs_page():
    """Game attributes page HTML."""
    return load_fixture("game_attrs.html")


@pytest.fixture
def program_ratings_page():
    """Program ratings page HTML."""
    return load_fixture("program_ratings.html")


@pytest.fixture
def kpoy_page():
    """KenPom Player of the Year page HTML."""
    return load_fixture("kpoy.html")


@pytest.fixture
def point_dist_page():
    """Point distribution page HTML."""
    return load_fixture("point_dist.html")
