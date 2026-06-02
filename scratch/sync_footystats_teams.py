"""
1. standings kolleksiyasından komandaları teams-ə yazır
2. footystats.org liqa cədvəlini qaşıyır
3. ADLA (fuzzy search) uyğunlaşdırır
4. footystats adını alias-a əlavə edir, loqonu yeniləyir

İstifadə: python scratch/sync_footystats_teams.py
"""

import os
import sys
import time
import re
import difflib
import unicodedata

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


def norm(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).lower())


def fuzzy_score(a, b):
    na, nb = norm(a), norm(b)
    if na in nb or nb in na:
        return 1.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


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
            teams.append({"name": name, "logo": logo})

    return teams


def find_best_match(db, fs_name, league_id):
    """Find best matching team by name, alias, or fuzzy."""
    all_teams = list(db.teams.find({"league_id": league_id}))
    best, best_score = None, 0.0

    for t in all_teams:
        candidates = [t["name"]] + (t.get("aliases") or [])
        for c in candidates:
            score = fuzzy_score(fs_name, c)
            if score > best_score:
                best_score = score
                best = t

    if best_score >= 0.7:
        return best
    return None


def sync_league(league, driver):
    league_path = league.get("footystats_link", "")
    league_id = str(league.get("_id"))
    league_name = league.get("name", "")

    if not league_path or not league_id or not league_name:
        return

    url = league_path.rstrip("/")
    if url.endswith("/fixtures"):
        url = url[:-9]

    print(f"\n=== {league_name} ===")

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    standings = list(db.standings.find({"league_name": league_name}).sort("rank", 1))
    if not standings:
        print(f"  No standings found, skipping")
        client.close()
        return

    synced = 0
    for st in standings:
        st_name = st.get("team", "")
        if st_name and not db.teams.find_one({"name": st_name, "league_id": league_id}):
            db.teams.insert_one({"name": st_name, "league_id": league_id, "logo": "", "aliases": []})
            synced += 1
    print(f"  Standings: {len(standings)} teams" + (f" (synced {synced})" if synced else ""))

    fs_teams = scrape_league_table(driver, url)
    if not fs_teams:
        client.close()
        return

    print(f"  Footystats: {len(fs_teams)} teams")

    aliases_added = 0
    logos_updated = 0
    created = 0
    matched = 0

    for fs in fs_teams:
        fs_name = fs["name"]
        fs_logo = fs["logo"]

        existing = db.teams.find_one({"name": fs_name, "league_id": league_id})
        if not existing:
            existing = db.teams.find_one({"aliases": fs_name, "league_id": league_id})
        if not existing:
            existing = find_best_match(db, fs_name, league_id)

        if existing:
            update = {}
            aliases_set = set(existing.get("aliases") or [])
            if fs_name not in aliases_set:
                aliases_set.add(fs_name)
                update["aliases"] = list(aliases_set)
                aliases_added += 1
            if fs_logo and not existing.get("logo"):
                update["logo"] = fs_logo
                logos_updated += 1
            if update:
                db.teams.update_one({"_id": existing["_id"]}, {"$set": update})
            matched += 1
        else:
            db.teams.insert_one({
                "name": fs_name,
                "league_id": league_id,
                "logo": fs_logo,
                "aliases": [fs_name],
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            })
            created += 1

    client.close()
    print(f"  Matched: {matched}, Created: {created}, Aliases added: {aliases_added}, Logos updated: {logos_updated}")


def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    leagues = list(db.leagues_config.find({"footystats_link": {"$ne": ""}, "name": {"$ne": ""}}))
    client.close()

    if not leagues:
        print("No leagues found.")
        return

    print(f"Found {len(leagues)} leagues")

    opts = uc.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=opts, version_main=148)

    try:
        for league in leagues:
            try:
                sync_league(league, driver)
                time.sleep(1)
            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
    finally:
        driver.quit()

    print("\nDone!")


if __name__ == "__main__":
    main()
