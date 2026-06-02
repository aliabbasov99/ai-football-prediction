import os
import re
import time
import difflib
import unicodedata
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

DB_NAME = "football_prediction"
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

AZ_TO_EN = {}
# Will be populated dynamically from DB


# Load explicit mappings (Name=Name format) from dictionary.txt at import time
_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "dictionary.txt")
if not os.path.exists(_dict_path):
    _dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictionary.txt")
if os.path.exists(_dict_path):
    with open(_dict_path, "r", encoding="utf-8") as _f:
        _raw_lines = _f.readlines()
    _explicit_count = 0
    for _line in _raw_lines:
        _line = _line.strip()
        if "=" in _line and not _line.startswith("#"):
            _az, _en = _line.split("=", 1)
            _az = _az.strip()
            _en = _en.strip()
            if _az and _en:
                AZ_TO_EN[_az] = _en
                _explicit_count += 1
    if _explicit_count > 0:
        print(f"[Misli] Loaded {_explicit_count} explicit mappings from dictionary.txt")

# Display names on misli.az for each league in the category tree
LEAGUE_AZ_NAMES = {
    "Premier League": "PREMYER L\u0130QA",
    "La Liga": "LA L\u0130QA",
    "Bundesliga": "BUNDESL\u0130QA",
    "Serie A": "SER\u0130YA A",
    "Ligue 1": "L\u0130QA 1",
    "Primeira Liga": "PR\u0130MEYRA L\u0130QA",
    "Eredivisie": "ERED\u0130V\u0130Z\u0130YA",
    "Brasileirao": "SER\u0130YA A",
    "MLS": "MLS",
}


def normalize_text(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]', '', text.lower().strip())


def extract_odds_from_row(row_soup):
    odds = {}
    odds_wrapper = row_soup.find("div", class_="bulletinOddsWrapper")
    if not odds_wrapper:
        return odds

    def get_pw_value(pw):
        # 1. Try finding div with class="oddValue"
        odd_val_div = pw.find("div", class_="oddValue")
        if odd_val_div:
            span = odd_val_div.find("span")
            if span:
                return span.get_text(strip=True)
            return odd_val_div.get_text(strip=True)
        # 2. Try finding span with class="lastOdd"
        last_odd_span = pw.find("span", class_="lastOdd")
        if last_odd_span:
            return last_odd_span.get_text(strip=True)
        # 3. Fallback: find any span in pw
        all_spans = pw.find_all("span")
        if all_spans:
            return all_spans[0].get_text(strip=True)
        return ""

    rate_divs = odds_wrapper.find_all("div", class_="bulletinOddsRate")
    for rate_div in rate_divs:
        priority = rate_div.get("data-priority", "")
        pws = rate_div.find_all("div", class_="percentageWrapper")
        
        # We extract all values first
        values = []
        for pw in pws:
            if pw.find("div", class_="oddsType") or "oddType" in pw.get("class", []):
                # Skip oddsType separator (like 2.5) in priority 3
                continue
            val = get_pw_value(pw)
            if val:
                values.append(val)
                
        if priority == "1" and len(values) >= 3:
            odds["home_win"] = values[0]
            odds["draw"] = values[1]
            odds["away_win"] = values[2]
        elif priority == "2" and len(values) >= 3:
            odds["double_chance"] = {"1X": values[0], "12": values[1], "X2": values[2]}
        elif priority == "3" and len(values) >= 2:
            # First is ALT (Under), second is ÜST (Over)
            odds["over_under"] = {"under": values[0], "over": values[1]}
        elif priority == "4" and len(values) >= 2:
            # First is Bəli (Yes), second is Xeyr (No)
            odds["btts"] = {"yes": values[0], "no": values[1]}
            
    return odds


def find_team_names(row_soup):
    match_info = row_soup.find("div", class_="bulletinMatchInfo")
    if match_info:
        home_el = match_info.find("span", class_="bulletinHomeTeam")
        away_el = match_info.find("span", class_="bulletinAwayTeam")
        if home_el and away_el:
            home = home_el.get_text(strip=True)
            away = away_el.get_text(strip=True)
            if home and away:
                return [home, away]
    all_texts = list(row_soup.stripped_strings)
    skip_words = {"comment", "İddaa İstatistik", "Canlı İddaa Kapalı Market", "C", "1", "X", "2"}
    non_odds = [t for t in all_texts if len(t) > 2 and t not in skip_words and not re.match(r'^[\d.+\-*/]+$', t)]
    if len(non_odds) >= 2:
        return non_odds[:2]
    return []


def map_team_name(raw_name):
    if raw_name in AZ_TO_EN:
        return AZ_TO_EN[raw_name]
    norm = normalize_text(raw_name)
    for az_name, en_name in AZ_TO_EN.items():
        if normalize_text(az_name) == norm:
            return en_name
    return raw_name


def _infer_from_dictionary():
    """Infer AZ->EN team name mappings from raw page text in dictionary.txt."""
    _dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "dictionary.txt")
    if not os.path.exists(_dict_path):
        _dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dictionary.txt")
    if not os.path.exists(_dict_path):
        return

    with open(_dict_path, "r", encoding="utf-8") as _f:
        _raw_lines_list = [l.strip() for l in _f if l.strip()]


    _skip_words = {"comment", "İddaa İstatistik", "Canlı İddaa Kapalı Market", "C", "1", "X", "2",
                   "Bu Gün", "Sabah", "Cüm.", "Baz.", "ÇAx.", "Şən.", "Cümə", "Şənbə",
                   "Bazar", "Çərşənbə", "Çərşənbə Axşamı", "Cümə Axşamı"}
    _found_az_names = set()
    for _line in _raw_lines_list:
        if _line in _skip_words or re.match(r'^[\d.:+\-/]+$', _line) or re.match(r'^[\d.]+$', _line):
            continue
        if re.match(r'^[\w\s]+$', _line, re.U) and 3 < len(_line) < 40:
            _found_az_names.add(_line)

    if not _found_az_names:
        return

    try:
        _client = MongoClient(MONGO_URL)
        _db = _client[DB_NAME]
        _valid_dates = []
        for _delta in [0, 1]:
            _d = datetime.now() + timedelta(days=_delta)
            _valid_dates.append(f"{_d.strftime('%A, %B')} {_d.day} {_d.strftime('%Y')}")
        _db_fixtures = list(_db.fixtures.find({"date": {"$in": _valid_dates}}))
        _client.close()

        _inferred = 0
        for _az_name in sorted(_found_az_names):
            if _az_name in AZ_TO_EN:
                continue
            _best_match = None
            _best_score = 0
            for _f in _db_fixtures:
                _h = _f.get("home_team", "")
                _a = _f.get("away_team", "")
                for _en_candidate in [_h, _a]:
                    if not _en_candidate:
                        continue
                    _az_norm = normalize_text(_az_name)
                    _en_norm = normalize_text(_en_candidate)
                    _score = 0
                    if _az_norm == _en_norm:
                        _score = 3
                    elif _az_norm in _en_norm or _en_norm in _az_norm:
                        _score = 2
                    else:
                        _ratio = difflib.SequenceMatcher(None, _az_norm, _en_norm).ratio()
                        if _ratio >= 0.7:
                            _score = 1
                    if _score > _best_score:
                        _best_score = _score
                        _best_match = _en_candidate
            if _best_match and _best_score > 0:
                AZ_TO_EN[_az_name] = _best_match
                _inferred += 1
                print(f"  [dict] Inferred: {_az_name} -> {_best_match}")
        if _inferred:
            print(f"[Misli] Inferred {_inferred} team name mappings from dictionary.txt")
        else:
            print(f"[Misli] Found {len(_found_az_names)} names in dictionary.txt but could not infer mappings")
    except Exception as _e:
        print(f"[Misli] dictionary.txt inference error: {_e}")


def scrape_misli():
    print("\n[Misli] Starting misli.az odds scraping...")
    try:
        import undetected_chromedriver as uc
    except ImportError:
        print("[Misli] undetected_chromedriver not installed, skipping.")
        return

    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Load dynamic config and team aliases
    leagues_config = list(db.leagues_config.find({}))
    league_urls = {}
    for l in leagues_config:
        name = l.get("name")
        m_link = l.get("misli_link")
        if name and m_link:
            league_urls[name] = m_link

    # Load central alias map from teams collection
    alias_count = 0
    for team in db.teams.find({}, {"name": 1, "aliases": 1}):
        canonical = team.get("name")
        for alias in team.get("aliases", []):
            if alias and alias not in AZ_TO_EN:
                AZ_TO_EN[alias] = canonical
                alias_count += 1
    if alias_count:
        print(f"[Misli] Loaded {alias_count} aliases from teams collection")

    # Build normalized alias maps for matching
    TEAM_ALIASES_NORM = {}
    for team in db.teams.find({}, {"name": 1, "aliases": 1}):
        canonical = team.get("name", "")
        if not canonical:
            continue
        c_norm = normalize_text(canonical)
        alias_set = {c_norm}
        for alias in team.get("aliases", []):
            if alias:
                alias_set.add(normalize_text(alias))
        
        # Map every single name in the set to the entire set of aliases
        for name_norm in alias_set:
            if name_norm not in TEAM_ALIASES_NORM:
                TEAM_ALIASES_NORM[name_norm] = set()
            TEAM_ALIASES_NORM[name_norm].update(alias_set)

    print(f"[Misli] Loaded {len(league_urls)} leagues from config")

    _infer_from_dictionary()

    valid_dates = []
    for delta in [0, 1]:
        d = datetime.now() + timedelta(days=delta)
        valid_dates.append(f"{d.strftime('%A, %B')} {d.day} {d.strftime('%Y')}")

    # Early exit check: are there any fixtures at all for these dates?
    total_fixtures_count = db.fixtures.count_documents({"date": {"$in": valid_dates}})
    if total_fixtures_count == 0:
        print("[Misli] Bugun/sabah ucun hecbir fixture tapilmadi. Scraper dayandirilir.")
        client.close()
        return

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options, version_main=148)

    total_matched = 0
    total_fixtures = 0

    try:
        for league_name, url in league_urls.items():
            db_fixtures = list(db.fixtures.find({
                "league_name": league_name,
                "date": {"$in": valid_dates},
                "predictions.misli_odds": {"$exists": False},
            }))
            if not db_fixtures:
                print(f"\n[Misli] {league_name} - bugun/sabah oyun yoxdur, kecildi.")
                continue

            print(f"\n[Misli] {league_name} ({len(db_fixtures)} oyun) -> {url}")
            driver.get(url)
            time.sleep(2)

            # Scroll down to lazy-load matches
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(0.8)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            rows = soup.find_all("div", class_=re.compile(r"bulletinRowInner|bulletinRow"))
            if not rows:
                match_infos = soup.find_all("div", class_="bulletinMatchInfo")
                rows = [mi.find_parent() for mi in match_infos if mi.find_parent()]
            if not rows:
                rows = soup.find_all("div", attrs={"data-detail-id": True})

                # If no game rows, site is showing category tree — click league to load games
                if not rows:
                    az_name = LEAGUE_AZ_NAMES.get(league_name)
                    if az_name:
                        try:
                            league_el = driver.find_element(
                                By.XPATH, f"//p[@class='leagueName' and contains(text(), '{az_name}')]"
                            )
                            driver.execute_script("arguments[0].click();", league_el)
                            time.sleep(2)
                            soup = BeautifulSoup(driver.page_source, "html.parser")
                            rows = soup.find_all("div", class_=re.compile(r"bulletinRowInner|bulletinRow"))
                            if not rows:
                                match_infos = soup.find_all("div", class_="bulletinMatchInfo")
                                rows = [mi.find_parent() for mi in match_infos if mi.find_parent()]
                            if not rows:
                                rows = soup.find_all("div", attrs={"data-detail-id": True})
                        except Exception:
                            pass

            scraped = []
            for row in rows:
                odds = extract_odds_from_row(row)
                if not odds:
                    continue
                teams = find_team_names(row)
                if len(teams) >= 2:
                    home_en = map_team_name(teams[0])
                    away_en = map_team_name(teams[1])
                    scraped.append((home_en, away_en, odds))

            print(f"[Misli] {len(scraped)} matches scraped")

            league_matched = 0
            for db_f in db_fixtures:
                db_home = db_f.get("home_team", "")
                db_away = db_f.get("away_team", "")
                if not db_home or not db_away:
                    continue

                best_odds = None
                best_score = 0
                db_h_norm = normalize_text(db_home)
                db_a_norm = normalize_text(db_away)
                db_h_aliases = TEAM_ALIASES_NORM.get(db_h_norm, {db_h_norm})
                db_a_aliases = TEAM_ALIASES_NORM.get(db_a_norm, {db_a_norm})

                for h_en, a_en, odds in scraped:
                    h_norm = normalize_text(h_en)
                    a_norm = normalize_text(a_en)
                    scraped_h_aliases = TEAM_ALIASES_NORM.get(h_norm, {h_norm})
                    scraped_a_aliases = TEAM_ALIASES_NORM.get(a_norm, {a_norm})

                    # Direct/Alias exact intersection matches
                    home_matched = (h_norm == db_h_norm) or not scraped_h_aliases.isdisjoint(db_h_aliases)
                    away_matched = (a_norm == db_a_norm) or not scraped_a_aliases.isdisjoint(db_a_aliases)

                    if home_matched and away_matched:
                        score = 3
                    elif ((h_norm == db_a_norm) or not scraped_h_aliases.isdisjoint(db_a_aliases)) and \
                         ((a_norm == db_h_norm) or not scraped_a_aliases.isdisjoint(db_h_aliases)):
                        score = 2
                    else:
                        h_fuzzy = False
                        for s_alias in scraped_h_aliases:
                            for d_alias in db_h_aliases:
                                if s_alias in d_alias or d_alias in s_alias:
                                    h_fuzzy = True
                                    break
                                ratio = difflib.SequenceMatcher(None, s_alias, d_alias).ratio()
                                if ratio >= 0.7:
                                    h_fuzzy = True
                                    break
                            if h_fuzzy:
                                break

                        a_fuzzy = False
                        for s_alias in scraped_a_aliases:
                            for d_alias in db_a_aliases:
                                if s_alias in d_alias or d_alias in s_alias:
                                    a_fuzzy = True
                                    break
                                ratio = difflib.SequenceMatcher(None, s_alias, d_alias).ratio()
                                if ratio >= 0.7:
                                    a_fuzzy = True
                                    break
                            if a_fuzzy:
                                break

                        if h_fuzzy and a_fuzzy:
                            score = 1
                        else:
                            score = 0

                    if score > best_score:
                        best_score = score
                        best_odds = odds

                if best_odds and best_score >= 1:
                    db.fixtures.update_one(
                        {"_id": db_f["_id"]},
                        {"$set": {"predictions.misli_odds": best_odds}}
                    )
                    league_matched += 1
                    total_matched += 1
                    print(f"  [OK] {db_home} vs {db_away}")

            print(f"[Misli] {league_name}: {league_matched}/{len(db_fixtures)} matched")
            total_fixtures += len(db_fixtures)

    except Exception as e:
        print(f"[Misli] Xeta: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        client.close()

    print(f"\n[Misli] Total: {total_matched}/{total_fixtures} matches matched.")


def cleanup_scratch():
    print("[Misli] No scratch files to clean up.")


if __name__ == "__main__":
    scrape_misli()
    cleanup_scratch()
