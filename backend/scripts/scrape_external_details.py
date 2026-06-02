import undetected_chromedriver as uc
import time
import os
import re
import unicodedata
import random
import difflib
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta

def get_today_tomorrow_dates():
    result = []
    for delta in [0, 1]:
        d = datetime.now() + timedelta(days=delta)
        result.append(f"{d.strftime('%A, %B')} {d.day} {d.strftime('%Y')}")
    return result

DB_NAME = "football_prediction"
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

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

def remove_accents(input_str):
    if not input_str: return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_text(text):
    if not text: return ""
    text = remove_accents(text).lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

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
        print(f"[External] Loaded {len(_ALIAS_MAP)} team aliases from DB")
    except Exception as e:
        print(f"[External] Alias load error: {e}")
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



def _scrape_form_column(col_soup):
    info = {}
    form_box = col_soup.find("div", class_="form-box")
    if form_box:
        info["ppg"] = form_box.get_text(strip=True)
    form_run_ul = col_soup.find("ul", class_="form-run")
    if form_run_ul:
        run = []
        for li in form_run_ul.find_all("li"):
            a = li.find("a", class_="form-run-box")
            if a:
                txt = a.get_text(strip=True)
                if txt in ("W", "D", "L"):
                    run.append(txt)
        if run:
            info["form_run"] = run
    wrapper = col_soup.find("div", class_="h2h-history-results-wrapper")
    if wrapper:
        last5 = []
        for row in wrapper.find_all("div", class_="h2h-history-row"):
            divs = row.find_all("div", class_="team-name-box")
            score_box = row.find("div", class_="score-box")
            if len(divs) >= 2 and score_box:
                home_txt = divs[0].get_text(strip=True)
                away_txt = divs[1].get_text(strip=True)
                score_a = score_box.find("a")
                score = score_a.get_text(strip=True) if score_a else ""
                if score and not any(c.isdigit() for c in score.replace(" ", "")):
                    continue
                last5.append({
                    "home": home_txt,
                    "away": away_txt,
                    "score": score,
                })
        if last5:
            info["last5"] = last5
    return info


def _parse_form_section(driver, match):
    from selenium.webdriver.common.by import By

    def _team_logo_img(col):
        return col.find("img", alt=lambda a: a and "Logo" in a)

    def _find_form_container(soup):
        """Form container tap - section ve ya div ola biler."""
        fs = soup.find("section", class_=lambda c: c and "form-section" in c if c else False)
        if fs:
            return fs
        for div in soup.find_all("div", class_=lambda c: c and "rmt0" in (c.split() if c else []) if c else False):
            cols = div.find_all("div", class_="w30 fl")
            if len(cols) >= 2:
                return div
        for div in soup.find_all("div", class_=lambda c: c and "mt05e" in (c.split() if c else []) if c else False):
            cols = div.find_all("div", class_="w30 fl")
            if len(cols) >= 2:
                return div
        return None

    def _find_team_positions(soup):
        fs = _find_form_container(soup)
        if not fs:
            return None, None
        cols = fs.find_all("div", class_="w30 fl")
        pos = {}
        for i, col in enumerate(cols):
            img = _team_logo_img(col)
            txt = img.get("alt", "").replace(" Logo", "") if img else ""
            txt = resolve_team_name(txt)
            if fuzzy_match(match["home_team"], txt, is_team=True):
                pos["home_team"] = i
            elif fuzzy_match(match["away_team"], txt, is_team=True):
                pos["away_team"] = i
        return pos if len(pos) == 2 else None, fs

    form_data = {}
    soup_init = BeautifulSoup(driver.page_source, 'html.parser')
    team_positions, fs_init = _find_team_positions(soup_init)
    if team_positions:
        for tab_name in ("overall", "home", "away"):
            try:
                tabs = driver.find_elements(By.CSS_SELECTOR, f"li[data-form='{tab_name}'] p")
                for tab in tabs:
                    try:
                        driver.execute_script("arguments[0].click();", tab)
                    except:
                        pass
            except:
                pass
            time.sleep(1.2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            _, fs = _find_team_positions(soup)
            if not fs:
                continue
            cols = fs.find_all("div", class_="w30 fl")
            for side, idx in team_positions.items():
                if idx >= len(cols):
                    continue
                if side not in form_data:
                    form_data[side] = {}
                info = _scrape_form_column(cols[idx])
                if info:
                    form_data[side][tab_name] = info

    # AllHomeAway combined: overall + home + away melumatlarini birlesdir
    if form_data:
        for side in form_data:
            tabs_data = form_data[side]
            combined = {}
            # form_run ("overall" esasdir, yoxdursa home, yoxdursa away)
            for src in ("overall", "home", "away"):
                t = tabs_data.get(src, {})
                fr = t.get("form_run")
                if fr:
                    combined["form_run"] = fr
                    combined["ppg"] = t.get("ppg", "")
                    if src == "overall":
                        break
            # last5 - butun tablardan topla, unikal saxla
            seen = set()
            merged_last5 = []
            for src in ("overall", "home", "away"):
                for m in tabs_data.get(src, {}).get("last5", []):
                    key = (m.get("home",""), m.get("away",""), m.get("score",""))
                    if key not in seen:
                        seen.add(key)
                        merged_last5.append(m)
            if merged_last5:
                combined["last5"] = merged_last5
            if combined:
                form_data[side]["combined"] = combined

    if not form_data or all(len(v) == 0 for v in form_data.values()):
        print("    [Form] Selenium tab approach empty, using visible-data fallback")
        fallback = {}
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        fs = _find_form_container(soup)
        if fs:
            for col in fs.find_all("div", class_="w30 fl"):
                img = _team_logo_img(col)
                txt = img.get("alt", "").replace(" Logo", "") if img else ""
                txt = resolve_team_name(txt)
                side = None
                if fuzzy_match(match["home_team"], txt, is_team=True):
                    side = "home_team"
                elif fuzzy_match(match["away_team"], txt, is_team=True):
                    side = "away_team"
                if not side:
                    continue
                info = _scrape_form_column(col)
                if info:
                    active_tab = col.find("p", class_="active")
                    tab_key = "overall"
                    if active_tab:
                        parent = active_tab.find_parent("li")
                        if parent and parent.get("data-form"):
                            tab_key = parent["data-form"]
                    if side not in fallback:
                        fallback[side] = {}
                    fallback[side][tab_key] = info
        if fallback:
            for side, d in fallback.items():
                if side not in form_data:
                    form_data[side] = {}
                form_data[side].update(d)

    return form_data


def scrape_footystats_h2h(driver, db, match):
    _ensure_alias_map()
    url = match["predictions"].get("footystats_h2h_link", "")
    if not url:
        return {}

    print(f"  [FootyStats] {match['home_team']} vs {match['away_team']}")
    driver.get(url)
    time.sleep(2)

    for _ in range(5):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        has_data = soup.find("div", class_="comparison-bar") or soup.find("div", class_="stat-grid")
        if has_data:
            break
        time.sleep(2)

    if not has_data:
        page_text = driver.page_source.lower()
        if "captcha" in page_text or "cf-browser-verification" in page_text:
            print("    [FootyStats] Blocked, skipping.")
        return {}

    h2h_data = {}

    # Comparison bars
    bars = soup.find_all("div", class_="comparison-bar")
    for bar in bars:
        label_el = bar.find("div", class_="comparison-title")
        home_el = bar.find("div", class_="stat-home")
        away_el = bar.find("div", class_="stat-away")
        if label_el and home_el and away_el:
            key = normalize_text(label_el.get_text(strip=True))
            h2h_data[key] = {
                "home": home_el.get_text(strip=True),
                "away": away_el.get_text(strip=True),
            }

    # Stat grid
    stat_grid = soup.find("div", class_="stat-grid")
    if stat_grid:
        rows = stat_grid.find_all("div", class_="stat-row")
        for row in rows:
            cells = row.find_all("div", class_=lambda c: c and "stat-cell" in c if c else False)
            if len(cells) >= 3:
                label = cells[1].get_text(strip=True)
                h2h_data[normalize_text(label)] = {
                    "home": cells[0].get_text(strip=True),
                    "away": cells[2].get_text(strip=True),
                }

    # Form section
    form_data = _parse_form_section(driver, match)
    if form_data:
        h2h_data["form"] = form_data

    return h2h_data


def _parse_1x2_outcome(pred_value, data_trans, home_team, away_team):
    """Determine 1X2 outcome from prediction text and data-trans attribute."""
    # Try data-trans attribute first (e.g., "match.probability.1x2.1" -> home)
    if data_trans:
        parts = data_trans.split()
        if parts:
            key = parts[0]
            suffix = key.rsplit(".", 1)[-1]
            if suffix == "1":
                return "home"
            elif suffix == "2":
                return "away"
            elif suffix.lower() in ("x", "draw"):
                return "draw"
    # Fallback to text matching
    if home_team in pred_value:
        return "home"
    if away_team in pred_value:
        return "away"
    # Try alias-resolved pred_value
    resolved_pred = resolve_team_name(pred_value)
    if resolved_pred != pred_value:
        if home_team == resolved_pred or home_team in resolved_pred:
            return "home"
        if away_team == resolved_pred or away_team in resolved_pred:
            return "away"
    if "draw" in pred_value.lower():
        return "draw"
    return "unknown"


def scrape_wincomparator(driver, db, match):
    """Scrape 1X2, Under/Over, BTTS predictions from wincomparator match page."""
    _ensure_alias_map()
    url = match["predictions"].get("wincomparator_link", "")
    if not url: return {}

    print(f"  [WinComparator] {match['home_team']} vs {match['away_team']}")
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = {}

    cards = soup.find_all("div", class_="border border-primary-grayborder rounded-md cursor-pointer")

    for card in cards:
        type_el = card.find("span", class_="bg-secondary-lightgreen")
        if not type_el:
            continue
        card_type = type_el.get_text(strip=True)

        # Prediction value
        pred_bg = card.find("div", class_="bg-secondary-gray")
        pred_value = ""
        data_trans = ""
        if pred_bg:
            data_trans = pred_bg.get("data-trans", "")
            pred_span = pred_bg.find("span", class_="text-primary-darkblue font-bold")
            if pred_span:
                pred_value = pred_span.get_text(strip=True)

        # Probability %
        prob_span = card.find("span", string=re.compile(r'%'))
        probability = ""
        if prob_span:
            m = re.search(r'(\d+\.?\d*)%', prob_span.get_text(strip=True))
            if m:
                probability = m.group(1)

        # Odds from bookmaker section
        odds_el = card.find("div", class_=lambda c: c and "font-bold" in c and "text-primary-darkblue" in c if c else False)
        odds = odds_el.get_text(strip=True) if odds_el else ""

        if "1X2" in card_type:
            outcome = _parse_1x2_outcome(pred_value, data_trans, match["home_team"], match["away_team"])
            data["1x2"] = {
                "outcome": outcome,
                "prediction": pred_value,
                "probability": probability,
                "odds": odds,
            }
        elif "Under" in card_type or "Over" in card_type:
            data["under_over"] = {
                "type": "over" if pred_value.startswith("+") else "under",
                "line": pred_value,
                "probability": probability,
            }
        elif "BTTS" in card_type:
            data["btts"] = {
                "prediction": pred_value,
                "probability": probability,
                "odds": odds,
            }

    return data


def _extract_league_from_h4(h4):
    """Extract clean league name from oddslot h4 (remove count span)."""
    count_span = h4.find("span", class_="drop-league__count")
    if count_span:
        count_span.decompose()
    return h4.get_text(strip=True)


# Explicit Oddslot league -> DB league name overrides
ODDSLOT_LEAGUE_MAP = {
    "England: Premier League": "Premier League",
    "Spain: La Liga": "La Liga",
    "USA: Major League Soccer": "MLS",
    "Major League Soccer": "MLS",
}

def _match_league(oddslot_league, db):
    """Match oddslot league name to a DB league using leagues_config."""
    leagues_config = list(db.leagues_config.find({}))
    oddslot_clean = oddslot_league.rsplit("(", 1)[0].strip()
    
    for l in leagues_config:
        l_name = l.get("name", "")
        odd_name = l.get("oddslot_link", "")
        if not odd_name:
            continue

        # Normalize for comparison
        n_oddslot_link = normalize_text(odd_name)
        n_raw = normalize_text(oddslot_clean)

        # Strategy 1: Exact full-title match (preferred)
        if n_oddslot_link == n_raw:
            return l_name

        # Strategy 2: Match just the league part (after colon)
        league_part = oddslot_clean.split(":")[1].strip() if ":" in oddslot_clean else oddslot_clean
        n_league = normalize_text(league_part)
        if n_oddslot_link == n_league:
            return l_name

    return None


def scrape_oddslot_listing(driver, db):
    """Scrape oddslot listing pages for today and tomorrow, filtering by league.
    
    If db_league_names is provided, only matches from fuzzy-matched league sections
    are included.
    Returns dict: (norm_home, norm_away) -> {home_percent, away_percent}
    """
    urls = [
        "https://oddslot.com/odds/?day=today",
        "https://oddslot.com/odds/?day=tomorrow"
    ]
    results = {}

    for url in urls:
        print(f"  [Oddslot Listing] {url}")
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        league_sections = soup.find_all("div", class_="drop-league")

        for section in league_sections:
            header = section.find("div", class_="drop-league__header")
            if not header:
                continue
            h4 = header.find("h4")
            if not h4:
                continue

            oddslot_league = _extract_league_from_h4(h4)

            matched = _match_league(oddslot_league, db)
            if not matched:
                print(f"    [Oddslot] Skipping league '{oddslot_league}' (no match in DB)")
                continue
            if oddslot_league != matched:
                print(f"    [Oddslot] League matched: '{oddslot_league}' -> '{matched}'")

            match_divs = section.find_all("div", class_="odds-match")
            for match_div in match_divs:
                home_el = match_div.find("a", class_="odds-match__team--home")
                away_el = match_div.find("a", class_="odds-match__team--away")
                if not home_el or not away_el:
                    continue

                home_team = home_el.find("span").get_text(strip=True)
                away_team = away_el.find("span").get_text(strip=True)

                chances = match_div.find_all("span", class_="odds-match__chance")
                home_pct = chances[0].get_text(strip=True).replace("%", "") if len(chances) >= 1 else ""
                away_pct = chances[1].get_text(strip=True).replace("%", "") if len(chances) >= 2 else ""

                key = (normalize_text(home_team), normalize_text(away_team))
                results[key] = {
                    "home_percent": home_pct,
                    "away_percent": away_pct,
                    "home_team": home_team, # store for fuzzy matching later
                    "away_team": away_team
                }

    return results


def _match_team_names(db_home, db_away, listing_home, listing_away):
    """Try multiple strategies to match DB team names vs listing team names."""
    listing_home = resolve_team_name(listing_home)
    listing_away = resolve_team_name(listing_away)
    nh = normalize_text(db_home)
    na = normalize_text(db_away)
    lh = normalize_text(listing_home)
    la = normalize_text(listing_away)

    # Strategy 1: exact match
    if nh == lh and na == la:
        return True
    # Strategy 2: reversed
    if nh == la and na == lh:
        return True

    # Strategy 3: substring (one contains the other)
    if (nh in lh or lh in nh) and (na in la or la in na):
        return True
    if (nh in la or la in nh) and (na in lh or lh in na):
        return True

    # Strategy 4: fuzzy match both sides
    home_ratio = difflib.SequenceMatcher(None, nh, lh).ratio()
    away_ratio = difflib.SequenceMatcher(None, na, la).ratio()
    if home_ratio >= 0.6 and away_ratio >= 0.6:
        return True
    home_ratio_r = difflib.SequenceMatcher(None, nh, la).ratio()
    away_ratio_r = difflib.SequenceMatcher(None, na, lh).ratio()
    if home_ratio_r >= 0.6 and away_ratio_r >= 0.6:
        return True

    return False


def _strip_common_prefix(name):
    """Strip common prefixes/suffixes from team names for matching."""
    n = name.lower().strip()
    prefixes = ["deportivo ", "fc ", "real ", "club ", "atletico ", "athletic "]
    for p in prefixes:
        if n.startswith(p):
            n = n[len(p):]
            break
    suffixes = [" fc", " sc", " cf", " fk", " united", " city"]
    for s in suffixes:
        if n.endswith(s):
            n = n[:-len(s)]
            break
    return normalize_text(n)


def scrape_oddslot(driver, db, match, oddslot_data=None):
    """Look up match percentages from pre-scraped oddslot listing data."""
    if not oddslot_data:
        return {}

    db_home = match["home_team"]
    db_away = match["away_team"]
    data = None

    # Try direct lookup first (fast path)
    key = (normalize_text(db_home), normalize_text(db_away))
    data = oddslot_data.get(key)
    if not data:
        key_rev = (normalize_text(db_away), normalize_text(db_home))
        data = oddslot_data.get(key_rev)

    # Strategy 4: iterate all listing entries and try fuzzy matching
    if not data:
        for (lh, la), odds in oddslot_data.items():
            if fuzzy_match(db_home, resolve_team_name(odds["home_team"]), is_team=True) and fuzzy_match(db_away, resolve_team_name(odds["away_team"]), is_team=True):
                data = odds
                break

    if data:
        print(f"  [Oddslot] {db_home} vs {db_away} -> Home: {data['home_percent']}%, Away: {data['away_percent']}%")
    else:
        print(f"  [Oddslot] {db_home} vs {db_away} -> not found in listing")

    return data or {}


def run_oddslot_only():
    """Only scrape Oddslot percentages — no FootyStats H2H or WinComparator."""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    valid_dates = get_today_tomorrow_dates()
    print(f"[Oddslot Only] Tarix filteri: {valid_dates}")

    matches = list(db.fixtures.find({
        "date": {"$in": valid_dates},
        "predictions.oddslot_stats": {"$exists": False},
    }))
    # Early exit check
    if not matches:
        print("[Oddslot Only] Bugun/sabah oddslot statistikasi olmayan fixture yoxdur. Scraper dayandirilir.")
        client.close()
        return

    def _create_driver():
        _cleanup_stale_chromedriver()
        opt = uc.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--incognito")
        return uc.Chrome(options=opt, version_main=148)

    driver = _create_driver()

    def _ensure_driver():
        nonlocal driver
        try:
            driver.current_url
        except:
            print(f"    [!] Window closed, recreating driver...")
            try:
                driver.quit()
            except:
                pass
            driver = _create_driver()

    try:
        _ensure_driver()
        db_league_names = list(set(m.get("league_name", "") for m in matches if m.get("league_name")))
        print(f"[Oddslot Only] Listing celinir (liqalar: {db_league_names})...")
        oddslot_data = scrape_oddslot_listing(driver, db)
        print(f"[Oddslot Only] Listing: {len(oddslot_data)} oyun tapildi.")

        matched = 0
        for m in matches:
            _ensure_driver()
            try:
                os_data = scrape_oddslot(driver, db, m, oddslot_data)
            except Exception as e:
                print(f"    [!] Oddslot error: {e}")
                os_data = None
            if os_data:
                db.fixtures.update_one(
                    {"_id": m["_id"]},
                    {"$set": {"predictions.oddslot_stats": os_data}}
                )
                matched += 1

            time.sleep(random.uniform(0.5, 1))

    finally:
        driver.quit()
        client.close()


def run():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    valid_dates = get_today_tomorrow_dates()
    print(f"[*] Tarix filteri: {valid_dates}")

    matches = list(db.fixtures.find({
        "date": {"$in": valid_dates},
        "$or": [
            {"predictions.wincomparator_link": {"$exists": True, "$ne": ""}},
            {"predictions.oddslot_link": {"$exists": True, "$ne": ""}},
            {"predictions.footystats_h2h_link": {"$exists": True, "$ne": ""}},
        ]
    }))

    # Early exit check
    if not matches:
        print("[!] Bugun/sabah ucun xarici linki olan fixture yoxdur. Scraper dayandirilir.")
        client.close()
        return

    def _create_driver():
        _cleanup_stale_chromedriver()
        opt = uc.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--incognito")
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        driver = uc.Chrome(options=opt, version_main=148)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    driver = _create_driver()

    try:
        fs_counter = 0
        for m in matches:
            update_data = {}
            fs_data = None
            wc_data = None

            def _ensure_driver():
                nonlocal driver
                try:
                    driver.current_url
                except:
                    print(f"    [!] Window closed, recreating driver...")
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = _create_driver()

            # FootyStats H2H — skip if no link or already has stats
            if m.get("predictions", {}).get("footystats_h2h_link") and not m.get("predictions", {}).get("footystats_stats"):
                _ensure_driver()
                try:
                    fs_data = scrape_footystats_h2h(driver, db, m)
                    if fs_data:
                        update_data["predictions.footystats_stats"] = fs_data
                except Exception as e:
                    print(f"    [!] FootyStats error: {e}")

            # WinComparator — skip if already has stats
            if not m.get("predictions", {}).get("wincomparator_stats"):
                _ensure_driver()
                try:
                    wc_data = scrape_wincomparator(driver, db, m)
                    if wc_data:
                        update_data["predictions.wincomparator_stats"] = wc_data
                except Exception as e:
                    print(f"    [!] WinComparator error: {e}")

            if update_data:
                db.fixtures.update_one({"_id": m["_id"]}, {"$set": update_data})
                print(f"    [+] Saved. FootyStats:{'OK' if fs_data else '-'} WinComp:{'OK' if wc_data else '-'}")
            else:
                print(f"    [!] No data scraped.")

            time.sleep(random.uniform(0.5, 1.5))

    finally:
        _safe_quit_driver(driver)
        client.close()


def run_footystats_predictions_only():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    valid_dates = get_today_tomorrow_dates()
    print(f"[FootyStats Only] Tarix filteri: {valid_dates}")

    matches = list(db.fixtures.find({
        "date": {"$in": valid_dates},
        "predictions.footystats_h2h_link": {"$exists": True, "$ne": ""},
        "predictions.footystats_stats": {"$exists": False},
    }))

    if not matches:
        print("[FootyStats Only] Bugun/sabah footystats linki olan ve ya statistikasi olmayan fixture yoxdur.")
        client.close()
        return

    print(f"[FootyStats Only] {len(matches)} fixture tapildi.")

    def _create_driver():
        _cleanup_stale_chromedriver()
        opt = uc.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--incognito")
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        driver = uc.Chrome(options=opt, version_main=148)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    scraped = 0
    for m in matches:
        print(f"  [FootyStats] {m['home_team']} vs {m['away_team']}")
        driver = _create_driver()
        try:
            fs_data = scrape_footystats_h2h(driver, db, m)
            if fs_data:
                db.fixtures.update_one(
                    {"_id": m["_id"]},
                    {"$set": {"predictions.footystats_stats": fs_data}}
                )
                scraped += 1
                print(f"    [+] FootyStats H2H saved.")
            else:
                print(f"    [!] No footystats data.")
        finally:
            _safe_quit_driver(driver)

        print(f"    15 saniye gozleme...")
        time.sleep(15)

    print(f"\n[FootyStats Only] {scraped}/{len(matches)} matca melumat yazildi.")
    client.close()
    return

    print(f"[FootyStats Only] {len(matches)} fixture tapildi.")
    _fetch_proxies()

    def _create_driver(proxy=None):
        opt = uc.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--incognito")
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        if proxy:
            opt.add_argument(f'--proxy-server={proxy}')
        driver = uc.Chrome(options=opt, version_main=148)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    scraped = 0
    prev_driver = None
    for m in matches:
        if prev_driver:
            try:
                prev_driver.close()
            except:
                pass
            try:
                prev_driver.quit()
            except:
                pass

        proxy = _next_proxy()
        print(f"  [FootyStats] {m['home_team']} vs {m['away_team']} (proxy: {proxy or 'yox'})")
        driver = _create_driver(proxy)
        try:
            fs_data = scrape_footystats_h2h(driver, db, m)
            if fs_data:
                db.fixtures.update_one(
                    {"_id": m["_id"]},
                    {"$set": {"predictions.footystats_stats": fs_data}}
                )
                scraped += 1
                print(f"    [+] FootyStats H2H saved.")
            else:
                print(f"    [!] No footystats data.")
        finally:
            try:
                driver.close()
            except:
                pass
            try:
                driver.quit()
            except:
                pass
            prev_driver = None

        time.sleep(2)

    print(f"\n[FootyStats Only] {scraped}/{len(matches)} matca melumat yazildi.")
    client.close()


def run_wincomparator_predictions_only():
    """Scrape only WinComparator predictions — no FootyStats or Oddslot."""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]

    valid_dates = get_today_tomorrow_dates()
    print(f"[WinComparator Only] Tarix filteri: {valid_dates}")

    matches = list(db.fixtures.find({
        "date": {"$in": valid_dates},
        "predictions.wincomparator_link": {"$exists": True, "$ne": ""},
        "predictions.wincomparator_stats": {"$exists": False},
    }))

    if not matches:
        print("[WinComparator Only] Bugun/sabah wincomparator linki olan ve ya statistikasi olmayan fixture yoxdur.")
        client.close()
        return

    print(f"[WinComparator Only] {len(matches)} fixture tapildi.")

    def _create_driver():
        _cleanup_stale_chromedriver()
        opt = uc.ChromeOptions()
        opt.add_argument("--no-sandbox")
        opt.add_argument("--window-size=1920,1080")
        opt.add_argument("--incognito")
        opt.add_argument("--disable-blink-features=AutomationControlled")
        opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        driver = uc.Chrome(options=opt, version_main=148)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    driver = _create_driver()

    def _ensure_driver():
        nonlocal driver
        try:
            driver.current_url
        except:
            print(f"    [!] Window closed, recreating driver...")
            try:
                driver.quit()
            except:
                pass
            driver = _create_driver()

    try:
        scraped = 0
        for m in matches:
            _ensure_driver()
            try:
                wc_data = scrape_wincomparator(driver, db, m)
            except Exception as e:
                print(f"    [!] WinComparator error: {e}")
                wc_data = None
            if wc_data:
                db.fixtures.update_one(
                    {"_id": m["_id"]},
                    {"$set": {"predictions.wincomparator_stats": wc_data}}
                )
                scraped += 1
                print(f"    [+] WinComparator saved.")
            else:
                print(f"    [!] No wincomparator data.")

            time.sleep(random.uniform(0.5, 1.5))

        print(f"\n[WinComparator Only] {scraped}/{len(matches)} matca melumat yazildi.")

    finally:
        _safe_quit_driver(driver)
        client.close()


def run_with_steps(steps=None):
    """Run specific external detail scrapers. steps=None means all steps."""
    if steps is None:
        steps = ["footystats", "wincomparator", "oddslot"]

    for step in steps:
        print(f"\n{'='*50}")
        print(f"EXTERNAL DETAILS: {step}")
        print(f"{'='*50}")
        try:
            if step == "footystats":
                run_footystats_predictions_only()
            elif step == "wincomparator":
                run_wincomparator_predictions_only()
            elif step == "oddslot":
                run_oddslot_only()
            else:
                print(f"  [!] Bilinmeyen step: {step}")
        except Exception as e:
            print(f"  [!] {step} xetasi: {e}")


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
    if steps:
        run_with_steps(steps)
    else:
        run()
