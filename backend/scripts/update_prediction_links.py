import re
import time
import random
import unicodedata
import os
import difflib
from pymongo import MongoClient
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from datetime import datetime, timedelta

def get_today_tomorrow_dates():
    """Returns date strings for today and tomorrow in DB format: 'Monday, May 12 2026'"""
    result = []
    for delta in [0, 1]:
        d = datetime.now() + timedelta(days=delta)
        result.append(f"{d.strftime('%A, %B')} {d.day} {d.strftime('%Y')}")
    return result

# Config
DB_NAME = "football_prediction"
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

# Dynamic league config loaded in functions


def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_text(text):
    if not text: return ""
    text = remove_accents(text).lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def _strip_suffixes(name):
    suffixes = ["fc", "sc", "cf", "fk", "afc", "ud", "cd", "united", "city", "real", "club", "deportivo"]
    for s in suffixes:
        if name.endswith(s):
            name = name[:-len(s)]
    return name

def fuzzy_match(name1, name2, is_team=False, threshold=0.7):
    n1 = normalize_text(name1)
    n2 = normalize_text(name2)
    if n1 in n2 or n2 in n1:
        return True
        
    if is_team:
        s1 = _strip_suffixes(n1)
        s2 = _strip_suffixes(n2)
        if s1 in s2 or s2 in s1:
            return True
        ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
        return ratio >= threshold
        
    return False

# ---- Central alias system ----
_ALIAS_MAP = {}
_ALIAS_LOADED = False

def _ensure_alias_map():
    global _ALIAS_MAP, _ALIAS_LOADED
    if _ALIAS_LOADED:
        return
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        _ALIAS_MAP.clear()
        for team in db.teams.find({}, {"name": 1, "aliases": 1}):
            name = team.get("name")
            if name:
                _ALIAS_MAP[name] = name
                for alias in team.get("aliases", []):
                    if alias:
                        _ALIAS_MAP[alias] = name
        client.close()
        print(f"[Links] Loaded {len(_ALIAS_MAP)} team aliases from DB")
    except Exception as e:
        print(f"[Links] Alias load error: {e}")
    _ALIAS_LOADED = True

def resolve_team_name(name):
    if not name:
        return name
    _ensure_alias_map()
    if name in _ALIAS_MAP:
        return _ALIAS_MAP[name]
    norm = normalize_text(name)
    for alias, canonical in _ALIAS_MAP.items():
        if normalize_text(alias) == norm:
            return canonical
    return name

def _cleanup_stale_chromedriver():
    import glob
    ucd_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'appdata', 'roaming', 'undetected_chromedriver')
    exe_path = os.path.join(ucd_dir, 'undetected_chromedriver.exe')
    if os.path.exists(exe_path):
        for _ in range(3):
            try:
                os.remove(exe_path)
                break
            except:
                time.sleep(0.5)

def _safe_quit_driver(d):
    if d is None:
        return
    try:
        d.close()
    except:
        pass
    try:
        d.quit()
    except:
        pass
    try:
        d.service.process = None
    except:
        pass


# --- SCRAPING FUNCTIONS ---

def update_wincomparator(driver, db):
    print("\n" + "="*30)
    print("STEP 2: WINCOMPARATOR")
    print("="*30)
    _ensure_alias_map()
    leagues_config = list(db.leagues_config.find({"wincomparator_link": {"$ne": ""}}))
    valid_dates = get_today_tomorrow_dates()
    for league in leagues_config:
        league_name = league.get("name")
        league_path = league.get("wincomparator_link")
        if not league_path: continue

        fixtures = list(db.fixtures.find({"league_name": league_name, "date": {"$in": valid_dates}}))
        if not fixtures:
            print(f"  [{league_name}] Bugun/sabah ucun fixture yoxdur, kecilir.")
            continue
        
        url = league_path if league_path.startswith("http") else f"https://www.wincomparator.com/predictions/football/{league_path}"
        driver.get(url)
        time.sleep(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try old layout (border-b-secondary-gray containers) first, then new layout (a.w-full with team spans)
        match_containers = soup.find_all("div", class_=lambda c: c and "border-b-secondary-gray" in c)
        
        if not match_containers:
            # New layout: find all a.w-full that contain team name spans
            for link_tag in soup.find_all("a", class_="w-full"):
                team_spans = link_tag.find_all("span", class_=lambda c: c and "text-primary-darkblue" in c and "leading-5" in c)
                if len(team_spans) >= 2:
                    match_containers.append(link_tag)
        
        updated = 0
        for container in match_containers:
            link_tag = container if container.name == "a" else container.find("a", class_="w-full")
            if not link_tag: continue
            
            team_spans = link_tag.find_all("span", class_=lambda c: c and "text-primary-darkblue" in c and "leading-5" in c)
            if len(team_spans) < 2: continue
            
            home_name_raw = team_spans[0].get_text(strip=True)
            away_name_raw = team_spans[1].get_text(strip=True)
            home_name = resolve_team_name(home_name_raw)
            away_name = resolve_team_name(away_name_raw)
            href = link_tag.get("href")
            
            for f in fixtures:
                db_home = resolve_team_name(f["home_team"])
                db_away = resolve_team_name(f["away_team"])
                if fuzzy_match(db_home, home_name, is_team=True) and fuzzy_match(db_away, away_name, is_team=True):
                    db.fixtures.update_one({"_id": f["_id"]}, {"$set": {
                        "predictions.wincomparator_link": f"https://www.wincomparator.com{href}"
                    }})
                    updated += 1
                    break
        print(f"  [{league_name}] Updated: {updated}")

def update_oddslot(driver, db):
    print("\n" + "="*30)
    print("STEP 3: ODDSLOT")
    print("="*30)
    _ensure_alias_map()
    valid_dates = get_today_tomorrow_dates()
    
    # Early exit check
    if db.fixtures.count_documents({"date": {"$in": valid_dates}}) == 0:
        print("[Oddslot] Bugun/sabah ucun hecbir fixture tapilmadi. Scraper dayandirilir.")
        return

    for i, day in enumerate(["today", "tomorrow"]):
        date_db = valid_dates[i]
        if db.fixtures.count_documents({"date": date_db}) == 0:
            print(f"[Oddslot] {date_db} tarixi ucun fixture yoxdur, atlanir.")
            continue

        url = f"https://oddslot.com/odds/?day={day}"
        driver.get(url)
        time.sleep(15)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        league_blocks = soup.find_all("div", class_="drop-league")
        
        updated = 0
        for block in league_blocks:
            header = block.find(class_="drop-league__header")
            if not header: continue
            
            raw_title = header.get_text(strip=True)
            # Normalize raw_title: strip count from end, strip whitespace
            raw_title_clean = raw_title.rsplit("(", 1)[0].strip()
            
            leagues_config = list(db.leagues_config.find({}))
            matched_db_league = None
            for l in leagues_config:
                l_name = l.get("name", "")
                odd_name = l.get("oddslot_link", "")
                if not odd_name:
                    continue
                # Normalize both for comparison
                n_oddslot = normalize_text(odd_name)
                n_raw = normalize_text(raw_title_clean)
                # Prefer exact full-title match (e.g. "Belarus:Premier League" -> "Belarus:Premier League")
                if n_oddslot == n_raw:
                    matched_db_league = l_name
                    break
                # Also try matching just the league part (after colon) if no exact match
                # This handles cases where oddslot_link has extra spaces vs raw_title
                odd_league = raw_title_clean.split(":")[1].strip() if ":" in raw_title_clean else raw_title_clean
                n_league = normalize_text(odd_league)
                if n_oddslot == n_league:
                    matched_db_league = l_name
                    break

            if not matched_db_league: continue
            
            db_fixtures = list(db.fixtures.find({"league_name": matched_db_league, "date": {"$in": valid_dates}}))
            match_rows = block.find_all("div", class_="odds-match")
            
            for row in match_rows:
                home_tag = row.find("a", class_="odds-match__team--home")
                away_tag = row.find("a", class_="odds-match__team--away")
                if not home_tag or not away_tag: continue
                
                h_name = home_tag.get_text(strip=True)
                a_name = away_tag.get_text(strip=True)
                link = home_tag.get("href")
                
                # Extract percentage chances
                chance_spans = row.find_all("span", class_="odds-match__chance")
                home_chance = chance_spans[0].get_text(strip=True).replace('%', '') if len(chance_spans) > 0 else ""
                away_chance = chance_spans[1].get_text(strip=True).replace('%', '') if len(chance_spans) > 1 else ""
                
                h_name_resolved = resolve_team_name(h_name)
                a_name_resolved = resolve_team_name(a_name)

                for f in db_fixtures:
                    db_home = resolve_team_name(f["home_team"])
                    db_away = resolve_team_name(f["away_team"])
                    if fuzzy_match(db_home, h_name_resolved, is_team=True) and fuzzy_match(db_away, a_name_resolved, is_team=True):
                        update_doc = {
                            "predictions.oddslot_link": f"https://oddslot.com{link}"
                        }
                        if home_chance: update_doc["predictions.oddslot_home_chance"] = home_chance
                        if away_chance: update_doc["predictions.oddslot_away_chance"] = away_chance
                        
                        db.fixtures.update_one({"_id": f["_id"]}, {"$set": update_doc})
                        updated += 1
                        break
        print(f"  [{day.upper()}] Updated: {updated}")

def update_betimate(driver, db):
    print("\n" + "="*30)
    print("STEP 4: BETIMATE")
    print("="*30)
    valid_dates = get_today_tomorrow_dates()
    
    # Early exit check
    if db.fixtures.count_documents({"date": {"$in": valid_dates}}) == 0:
        print("[Betimate] Bugun/sabah ucun hecbir fixture tapilmadi. Scraper dayandirilir.")
        return

    _ensure_alias_map()

    leagues_config = list(db.leagues_config.find({"betimate_link": {"$ne": ""}}))
    if not leagues_config:
        print("[Betimate] Hecbir liqa ucun betimate_link tapilmadi. Atlanir.")
        return

    for league in leagues_config:
        league_name = league.get("name")
        league_path = league.get("betimate_link")
        
        # Check if we have fixtures for this league
        league_fixtures = list(db.fixtures.find({"league_name": league_name, "date": {"$in": valid_dates}}))
        if not league_fixtures:
            print(f"  [{league_name}] Bugun/sabah ucun fixture yoxdur, atlanir.")
            continue

        url = league_path if league_path.startswith("http") else f"https://betimate.com/en/football-predictions/{league_path}"
        print(f"  [{league_name}] Scraping: {url}")
        driver.get(url)
        time.sleep(12)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tables = soup.find_all("div", class_="predictions-table")
        
        updated = 0
        for table in tables:
            rows = table.find_all("div", class_="prediction-body")
            for row in rows:
                h_tag = row.find("div", class_="homeTeam")
                a_tag = row.find("div", class_="awayTeam")
                l_tag = row.find("a", class_="sports-team")
                if not h_tag or not a_tag or not l_tag: continue
                
                h_name = h_tag.get_text(strip=True)
                a_name = a_tag.get_text(strip=True)
                link = l_tag.get("href")
                
                # Extract probabilities
                prob_div = row.find("div", class_="probability")
                p_win = p_draw = p_lost = ""
                if prob_div:
                    win_div = prob_div.find("div", class_="predict-win")
                    draw_div = prob_div.find("div", class_="predict-draw")
                    lost_div = prob_div.find("div", class_="predict-lost")
                    p_win = win_div.get_text(strip=True) if win_div else ""
                    p_draw = draw_div.get_text(strip=True) if draw_div else ""
                    p_lost = lost_div.get_text(strip=True) if lost_div else ""
                
                # Extract predicted score
                score_div = row.find("div", class_="score")
                pred_score = score_div.get_text(strip=True) if score_div else ""
                
                h_name_resolved = resolve_team_name(h_name)
                a_name_resolved = resolve_team_name(a_name)

                for f in league_fixtures:
                    db_home = resolve_team_name(f["home_team"])
                    db_away = resolve_team_name(f["away_team"])
                    if fuzzy_match(db_home, h_name_resolved, is_team=True) and fuzzy_match(db_away, a_name_resolved, is_team=True):
                        update_doc = {
                            "predictions.betimate_link": link,
                            "predictions.betimate_home_win": p_win,
                            "predictions.betimate_draw": p_draw,
                            "predictions.betimate_away_win": p_lost,
                            "predictions.betimate_score": pred_score
                        }
                        db.fixtures.update_one({"_id": f["_id"]}, {"$set": update_doc})
                        updated += 1
                        break
        print(f"  [{league_name}] Updated: {updated}")

def update_sportsgambler(driver, db):
    print("\n" + "="*30)
    print("STEP 5: SPORTSGAMBLER")
    print("="*30)
    _ensure_alias_map()
    valid_dates = get_today_tomorrow_dates()
    
    # Early exit check
    if db.fixtures.count_documents({"date": {"$in": valid_dates}}) == 0:
        print("[SportsGambler] Bugun/sabah ucun hecbir fixture tapilmadi. Scraper dayandirilir.")
        return
        
    leagues_config = list(db.leagues_config.find({"sportsgambler_link": {"$ne": ""}}))
    if not leagues_config:
        print("  [!] No sportsgambler links found in leagues_config. Atlanir.")
        return
    
    updated_total = 0
    for league in leagues_config:
        league_name = league.get("name")
        url = league.get("sportsgambler_link")
        if not url: continue
        
        # Check if we have fixtures for this league
        league_fixtures = list(db.fixtures.find({"league_name": league_name, "date": {"$in": valid_dates}}))
        if not league_fixtures:
            print(f"  [{league_name}] Bugun/sabah ucun fixture yoxdur, atlanir.")
            continue

        print(f"\n  [SportsGambler] Scraping: {league_name} -> {url}")
        driver.get(url)
        time.sleep(8)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all("a", class_="betlist-item")
        
        updated_league = 0
        for item in items:
            # Determine league for this item (either the league we're in, or from the tag)
            item_league_tag = item.find("span", class_="betlist-league")
            sg_league = item_league_tag.get_text(strip=True) if item_league_tag else ""
            
            # Find which DB league this match belongs to
            matched_db_league = league_name if league_name != "Global" else None
            if league_name == "Global" or (sg_league and not fuzzy_match(league_name, sg_league)):
                # If global or if item league differs, try to match from all configs
                all_configs = list(db.leagues_config.find({}))
                for l in all_configs:
                    l_n = l.get("name", "")
                    l_s = l.get("sportsgambler_link", "")
                    if (l_s and fuzzy_match(l_s, sg_league)) or fuzzy_match(l_n, sg_league):
                        matched_db_league = l_n
                        break
            
            if not matched_db_league: continue
            
            teams_span = item.find("span", class_="betlist-teams")
            if not teams_span: continue
            tags = teams_span.find_all("span")
            if len(tags) < 2: continue
            
            h_name = tags[0].get_text(strip=True)
            a_name = tags[1].get_text(strip=True)
            link = item.get("href")
            if link and not link.startswith("http"):
                link = f"https://www.sportsgambler.com{link}"
            
            h_name_resolved = resolve_team_name(h_name)
            a_name_resolved = resolve_team_name(a_name)

            db_fixtures = list(db.fixtures.find({"league_name": matched_db_league, "date": {"$in": valid_dates}}))
            for f in db_fixtures:
                db_home = resolve_team_name(f["home_team"])
                db_away = resolve_team_name(f["away_team"])
                if fuzzy_match(db_home, h_name_resolved, is_team=True) and fuzzy_match(db_away, a_name_resolved, is_team=True):
                    db.fixtures.update_one({"_id": f["_id"]}, {"$set": {"predictions.sportsgambler_link": link}})
                    updated_league += 1
                    updated_total += 1
                    break
        print(f"    Updated {updated_league} matches for {league_name}")

    print(f"\n  [Total] Updated: {updated_total}")

def run_betimate_links_only():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    _cleanup_stale_chromedriver()
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    print("[*] Launching browser for betimate links...")
    driver = uc.Chrome(options=options, version_main=148)
    driver.maximize_window()

    try:
        update_betimate(driver, db)
    except Exception as e:
        print(f"[!] Error in betimate links: {e}")
    finally:
        _safe_quit_driver(driver)
        print("[*] Finished betimate links.")


def run_sportsgambler_links_only():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    _cleanup_stale_chromedriver()
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    print("[*] Launching browser for sportsgambler links...")
    driver = uc.Chrome(options=options, version_main=148)
    driver.maximize_window()

    try:
        update_sportsgambler(driver, db)
    except Exception as e:
        print(f"[!] Error in sportsgambler links: {e}")
    finally:
        _safe_quit_driver(driver)
        print("[*] Finished sportsgambler links.")


def run_wincomparator_links_only():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    _cleanup_stale_chromedriver()
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    print("[*] Launching browser for wincomparator links...")
    driver = uc.Chrome(options=options, version_main=148)
    driver.maximize_window()

    try:
        update_wincomparator(driver, db)
    except Exception as e:
        print(f"[!] Error in wincomparator links: {e}")
    finally:
        _safe_quit_driver(driver)
        print("[*] Finished wincomparator links.")


import shutil


def update_footystats(db):
    print("\n" + "="*30)
    print("STEP: FOOTYSTATS")
    print("="*30)
    leagues_config = list(db.leagues_config.find({"footystats_link": {"$ne": ""}}))
    if not leagues_config:
        print("[FootyStats] No footystats_link found in leagues_config. Atlanir.")
        return

    valid_dates = get_today_tomorrow_dates()
    for league in leagues_config:
        league_name = league.get("name")
        league_path = league.get("footystats_link")
        if not league_path:
            continue

        fixtures = list(db.fixtures.find({"league_name": league_name, "date": {"$in": valid_dates}}))
        if not fixtures:
            print(f"  [{league_name}] Bugun/sabah ucun fixture yoxdur, kecilir.")
            continue

        url = league_path if league_path.startswith("http") else f"https://footystats.org/{league_path}/fixtures"
        print(f"  [{league_name}] {url}")

        _cleanup_stale_chromedriver()
        opts = uc.ChromeOptions()
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1920,1080")
        try:
            driver = uc.Chrome(options=opts, version_main=148)
        except Exception:
            time.sleep(3)
            driver = uc.Chrome(options=opts, version_main=148)
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        _safe_quit_driver(driver)

        match_uls = soup.find_all("ul", class_=lambda c: c and "match row cf" in c if c else False)
        if not match_uls:
            print(f"  [{league_name}] Hec bir match tapilmadi.")
            continue

        updated = 0
        for mu in match_uls:
            date_li = mu.find("li", class_="date")
            match_ts = None
            if date_li:
                ts_str = date_li.get("data-time")
                if ts_str:
                    match_ts = int(ts_str)

            info_li = mu.find("li", class_="match-info")
            if not info_li:
                continue

            h2h_link_tag = info_li.find("a", class_=lambda c: c and "h2h-link" in c.split() if c else False)
            if not h2h_link_tag:
                continue

            href = h2h_link_tag.get("href", "")
            home_tag = info_li.find("a", class_=lambda c: c and "team home" in str(c) if c else False)
            away_tag = info_li.find("a", class_=lambda c: c and "team away" in str(c) if c else False)
            if not home_tag or not away_tag:
                continue

            h_name_span = home_tag.find("span", class_="hover-modal-parent hover-modal-ajax-team")
            a_name_span = away_tag.find("span", class_="hover-modal-parent hover-modal-ajax-team")
            h_name = resolve_team_name(h_name_span.get_text(strip=True) if h_name_span else home_tag.get_text(strip=True))
            a_name = resolve_team_name(a_name_span.get_text(strip=True) if a_name_span else away_tag.get_text(strip=True))

            link = f"https://footystats.org{href}" if href.startswith("/") else href

            for f in fixtures:
                if fuzzy_match(f["home_team"], h_name, is_team=True) and fuzzy_match(f["away_team"], a_name, is_team=True):
                    if match_ts:
                        f_date_obj = datetime.fromtimestamp(match_ts)
                        f_date_str = f"{f_date_obj.strftime('%A, %B')} {f_date_obj.day} {f_date_obj.strftime('%Y')}"
                        if f.get("date") != f_date_str:
                            continue
                    if f.get("predictions", {}).get("footystats_stats"):
                        print(f"    {h_name} vs {a_name} - artiq footystats datasi var, kecildi.")
                        continue
                    db.fixtures.update_one({"_id": f["_id"]}, {"$set": {"predictions.footystats_h2h_link": link}})
                    updated += 1
                    break

        print(f"  [{league_name}] Updated (link): {updated}")


def run_footystats_links_only():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    try:
        update_footystats(db)
    except Exception as e:
        print(f"[!] Error in footystats links: {e}")
    finally:
        client.close()
        print("[*] Finished footystats links.")


def run_all_link_updates(steps=None):
    """Run selected prediction link updaters. steps=None means all steps."""
    if steps is None:
        steps = ["wincomparator", "oddslot", "betimate", "sportsgambler", "footystats"]

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    print("\n" + "="*50)
    print(f"PROQNOZ LINKLERI YENILENIR: {', '.join(steps)}")
    print("="*50)

    report = {}
    driver = None

    needs_driver = [s for s in steps if s != "footystats"]
    if needs_driver:
        _cleanup_stale_chromedriver()
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        driver = uc.Chrome(options=options, version_main=148)
        driver.maximize_window()

    try:
        for step in steps:
            print(f"\n>>> {step}...")
            try:
                if step == "wincomparator":
                    update_wincomparator(driver, db)
                elif step == "oddslot":
                    update_oddslot(driver, db)
                elif step == "betimate":
                    update_betimate(driver, db)
                elif step == "sportsgambler":
                    update_sportsgambler(driver, db)
                elif step == "footystats":
                    update_footystats(db)
                else:
                    print(f"  [!] Bilinmeyen step: {step}")
                    report[step] = "BILINMEYEN STEP"
                    continue
                report[step] = "OK"
            except Exception as e:
                report[step] = f"XETA: {e}"
                print(f"  [!] {step} xetasi: {e}")
    finally:
        _safe_quit_driver(driver)

    # Report
    print("\n" + "="*50)
    print("HESABAT")
    print("="*50)
    ok_count = 0
    fail_count = 0
    for name, status in report.items():
        if status == "OK":
            print(f"  [OK] {name}")
        else:
            print(f"  [FAIL] {name} - {status}")
            fail_count += 1
    print("-"*50)
    print(f"  Cemi: {len(report)} | Ugurlu: {ok_count} | Xeta: {fail_count}")
    print("="*50)

    client.close()


if __name__ == "__main__":
    import sys
    steps = None
    if "--step" in sys.argv:
        idx = sys.argv.index("--step")
        steps = []
        for arg in sys.argv[idx+1:]:
            if arg.startswith("--"):
                break
            steps.append(arg)
    run_all_link_updates(steps)
