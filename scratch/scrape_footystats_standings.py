"""
Hər liqanın footystats.org liqa cədvəlinə gedir,
komanda adı, loqo və sırasını JSON fayla yazır.
DB-yə heç nə yazmır.

İstifadə: python scratch/scrape_footystats_standings.py
"""

import os
import sys
import json
import time
import re

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pymongo import MongoClient
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "football_prediction"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "footystats_data")


def scrape_league_table(driver, url):
    driver.get(url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table", class_="full-league-table")
    if not table:
        print(f"  Table not found")
        return []

    tbody = table.find("tbody")
    if not tbody:
        print(f"  tbody not found")
        return []

    teams = []
    rows = tbody.find_all("tr")
    for row in rows:
        pos_el = row.find("td", class_="position")
        position = pos_el.find("span").text.strip() if pos_el and pos_el.find("span") else ""

        team_el = row.find("td", class_="team")
        name = team_el.find("a").text.strip() if team_el and team_el.find("a") else ""

        crest_el = row.find("td", class_="crest")
        logo = crest_el.find("img")["src"] if crest_el and crest_el.find("img") else ""

        if name:
            teams.append({
                "position": int(position) if position.isdigit() else 0,
                "name": name,
                "logo": logo,
            })

    return teams


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    leagues = list(db.leagues_config.find({"footystats_link": {"$ne": ""}}))
    client.close()

    if not leagues:
        print("No leagues found.")
        return

    print(f"Found {len(leagues)} leagues")

    opts = uc.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=opts, version_main=148)

    all_data = {}

    try:
        for league in leagues:
            league_path = league.get("footystats_link", "")
            league_name = league.get("name", "")
            league_id = str(league.get("_id"))

            if not league_path or not league_name:
                continue

            url = league_path.rstrip("/")
            if url.endswith("/fixtures"):
                url = url[:-9]

            print(f"\n=== {league_name} ===")
            print(f"  URL: {url}")

            try:
                teams = scrape_league_table(driver, url)
                print(f"  Found {len(teams)} teams")

                all_data[league_name] = {
                    "league_id": league_id,
                    "name": league_name,
                    "url": url,
                    "teams": teams,
                }

                # Save per-league file
                safe_name = re.sub(r"[^a-z0-9]", "_", league_name.lower())
                filepath = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(all_data[league_name], f, indent=2, ensure_ascii=False)
                print(f"  Saved: {filepath}")

                time.sleep(1)

            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
    finally:
        driver.quit()

    # Save all data in one file
    all_filepath = os.path.join(OUTPUT_DIR, "all_leagues.json")
    with open(all_filepath, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"\nAll data saved: {all_filepath}")
    print(f"League files: {OUTPUT_DIR}/")
    print("Done!")


if __name__ == "__main__":
    main()
