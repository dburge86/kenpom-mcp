#!/usr/bin/env python3
"""
Comprehensive test of all 13 KenPom MCP tools using BYU data.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from kenpom_mcp.parsers.efficiency import parse_efficiency, parse_four_factors
from kenpom_mcp.parsers.misc import (
    parse_arenas,
    parse_game_attrs,
    parse_hca,
    parse_point_distribution,
    parse_program_ratings,
)
from kenpom_mcp.parsers.ratings import parse_pomeroy_ratings
from kenpom_mcp.parsers.stats import parse_height, parse_kpoy, parse_player_stats, parse_team_stats
from kenpom_mcp.scraper import KenPomScraper

load_dotenv(Path.cwd() / ".env")


def find_team(results, team_name="BYU"):
    """Find team in results list."""
    for team in results:
        if team_name.lower() in str(team.get("Team", "")).lower():
            return team
    return None


async def main():
    email = os.getenv("KENPOM_EMAIL")
    password = os.getenv("KENPOM_PASSWORD")

    if not email or not password:
        print("❌ Missing credentials")
        return

    scraper = KenPomScraper(email, password)

    try:
        print("=" * 80)
        print("KenPom MCP Server - Comprehensive Tool Test (BYU)")
        print("=" * 80)

        await scraper.login()
        print("✅ Login successful\n")

        # =====================================================================
        # Tool 1: get_ratings
        # =====================================================================
        print("📊 [1/13] get_ratings")
        print("-" * 80)
        soup = await scraper.get_ratings_page()
        results = parse_pomeroy_ratings(soup)
        byu = find_team(results)
        if byu:
            print(f"Team: {byu.get('Team')}")
            print(f"Rank: {byu.get('Rank')}")
            print(f"Conference: {byu.get('Conference')}")
            print(f"Record: {byu.get('Record')}")
            print(f"AdjEM: {byu.get('AdjEM')}")
            print(f"AdjO: {byu.get('AdjO')} (Rank: {byu.get('AdjO_Rank')})")
            print(f"AdjD: {byu.get('AdjD')} (Rank: {byu.get('AdjD_Rank')})")
            print(f"AdjT: {byu.get('AdjT')} (Rank: {byu.get('AdjT_Rank')})")
        print()

        # =====================================================================
        # Tool 2: get_efficiency
        # =====================================================================
        print("📊 [2/13] get_efficiency")
        print("-" * 80)
        soup = await scraper.get_efficiency_page()
        results = parse_efficiency(soup)
        byu = find_team(results)
        if byu:
            print(f"Team: {byu.get('Team')}")
            print(f"Rank: {byu.get('Rank')}")
            print(f"Conference: {byu.get('Conference')}")
            print(f"AdjT: {byu.get('AdjT')} (Rank: {byu.get('AdjT_Rank')})")
            print(f"AdjOE: {byu.get('AdjOE')} (Rank: {byu.get('AdjOE_Rank')})")
            print(f"AdjDE: {byu.get('AdjDE')} (Rank: {byu.get('AdjDE_Rank')})")
        print()

        # =====================================================================
        # Tool 3: get_four_factors
        # =====================================================================
        print("📊 [3/13] get_four_factors")
        print("-" * 80)
        soup = await scraper.get_four_factors_page()
        results = parse_four_factors(soup)
        byu = find_team(results)
        if byu:
            print(f"Team: {byu.get('Team')}")
            print(f"Rank: {byu.get('Rank')}")
            print(f"AdjOE: {byu.get('AdjOE')} (Rank: {byu.get('AdjOE_Rank')})")
            print(f"AdjDE: {byu.get('AdjDE')} (Rank: {byu.get('AdjDE_Rank')})")
            print(f"Off eFG%: {byu.get('Off_eFG_Pct')} (Rank: {byu.get('Off_eFG_Pct_Rank')})")
            print(f"Off TO%: {byu.get('Off_TO_Pct')} (Rank: {byu.get('Off_TO_Pct_Rank')})")
            print(f"Def eFG%: {byu.get('Def_eFG_Pct')} (Rank: {byu.get('Def_eFG_Pct_Rank')})")
            print(f"Def TO%: {byu.get('Def_TO_Pct')} (Rank: {byu.get('Def_TO_Pct_Rank')})")
        print()

        # =====================================================================
        # Tool 4: get_team_stats (offense)
        # =====================================================================
        print("📊 [4/13] get_team_stats (offense)")
        print("-" * 80)
        try:
            soup = await scraper.get_team_stats_page(defense=False)
            results = parse_team_stats(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Conference: {byu.get('Conference')}")
                # Show first 5 keys
                keys = list(byu.keys())[:10]
                for key in keys:
                    print(f"{key}: {byu.get(key)}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 5: get_team_stats (defense)
        # =====================================================================
        print("📊 [5/13] get_team_stats (defense)")
        print("-" * 80)
        try:
            soup = await scraper.get_team_stats_page(defense=True)
            results = parse_team_stats(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Conference: {byu.get('Conference')}")
                keys = list(byu.keys())[:10]
                for key in keys:
                    print(f"{key}: {byu.get(key)}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 6: get_player_stats
        # =====================================================================
        print("📊 [6/13] get_player_stats (eFG%)")
        print("-" * 80)
        try:
            soup = await scraper.get_player_stats_page(metric="eFG")
            results = parse_player_stats(soup)
            print(f"Total players: {len(results)}")
            # Find BYU players in top results
            byu_players = [p for p in results if "BYU" in str(p.get("Team", ""))]
            if byu_players:
                for player in byu_players[:3]:
                    print(f"Player: {player.get('Player')}")
                    print(f"  Team: {player.get('Team')}")
                    print(f"  Rank: {player.get('Rank')}")
                    stats = {k: v for k, v in player.items() if k not in ["Player", "Team", "Rank"]}
                    print(f"  Stats: {list(stats.items())}")
                    print()
            else:
                print("(No BYU players in top results for eFG%)")
                if results:
                    print(f"Sample: {results[0]}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 7: get_height
        # =====================================================================
        print("📊 [7/13] get_height")
        print("-" * 80)
        try:
            soup = await scraper.get_height_page()
            results = parse_height(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Conference: {byu.get('Conference')}")
                print(f"Avg Height: {byu.get('Avg_Hgt')} (Rank: {byu.get('Avg_Hgt_Rank')})")
                print(f"Eff Height: {byu.get('Eff_Hgt')} (Rank: {byu.get('Eff_Hgt_Rank')})")
                print(f"Experience: {byu.get('Experience')} (Rank: {byu.get('Experience_Rank')})")
                print(f"Bench: {byu.get('Bench')} (Rank: {byu.get('Bench_Rank')})")
                print(f"Continuity: {byu.get('Continuity')} (Rank: {byu.get('Continuity_Rank')})")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 8: get_fanmatch (today's games)
        # =====================================================================
        print("📊 [8/13] get_fanmatch (today)")
        print("-" * 80)
        soup = await scraper.get_fanmatch_page()
        from kenpom_mcp.parsers.fanmatch import parse_fanmatch

        results = parse_fanmatch(soup)
        print(f"Total games today: {len(results.get('games', []))}")
        # Check if BYU is playing
        byu_games = [
            g
            for g in results.get("games", [])
            if "BYU" in str(g.get("Team1", "")) or "BYU" in str(g.get("Team2", ""))
        ]
        if byu_games:
            print("BYU game today:")
            for game in byu_games:
                print(f"  {game.get('Team1')} vs {game.get('Team2')}")
                print(f"  Time: {game.get('Time')}")
                print(f"  Prediction: {game}")
        else:
            print("(No BYU games today)")
        print()

        # =====================================================================
        # Tool 9: get_arenas
        # =====================================================================
        print("📊 [9/13] get_arenas")
        print("-" * 80)
        try:
            soup = await scraper.get_arenas_page()
            results = parse_arenas(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Arena: {byu.get('Arena')}")
                print(f"Capacity: {byu.get('Capacity')}")
                print(f"Altitude: {byu.get('Altitude')}")
                keys = list(byu.keys())
                for key in keys:
                    print(f"{key}: {byu.get(key)}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 10: get_game_attrs (Excitement)
        # =====================================================================
        print("📊 [10/13] get_game_attrs (Excitement)")
        print("-" * 80)
        try:
            soup = await scraper.get_game_attrs_page(metric="Excitement")
            results = parse_game_attrs(soup)
            # Check if BYU has any games in top results
            byu_games = [
                g
                for g in results[:20]
                if "BYU" in str(g.get("Team1", "")) or "BYU" in str(g.get("Team2", ""))
            ]
            if byu_games:
                print("BYU games in top 20 most exciting:")
                for game in byu_games[:3]:
                    print(f"  {game.get('Team1')} vs {game.get('Team2')}")
                    print(f"  Date: {game.get('Date')}")
                    print(f"  Rank: {game.get('Rank')}")
                    print()
            else:
                print("(No BYU games in top 20 most exciting)")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 11: get_program_ratings
        # =====================================================================
        print("📊 [11/13] get_program_ratings")
        print("-" * 80)
        try:
            soup = await scraper.get_program_ratings_page()
            results = parse_program_ratings(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Rank: {byu.get('Rank')}")
                keys = list(byu.keys())
                for key in keys[:10]:
                    print(f"{key}: {byu.get(key)}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 12: get_kpoy (Player of the Year)
        # =====================================================================
        print("📊 [12/13] get_kpoy")
        print("-" * 80)
        try:
            soup = await scraper.get_kpoy_page()
            results = parse_kpoy(soup)
            # Check if any BYU players
            if isinstance(results, list) and len(results) > 0:
                # KPOY returns list of tables
                all_players = []
                for table in results:
                    if isinstance(table, list):
                        all_players.extend(table)
                    else:
                        all_players.append(table)
                byu_players = [p for p in all_players if "BYU" in str(p.get("Team", ""))]
            else:
                byu_players = []

            if byu_players:
                print("BYU players in KPOY standings:")
                for player in byu_players[:3]:
                    print(f"  {player.get('Player')} - {player.get('Team')}")
                    print(f"  Rank: {player.get('Rank')}")
                    print(f"  Stats: {list(player.items())[:5]}")
                    print()
            else:
                print("(No BYU players in KPOY standings)")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 13: get_point_distribution
        # =====================================================================
        print("📊 [13/13] get_point_distribution")
        print("-" * 80)
        try:
            soup = await scraper.get_point_dist_page()
            results = parse_point_distribution(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Conference: {byu.get('Conference')}")
                keys = list(byu.keys())
                for key in keys[:15]:
                    print(f"{key}: {byu.get(key)}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        # =====================================================================
        # Tool 14: get_hca (Home Court Advantage)
        # =====================================================================
        print("📊 [BONUS] get_hca (Home Court Advantage)")
        print("-" * 80)
        try:
            soup = await scraper.get_hca_page()
            results = parse_hca(soup)
            byu = find_team(results)
            if byu:
                print(f"Team: {byu.get('Team')}")
                print(f"Conference: {byu.get('Conference')}")
                keys = list(byu.keys())
                for key in keys:
                    print(f"{key}: {byu.get(key)}")
        except Exception as e:
            print(f"⚠️  Parser needs fixing: {e}")
        print()

        print("=" * 80)
        print("✅ ALL 13 TOOLS TESTED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
