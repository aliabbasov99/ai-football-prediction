import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import re
import random
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from datetime import datetime, timedelta

def _cleanup_stale_chromedriver():
    ucd_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'appdata', 'roaming', 'undetected_chromedriver')
    exe_path = os.path.join(ucd_dir, 'undetected_chromedriver.exe')
    if os.path.exists(exe_path):
        for _ in range(3):
            try:
                os.remove(exe_path)
                break
            except:
                time.sleep(0.5)

def get_today_tomorrow_dates():
    result = []
    for delta in [0, 1]:
        d = datetime.now() + timedelta(days=delta)
        result.append(f"{d.strftime('%A, %B')} {d.day} {d.strftime('%Y')}")
    return result

# Config
DB_NAME = "football_prediction"
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

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
        print(f"[Betimate] Loaded {len(_ALIAS_MAP)} team aliases from DB")
    except Exception as e:
        print(f"[Betimate] Alias load error: {e}")
    _ALIAS_LOADED = True

def resolve_team_name(name):
    if not name:
        return name
    _ensure_alias_map()
    if name in _ALIAS_MAP:
        return _ALIAS_MAP[name]
    return name

def parse_betimate_stats(soup):
    stats = {}
    container = soup.find("div", class_="probability-odd")
    if not container: return stats
    
    rows = container.find_all("div", class_="probability-odd-info-row")
    for r in rows:
        cols = r.find_all("div", class_="probability-odd-col")
        if len(cols) < 2: continue
        label = cols[0].get_text(strip=True).lower()
        prob = cols[1].get_text(strip=True)
        
        if "home win" in label: stats["home_win"] = prob
        elif "draw" == label: stats["draw"] = prob
        elif "away win" in label: stats["away_win"] = prob
        elif "under 2.5" in label: stats["under_2_5"] = prob
        elif "over 2.5" in label: stats["over_2_5"] = prob
        elif "btts yes" in label: stats["btts_yes"] = prob
        elif "btts no" in label: stats["btts_no"] = prob
    return stats

def parse_upcoming_matches(soup, team_type):
    matches = []
    seen_matches = set() # To prevent duplicates
    
    containers = soup.find_all("div", class_=f"{team_type}-last-matches")
    target_container = None
    
    for c in containers:
        title_el = c.find("h4", class_="match-title")
        if not title_el: continue
        title_text = title_el.get_text().lower()
        
        if "upcoming" in title_text:
            target_container = c
            break
            
    if not target_container: return matches
    
    rows = target_container.find_all("div", class_="matches-row")
    for r in rows:
        date_div = r.find("div", class_="matches-date")
        if not date_div: continue
        
        # Clean up date
        if date_div.find("div", class_="st_ltag"):
            date_raw = date_div.find(text=True, recursive=False)
            if date_raw: date_raw = date_raw.strip()
            else: date_raw = date_div.get_text(strip=True).replace("EPL", "").replace("UCL", "").strip()
        else:
            date_raw = date_div.get_text(strip=True)
            
        home = resolve_team_name(r.find("div", class_="matches-home").get_text(strip=True))
        away = resolve_team_name(r.find("div", class_="matches-away").get_text(strip=True))
        
        res = ""
        res_div = r.find("div", class_="st_res")
        if res_div:
            res = res_div.get_text(strip=True)
        else:
            res_cnt = r.find("div", class_="matches-rescnt")
            if res_cnt: res = res_cnt.get_text(strip=True)
            
        # Skip if result is a real score
        if res and res != "0-0" and "-" in res:
            if re.search(r"\d-\d", res): continue
            
        # Deduplication check
        match_id = f"{date_raw}|{home}|{away}"
        if match_id in seen_matches:
            continue
        seen_matches.add(match_id)
        
        matches.append({
            "date": date_raw,
            "home": home,
            "away": away,
            "result": res
        })
    return matches

def parse_top_scorers(soup):
    scorers = []
    body = soup.find("div", class_="player-body")
    if not body: return scorers
    
    rows = body.find_all("div", class_="player-content")
    for r in rows:
        cells = r.find_all("div", class_="player-cell")
        if len(cells) < 7: continue
        
        rank = cells[0].get_text(strip=True)
        name_box = cells[1].find("a", class_="top-scorers-player-name")
        name = name_box.find("span", class_="show-desktop").get_text(strip=True) if name_box else ""
        team_box = cells[1].find("a", class_="sp-c-top-scorers__teams")
        team = team_box.find("span", class_="show-desktop").get_text(strip=True) if team_box else ""
        
        scorers.append({
            "rank": rank,
            "name": name,
            "team": team,
            "ga": cells[2].get_text(strip=True),
            "pk": cells[3].get_text(strip=True),
            "mp": cells[4].get_text(strip=True),
            "minutes": cells[5].get_text(strip=True),
            "mpg": cells[6].get_text(strip=True)
        })
    return scorers

def run():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    valid_dates = get_today_tomorrow_dates()
    print(f"[*] Tarix filteri: {valid_dates}")
    matches = list(db.fixtures.find({
        "predictions.betimate_link": {"$exists": True, "$ne": ""},
        "date": {"$in": valid_dates},
        "$or": [
            {"predictions.betimate_stats": {"$exists": False}},
            {"predictions.betimate_stats": None},
        ],
    }))
    if not matches:
        print("[!] Bugun/sabah ucun betimate linki olan ve statistikasi olmayan fixture yoxdur.")
        client.close()
        return
    print(f"[*] {len(matches)} fixture tapildi.")

    _cleanup_stale_chromedriver()
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--incognito")
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        for m in matches:
            url = m["predictions"]["betimate_link"]
            print(f"[*] Scraping Betimate: {m['home_team']} vs {m['away_team']}")
            driver.get(url)
            time.sleep(15)
            
            driver.execute_script("window.scrollTo(0, 3000);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 6000);")
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            stats = parse_betimate_stats(soup)
            home_upcoming = parse_upcoming_matches(soup, "home")
            away_upcoming = parse_upcoming_matches(soup, "away")
            top_scorers = parse_top_scorers(soup)
            
            update_data = {
                "predictions.betimate_stats": stats,
                "predictions.betimate_upcoming": {
                    "home": home_upcoming,
                    "away": away_upcoming
                }
            }
            if top_scorers:
                update_data["predictions.top_scorers"] = top_scorers
                
            db.fixtures.update_one({"_id": m["_id"]}, {"$set": update_data})
            print(f"    [+] Updated. (Upcoming: {len(home_upcoming)}/{len(away_upcoming)})")
            
            time.sleep(random.uniform(5, 10))
            
    finally:
        driver.quit()
        client.close()

if __name__ == "__main__":
    run()
