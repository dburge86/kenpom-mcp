"""Unit tests for KenPom HTML parsers."""

from kenpom_mcp.parsers import (
    parse_arenas,
    parse_efficiency,
    parse_fanmatch,
    parse_four_factors,
    parse_game_attrs,
    parse_hca,
    parse_height,
    parse_kpoy,
    parse_player_stats,
    parse_point_distribution,
    parse_pomeroy_ratings,
    parse_program_ratings,
    parse_team_stats,
)

# =============================================================================
# Test parse_pomeroy_ratings
# =============================================================================


def test_parse_pomeroy_ratings(ratings_page):
    """Test parsing Pomeroy ratings page."""
    result = parse_pomeroy_ratings(ratings_page)

    # Should return a list
    assert isinstance(result, list)
    assert len(result) > 0

    # Check first team
    first_team = result[0]
    assert first_team["Rank"] == "1"
    assert first_team["Team"] == "Duke"
    assert first_team["Conference"] == "ACC"
    assert first_team["Record"] == "20-3"
    # Core fields that should be present
    assert "AdjEM" in first_team


def test_parse_pomeroy_ratings_has_expected_fields(ratings_page):
    """Verify ratings parser returns expected fields."""
    result = parse_pomeroy_ratings(ratings_page)
    first_team = result[0]

    expected_fields = ["Rank", "Team", "Conference", "Record", "AdjEM"]
    for field in expected_fields:
        assert field in first_team, f"Missing field: {field}"


# =============================================================================
# Test parse_efficiency
# =============================================================================


def test_parse_efficiency(efficiency_page):
    """Test parsing efficiency page."""
    result = parse_efficiency(efficiency_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert first_team["Rank"] == "1"
    assert first_team["Team"] == "Duke"
    assert "AdjT" in first_team
    assert "AdjOE" in first_team
    assert "AdjDE" in first_team


def test_parse_efficiency_has_tempo_fields(efficiency_page):
    """Verify efficiency parser has tempo and possession length fields."""
    result = parse_efficiency(efficiency_page)
    first_team = result[0]

    assert "AdjT" in first_team
    assert "RawT" in first_team


# =============================================================================
# Test parse_four_factors
# =============================================================================


def test_parse_four_factors(four_factors_page):
    """Test parsing four factors page."""
    result = parse_four_factors(four_factors_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert first_team["Rank"] == "1"
    assert first_team["Team"] == "Duke"


def test_parse_four_factors_has_offensive_factors(four_factors_page):
    """Verify four factors has all offensive factors."""
    result = parse_four_factors(four_factors_page)
    first_team = result[0]

    # Check that offensive factor fields exist (with space separators)
    offensive_keywords = ["Off", "eFG", "TO", "OR", "FTRate"]
    for keyword in offensive_keywords:
        matching_fields = [key for key in first_team.keys() if keyword in key]
        assert len(matching_fields) > 0, f"Missing offensive field containing: {keyword}"


def test_parse_four_factors_has_defensive_factors(four_factors_page):
    """Verify four factors has all defensive factors."""
    result = parse_four_factors(four_factors_page)
    first_team = result[0]

    # Check that defensive factor fields exist (with space separators)
    defensive_keywords = ["Def", "eFG", "TO", "OR", "FTRate"]
    for keyword in defensive_keywords:
        matching_fields = [key for key in first_team.keys() if keyword in key]
        assert len(matching_fields) > 0, f"Missing defensive field containing: {keyword}"


# =============================================================================
# Test parse_team_stats
# =============================================================================


def test_parse_team_stats_offense(team_stats_offense_page):
    """Test parsing team stats (offense)."""
    result = parse_team_stats(team_stats_offense_page, defense=False)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert "Team" in first_team
    assert "Conference" in first_team


def test_parse_team_stats_defense(team_stats_defense_page):
    """Test parsing team stats (defense)."""
    result = parse_team_stats(team_stats_defense_page, defense=True)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert "Team" in first_team
    assert "Conference" in first_team


# =============================================================================
# Test parse_player_stats
# =============================================================================


def test_parse_player_stats(player_stats_page):
    """Test parsing player stats page."""
    result = parse_player_stats(player_stats_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_player = result[0]
    assert first_player["Rank"] == "1"
    assert first_player["Player"] == "Cooper Flagg"
    assert first_player["Team"] == "Duke"


def test_parse_player_stats_has_physical_attributes(player_stats_page):
    """Verify player stats has height, weight, year."""
    result = parse_player_stats(player_stats_page)
    first_player = result[0]

    assert "Height" in first_player
    assert "Weight" in first_player
    assert "Year" in first_player
    assert first_player["Height"] == "6-9"
    assert first_player["Year"] == "Fr"


# =============================================================================
# Test parse_height
# =============================================================================


def test_parse_height(height_page):
    """Test parsing height/experience page."""
    result = parse_height(height_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert first_team["Rank"] == "1"
    assert first_team["Team"] == "Duke"


def test_parse_height_has_all_metrics(height_page):
    """Verify height parser has all height/experience metrics."""
    result = parse_height(height_page)
    first_team = result[0]

    # Check for key metrics (field names may have spaces)
    expected_keywords = ["Hgt", "Experience", "Bench", "Continuity"]
    for keyword in expected_keywords:
        matching_fields = [key for key in first_team.keys() if keyword in key]
        assert len(matching_fields) > 0, f"Missing field containing: {keyword}"


# =============================================================================
# Test parse_fanmatch
# =============================================================================


def test_parse_fanmatch(fanmatch_page):
    """Test parsing FanMatch page."""
    result = parse_fanmatch(fanmatch_page)

    assert isinstance(result, dict)
    assert "date" in result
    assert "games" in result
    assert isinstance(result["games"], list)


def test_parse_fanmatch_extracts_daily_stats(fanmatch_page):
    """Verify FanMatch parser extracts daily statistics."""
    result = parse_fanmatch(fanmatch_page)

    assert result["date"] is not None
    assert result["ppg"] == 142.5
    assert result["avg_eff"] == 102.3


def test_parse_fanmatch_parses_games(fanmatch_page):
    """Verify FanMatch parser extracts game predictions."""
    result = parse_fanmatch(fanmatch_page)

    games = result["games"]
    assert len(games) == 3

    first_game = games[0]
    assert "Time" in first_game
    assert "Game" in first_game
    assert "Location" in first_game
    assert first_game["Time"] == "12:00 PM"


# =============================================================================
# Test parse_arenas
# =============================================================================


def test_parse_arenas(arenas_page):
    """Test parsing arenas page."""
    result = parse_arenas(arenas_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_arena = result[0]
    assert "Team" in first_arena
    assert "Arena" in first_arena


def test_parse_arenas_has_attendance_data(arenas_page):
    """Verify arenas parser has capacity and attendance."""
    result = parse_arenas(arenas_page)
    first_arena = result[0]

    attendance_fields = ["Capacity", "Avg", "Pct"]
    for field in attendance_fields:
        assert any(
            field in key for key in first_arena.keys()
        ), f"Missing attendance field containing: {field}"


# =============================================================================
# Test parse_hca
# =============================================================================


def test_parse_hca(hca_page):
    """Test parsing home court advantage page."""
    result = parse_hca(hca_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert first_team["Rank"] == "1"
    assert first_team["Team"] == "Duke"


def test_parse_hca_has_advantage_metrics(hca_page):
    """Verify HCA parser has home advantage metrics."""
    result = parse_hca(hca_page)
    first_team = result[0]

    # Check for key metrics (field names may have spaces)
    expected_keywords = ["HCA", "PF", "Record"]
    for keyword in expected_keywords:
        matching_fields = [key for key in first_team.keys() if keyword in key]
        assert len(matching_fields) > 0, f"Missing field containing: {keyword}"


# =============================================================================
# Test parse_game_attrs
# =============================================================================


def test_parse_game_attrs(game_attrs_page):
    """Test parsing game attributes page."""
    result = parse_game_attrs(game_attrs_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_game = result[0]
    assert first_game["Rank"] == "1"
    assert "Game" in first_game
    assert "Date" in first_game


def test_parse_game_attrs_has_game_info(game_attrs_page):
    """Verify game attributes has game details."""
    result = parse_game_attrs(game_attrs_page)
    first_game = result[0]

    expected_fields = ["Date", "Game", "Location"]
    for field in expected_fields:
        assert field in first_game, f"Missing field: {field}"


# =============================================================================
# Test parse_program_ratings
# =============================================================================


def test_parse_program_ratings(program_ratings_page):
    """Test parsing program ratings page."""
    result = parse_program_ratings(program_ratings_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_program = result[0]
    assert first_program["Rank"] == "1"
    assert first_program["Team"] == "Duke"


def test_parse_program_ratings_has_historical_data(program_ratings_page):
    """Verify program ratings has historical performance data."""
    result = parse_program_ratings(program_ratings_page)
    first_program = result[0]

    # Check for historical data keywords (field names may have spaces)
    historical_keywords = ["Best", "Worst", "Median", "Season"]
    for keyword in historical_keywords:
        matching_fields = [key for key in first_program.keys() if keyword in key]
        assert len(matching_fields) > 0, f"Missing field containing: {keyword}"


def test_parse_program_ratings_has_tournament_data(program_ratings_page):
    """Verify program ratings has NCAA tournament counts."""
    result = parse_program_ratings(program_ratings_page)
    first_program = result[0]

    # Check for tournament data keywords (field names may have spaces)
    tournament_keywords = ["NCAA", "Champs", "F4", "S16", "R1"]
    for keyword in tournament_keywords:
        matching_fields = [key for key in first_program.keys() if keyword in key]
        assert len(matching_fields) > 0, f"Missing field containing: {keyword}"


# =============================================================================
# Test parse_kpoy
# =============================================================================


def test_parse_kpoy(kpoy_page):
    """Test parsing KPOY page."""
    result = parse_kpoy(kpoy_page)

    # Should return list of tables (KPOY standings + Game MVP leaders)
    assert isinstance(result, list)
    assert len(result) == 2

    # Check first table (KPOY standings)
    kpoy_standings = result[0]
    assert isinstance(kpoy_standings, list)
    assert len(kpoy_standings) > 0


def test_parse_kpoy_has_player_info(kpoy_page):
    """Verify KPOY standings has player information."""
    result = parse_kpoy(kpoy_page)
    kpoy_standings = result[0]
    first_player = kpoy_standings[0]

    expected_fields = ["Player", "Team"]
    for field in expected_fields:
        assert field in first_player, f"Missing field: {field}"


def test_parse_kpoy_has_mvp_table(kpoy_page):
    """Verify KPOY parser extracts Game MVP leaders table."""
    result = parse_kpoy(kpoy_page)

    # Second table should be MVP leaders
    mvp_leaders = result[1]
    assert isinstance(mvp_leaders, list)
    assert len(mvp_leaders) > 0


# =============================================================================
# Test parse_point_distribution
# =============================================================================


def test_parse_point_distribution(point_dist_page):
    """Test parsing point distribution page."""
    result = parse_point_distribution(point_dist_page)

    assert isinstance(result, list)
    assert len(result) > 0

    first_team = result[0]
    assert first_team["Rank"] == "1"
    assert first_team["Team"] == "Duke"


def test_parse_point_distribution_has_scoring_breakdown(point_dist_page):
    """Verify point distribution has offensive scoring breakdown."""
    result = parse_point_distribution(point_dist_page)
    first_team = result[0]

    # Check for percentage and points fields for each shot type
    scoring_fields = ["2P", "3P", "FT"]
    for shot_type in scoring_fields:
        # At least one field should contain the shot type
        matching_fields = [key for key in first_team.keys() if shot_type in key]
        assert len(matching_fields) > 0, f"Missing fields for {shot_type}"


# =============================================================================
# Edge Case Tests
# =============================================================================


def test_parsers_handle_empty_table():
    """Test that parsers handle empty tables gracefully."""
    from bs4 import BeautifulSoup

    empty_html = "<html><body><table><thead><tr><th>Team</th></tr></thead><tbody></tbody></table></body></html>"
    soup = BeautifulSoup(empty_html, "lxml")

    # These should return empty lists, not crash
    assert parse_pomeroy_ratings(soup) == []
    assert parse_efficiency(soup) == []
    assert parse_four_factors(soup) == []
    assert parse_arenas(soup) == []
    assert parse_hca(soup) == []


def test_fanmatch_handles_missing_stats():
    """Test FanMatch parser handles missing daily stats."""
    from bs4 import BeautifulSoup

    minimal_html = """
    <html><body>
    <h2>Test Date</h2>
    <table><thead><tr><th>Game</th></tr></thead><tbody></tbody></table>
    </body></html>
    """
    soup = BeautifulSoup(minimal_html, "lxml")

    result = parse_fanmatch(soup)
    assert isinstance(result, dict)
    assert "date" in result
    assert "games" in result


def test_kpoy_handles_single_table():
    """Test KPOY parser handles pages with only one table."""
    from bs4 import BeautifulSoup

    single_table_html = """
    <html><body>
    <table><thead><tr><th>Player</th><th>Team</th></tr></thead>
    <tbody><tr><td>Player 1</td><td>Team 1</td></tr></tbody></table>
    </body></html>
    """
    soup = BeautifulSoup(single_table_html, "lxml")

    result = parse_kpoy(soup)
    assert isinstance(result, list)
    # Should return list with one table
    assert len(result) >= 1
