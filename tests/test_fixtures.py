"""Test that fixtures load correctly."""

import pytest


def test_ratings_fixture_loads(ratings_page):
    """Test ratings fixture loads as BeautifulSoup."""
    assert ratings_page is not None
    table = ratings_page.find("table", {"id": "ratings-table"})
    assert table is not None
    rows = table.find_all("tr")
    assert len(rows) > 1  # Header + data rows


def test_efficiency_fixture_loads(efficiency_page):
    """Test efficiency fixture loads."""
    assert efficiency_page is not None
    table = efficiency_page.find("table")
    assert table is not None


def test_four_factors_fixture_loads(four_factors_page):
    """Test four factors fixture loads."""
    assert four_factors_page is not None
    table = four_factors_page.find("table")
    assert table is not None


def test_team_stats_offense_fixture_loads(team_stats_offense_page):
    """Test team stats offense fixture loads."""
    assert team_stats_offense_page is not None
    table = team_stats_offense_page.find("table")
    assert table is not None


def test_team_stats_defense_fixture_loads(team_stats_defense_page):
    """Test team stats defense fixture loads."""
    assert team_stats_defense_page is not None
    table = team_stats_defense_page.find("table")
    assert table is not None


def test_player_stats_fixture_loads(player_stats_page):
    """Test player stats fixture loads."""
    assert player_stats_page is not None
    table = player_stats_page.find("table")
    assert table is not None


def test_height_fixture_loads(height_page):
    """Test height fixture loads."""
    assert height_page is not None
    table = height_page.find("table")
    assert table is not None


def test_fanmatch_fixture_loads(fanmatch_page):
    """Test fanmatch fixture loads."""
    assert fanmatch_page is not None
    title = fanmatch_page.find("h2")
    assert title is not None
    table = fanmatch_page.find("table")
    assert table is not None


def test_arenas_fixture_loads(arenas_page):
    """Test arenas fixture loads."""
    assert arenas_page is not None
    table = arenas_page.find("table")
    assert table is not None


def test_hca_fixture_loads(hca_page):
    """Test HCA fixture loads."""
    assert hca_page is not None
    table = hca_page.find("table")
    assert table is not None


def test_game_attrs_fixture_loads(game_attrs_page):
    """Test game attributes fixture loads."""
    assert game_attrs_page is not None
    table = game_attrs_page.find("table")
    assert table is not None


def test_program_ratings_fixture_loads(program_ratings_page):
    """Test program ratings fixture loads."""
    assert program_ratings_page is not None
    table = program_ratings_page.find("table")
    assert table is not None


def test_kpoy_fixture_loads(kpoy_page):
    """Test KPOY fixture loads."""
    assert kpoy_page is not None
    tables = kpoy_page.find_all("table")
    assert len(tables) == 2  # KPOY standings + Game MVP leaders


def test_point_dist_fixture_loads(point_dist_page):
    """Test point distribution fixture loads."""
    assert point_dist_page is not None
    table = point_dist_page.find("table")
    assert table is not None
