from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import os
from pymongo import MongoClient, UpdateOne
import datetime


def _build_urls(league_path):
    """Build standings and fixtures URLs from footystats_link."""
    if league_path.startswith("http"):
        base = re.sub(r'(/fixtures|-fixtures)$', '', league_path)
        fixtures_url = league_path
        standings_url = base
    else:
        base = league_path.rstrip("/")
        fixtures_url = f"https://footystats.org/{base}/fixtures"
        standings_url = f"https://footystats.org/{base}"
    return standings_url, fixtures_url


def parse_standings(html, league_name):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody tr")
    if not rows:
        print(f"  [{league_name}] Standings cedveli tapilmadi.")
        return [], {}

    standings = []
    logo_map = {}
    for row in rows:
        try:
            rank_el = row.select_one("td.position span")
            rank = rank_el.text.strip() if rank_el else "0"

            team_el = row.select_one("td.team a")
            team_name = team_el.text.strip() if team_el else ""

            if not team_name or not team_name.strip():
                continue
            if not rank or not rank.isdigit():
                continue

            mp = row.select_one("td.mp")
            won = row.select_one("td.win")
            drawn = row.select_one("td.draw")
            lost = row.select_one("td.loss")
            gf = row.select_one("td.gf")
            ga = row.select_one("td.ga")
            gd = row.select_one("td.gd")
            pts = row.select_one("td.points")

            played = mp.text.strip() if mp else "0"
            wins = won.text.strip() if won else "0"
            draws = drawn.text.strip() if drawn else "0"
            losses = lost.text.strip() if lost else "0"
            goals_for = gf.text.strip() if gf else "0"
            goals_against = ga.text.strip() if ga else "0"
            goal_diff = gd.text.strip() if gd else "0"
            points = pts.text.strip() if pts else "0"

            form_items = []
            form_el = row.select_one("td.form")
            if form_el:
                form_ul = form_el.find("ul", class_="form-run")
                if form_ul:
                    for li in form_ul.find_all("li"):
                        a_tag = li.find("a", class_="form-run-box")
                        if a_tag:
                            text = a_tag.get_text(strip=True).upper()
                        else:
                            text = li.get_text(strip=True).upper()
                        if text in ("W", "D", "L"):
                            form_items.append(text)
                            if len(form_items) >= 5:
                                break

            team_logo = ""
            crest = row.select_one("td.crest img")
            if crest and crest.get("src"):
                team_logo = crest["src"]

            team_data = {
                "rank": rank,
                "team": team_name,
                "played": int(played) if played.isdigit() else 0,
                "won": int(wins) if wins.isdigit() else 0,
                "drawn": int(draws) if draws.isdigit() else 0,
                "lost": int(losses) if losses.isdigit() else 0,
                "goals_for": int(goals_for) if goals_for.isdigit() else 0,
                "goals_against": int(goals_against) if goals_against.isdigit() else 0,
                "goal_difference": goal_diff,
                "points": int(points) if points.isdigit() else 0,
                "last_games": form_items,
                "team_logo": team_logo,
            }
            standings.append(team_data)
            if team_logo:
                logo_map[team_name] = team_logo
        except Exception as e:
            print(f"  [{league_name}] Xeta (standings row): {e}")

    print(f"  [{league_name}] {len(standings)} komanda tapildi.")
    return standings, logo_map


def parse_fixtures(html, league_name):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", lambda c: c and "colgroup" in str(c).lower() if c else False)
    if not table:
        table = soup.find("table")

    match_uls = soup.find_all("ul", class_=lambda c: c and "match row cf" in c if c else False)
    if not match_uls and not table:
        print(f"  [{league_name}] Oyun tapilmadi.")
        return []

    fixtures = []
    seen_keys = set()

    for mu in match_uls:
        try:
            date_li = mu.find("li", class_="date")
            date_str = ""
            time_str = ""
            match_ts = None
            match_status = "incomplete"
            if date_li:
                ts_span = date_li.find("span", class_="timezone-convert-match-week")
                if ts_span and ts_span.get("data-time"):
                    match_ts = int(ts_span["data-time"])
                    dt = datetime.datetime.fromtimestamp(match_ts)
                    date_str = f"{dt.strftime('%A, %B')} {dt.day} {dt.strftime('%Y')}"
                    time_str = dt.strftime("%H:%M")
                status_span = date_li.find("span", class_=lambda c: c and "match-time-soon" in str(c) if c else False)
                if status_span:
                    match_status = status_span.get("data-match-status", "incomplete")
                else:
                    for s in date_li.find_all("span"):
                        if s.get("data-match-status") == "complete":
                            match_status = "complete"
                            break

            info_li = mu.find("li", class_="match-info")
            if not info_li:
                continue

            home_a = info_li.find("a", class_=lambda c: c and "team home" in str(c) if c else False)
            away_a = info_li.find("a", class_=lambda c: c and "team away" in str(c) if c else False)
            if not home_a or not away_a:
                continue

            h_name_span = home_a.find("span", class_="hover-modal-parent hover-modal-ajax-team")
            a_name_span = away_a.find("span", class_="hover-modal-parent hover-modal-ajax-team")
            home_name = h_name_span.text.strip() if h_name_span else ""
            away_name = a_name_span.text.strip() if a_name_span else ""

            h2h_link = info_li.find("a", class_=lambda c: c and "h2h-link" in str(c) if c else False)
            score = ""
            if h2h_link:
                score_span = h2h_link.find("span", class_="ft-score")
                if score_span:
                    score = score_span.text.strip()

            odds_li = mu.find("li", class_="match-stats")
            home_odds = ""
            draw_odds = ""
            away_odds = ""
            if odds_li:
                odds_spans = odds_li.find_all("span", class_=lambda c: c and "col-lg-4" in str(c) if c else False)
                if len(odds_spans) >= 3:
                    home_odds = odds_spans[0].get_text(strip=True)
                    draw_odds = odds_spans[1].get_text(strip=True)
                    away_odds = odds_spans[2].get_text(strip=True)

            key = (home_name, away_name, date_str)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            fixtures.append({
                "date": date_str,
                "time": time_str,
                "home_team": home_name,
                "away_team": away_name,
                "score": score,
                "match_status": match_status,
                "timestamp": match_ts,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
            })
        except Exception as e:
            print(f"  [{league_name}] Xeta (fixture row): {e}")

    print(f"  [{league_name}] {len(fixtures)} oyun tapildi.")
    return fixtures


def save_standings_to_mongodb(data, league_name, league_id=None):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        collection = db["standings"]
        timestamp = datetime.datetime.now()
        ops = []
        for doc in data:
            doc["league_name"] = league_name
            doc["updated_at"] = timestamp
            ops.append(UpdateOne(
                {"team": doc["team"], "league_name": league_name},
                {"$set": doc},
                upsert=True
            ))
        if ops:
            collection.bulk_write(ops)
            print(f"  [{league_name}] {len(ops)} komanda standings-e yazildi.")

        if league_id:
            teams_col = db["teams"]
            updated = 0
            for doc in data:
                logo = doc.get("team_logo", "")
                team_name = doc.get("team", "")
                if logo and team_name:
                    result = teams_col.update_one(
                        {"name": team_name, "league_id": league_id, "logo": {"$in": ["", None]}},
                        {"$set": {"logo": logo}}
                    )
                    if result.modified_count:
                        updated += 1
            if updated:
                print(f"  [{league_name}] {updated} komandanin logosu teams-e yazildi.")

        client.close()
    except Exception as e:
        print(f"  [{league_name}] MongoDB xetasi (standings): {e}")


def save_fixtures_to_mongodb(data, league_name, valid_dates):
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        collection = db["fixtures"]
        timestamp = datetime.datetime.now()

        filtered = [g for g in data if g.get("date", "") in valid_dates]

        collection.delete_many({"league_name": league_name})
        docs = []
        for g in filtered:
            docs.append({
                "league_name": league_name,
                "group_name": league_name,
                "date": g.get("date", ""),
                "time": g.get("time", ""),
                "home_team": g.get("home_team", ""),
                "away_team": g.get("away_team", ""),
                "score": g.get("score", ""),
                "match_status": g.get("match_status", ""),
                "timestamp": g.get("timestamp"),
                "home_odds": g.get("home_odds", ""),
                "draw_odds": g.get("draw_odds", ""),
                "away_odds": g.get("away_odds", ""),
                "updated_at": timestamp,
            })
        if docs:
            collection.insert_many(docs)
            print(f"  [{league_name}] {len(docs)} oyun fixtures-e yazildi (bugun/sabah).")
        else:
            print(f"  [{league_name}] Bugun/sabah ucun oyun yoxdur.")
        client.close()
    except Exception as e:
        print(f"  [{league_name}] MongoDB xetasi (fixtures): {e}")


def _get_valid_dates():
    result = []
    for delta in [0, 1]:
        d = datetime.datetime.now() + datetime.timedelta(days=delta)
        result.append(f"{d.strftime('%A, %B')} {d.day} {d.strftime('%Y')}")
    return result


def scrape_league(league_name, standings_url, fixtures_url, driver, league_id=None):
    print(f"\n=== {league_name} ===")

    # --- STANDINGS ---
    print(f"  Standings yuklenir: {standings_url}")
    driver.get(standings_url)
    time.sleep(3)
    standings_data, logo_map = parse_standings(driver.page_source, league_name)
    if standings_data:
        save_standings_to_mongodb(standings_data, league_name, league_id)
    else:
        print(f"  [{league_name}] Standings tapilmadi.")

    # --- FIXTURES ---
    print(f"  Fixtures yuklenir: {fixtures_url}")
    driver.get(fixtures_url)
    time.sleep(3)
    fixtures_data = parse_fixtures(driver.page_source, league_name)
    valid_dates = _get_valid_dates()
    print(f"  Yalniz bugun ve sabah filtirlenir: {valid_dates}")
    save_fixtures_to_mongodb(fixtures_data, league_name, valid_dates)


def _load_leagues():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        configs = list(db["leagues_config"].find({"footystats_link": {"$ne": ""}}))
        client.close()
        if configs:
            return [{"name": c["name"], "footystats_link": c["footystats_link"], "league_id": str(c["_id"])} for c in configs]
    except Exception as e:
        print(f"DB'den liqa melumatlari yuklenemedi: {e}")
    return None


def scrape_all():
    print("[FootyStatsGames] Basladi - standings + fixtures Footystats-dan.")

    leagues = _load_leagues()
    if not leagues:
        print("[FootyStatsGames] Footystats linki olan liqa tapilmadi.")
        return

    service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for league in leagues:
            try:
                standings_url, fixtures_url = _build_urls(league["footystats_link"])
                scrape_league(league["name"], standings_url, fixtures_url, driver, league.get("league_id"))
            except Exception as e:
                print(f"[{league['name']}] Xeta: {e}")
    finally:
        driver.quit()

    print("\n[FootyStatsGames] Tamamlandi.")


if __name__ == "__main__":
    scrape_all()
