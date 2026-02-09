#!/usr/bin/env python3
"""
Debug script to test KenPom scraper and identify issues.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from kenpom_mcp.parsers.efficiency import parse_efficiency, parse_four_factors
from kenpom_mcp.scraper import KenPomScraper

# Load environment variables
load_dotenv()


async def main():
    email = os.getenv("KENPOM_EMAIL")
    password = os.getenv("KENPOM_PASSWORD")

    if not email or not password:
        print("❌ Missing KENPOM_EMAIL or KENPOM_PASSWORD in .env")
        return

    print(f"🔑 Using credentials: {email}")

    scraper = KenPomScraper(email, password)

    try:
        # Test login
        print("\n📡 Testing login...")
        await scraper.login()
        print("✅ Login successful!")

        # Test efficiency page
        print("\n📊 Fetching efficiency page (summary.php)...")
        efficiency_soup = await scraper.get_efficiency_page()

        # Save raw HTML for inspection
        debug_dir = Path("debug_output")
        debug_dir.mkdir(exist_ok=True)

        with open(debug_dir / "efficiency_raw.html", "w") as f:
            f.write(str(efficiency_soup))
        print(f"💾 Saved raw HTML to {debug_dir}/efficiency_raw.html")

        # Check for tables
        tables = efficiency_soup.find_all("table")
        print(f"📋 Found {len(tables)} table(s) on the page")

        if tables:
            print("\n🔍 First table structure:")
            first_table = tables[0]
            rows = first_table.find_all("tr")
            print(f"   - Total rows: {len(rows)}")

            if rows:
                headers = rows[0].find_all(["th", "td"])
                print(f"   - Headers: {[h.get_text(strip=True) for h in headers[:5]]}")
        else:
            print("\n⚠️  NO TABLES FOUND!")
            print("Checking for paywall/login indicators...")

            text = efficiency_soup.get_text()
            if "login" in text.lower():
                print("   - Page contains 'login' text (possible paywall)")
            if "subscribe" in text.lower():
                print("   - Page contains 'subscribe' text (possible paywall)")
            if "Logged in as" in text:
                print("   - Page shows 'Logged in as' (session is valid)")

            # Print first 500 chars of page
            print("\n📄 First 500 characters of page:")
            print(text[:500])

        # Try parsing
        print("\n🔬 Attempting to parse with parse_efficiency()...")
        try:
            results = parse_efficiency(efficiency_soup)
            print(f"✅ Parsed {len(results)} teams")
            if results:
                print(f"   Sample: {results[0]}")
        except Exception as e:
            print(f"❌ Parser error: {e}")

        # Test four factors page
        print("\n\n📊 Fetching four factors page (stats.php)...")
        ff_soup = await scraper.get_four_factors_page()

        with open(debug_dir / "four_factors_raw.html", "w") as f:
            f.write(str(ff_soup))
        print(f"💾 Saved raw HTML to {debug_dir}/four_factors_raw.html")

        tables = ff_soup.find_all("table")
        print(f"📋 Found {len(tables)} table(s) on the page")

        print("\n🔬 Attempting to parse with parse_four_factors()...")
        try:
            results = parse_four_factors(ff_soup)
            print(f"✅ Parsed {len(results)} teams")
            if results:
                print(f"   Sample: {results[0]}")
        except Exception as e:
            print(f"❌ Parser error: {e}")

        # Test ratings page (working one)
        print("\n\n📊 Fetching ratings page (index.php) as baseline...")
        ratings_soup = await scraper.get_ratings_page()
        tables = ratings_soup.find_all("table")
        print(f"📋 Found {len(tables)} table(s) on ratings page")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await scraper.close()
        print("\n🔒 Closed scraper")


if __name__ == "__main__":
    asyncio.run(main())
