import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING
import os
import sys

STATS_PAGES = [
    ("btts-stats", "Both Teams to Score (BTTS)", "/stats/btts-stats"),
    ("over15-goals", "Over 1.5 Goals", "/stats/over15-goals"),
    ("over25-goals", "Over 2.5 Goals", "/stats/over25-goals"),
    ("under25-goals", "Under 2.5 Goals", "/stats/under25-goals"),
    ("corner-stats", "Corner Stats", "/stats/corner-stats"),
    (
        "1st-2nd-half-goals",
        "First Half Goals & Second Half Goals",
        "/stats/1st-2nd-half-goals",
    ),
    ("scored-in-both-halves", "Scored In Both Halves", "/stats/scored-in-both-halves"),
    ("win-draw-win", "Win Draw Win", "/stats/win-draw-win"),
    ("referee-stats", "Referee Stats", "/stats/referee-stats"),
    ("card-stats", "Card Stats", "/stats/card-stats"),
    ("offside-stats", "Offsides", "/stats/offside-stats"),
    ("clean-sheet-stats", "Clean Sheets", "/stats/clean-sheet-stats"),
    ("common-score", "Common Scorelines", "/stats/common-score"),
    ("shots-on-target", "Shots On Target", "/stats/shots-on-target"),
    ("draws", "Football Draws", "/stats/draws"),
    ("predictions", "Predictions", "/predictions"),
]


def parse_table(table):
    rows = table.find_all("tr")
    if not rows:
        return [], []

    headers = []
    for th in rows[0].find_all("th"):
        for tooltip in th.find_all("div", class_="hover-modal-content"):
            tooltip.decompose()
        headers.append(th.get_text(strip=True))

    data = []
    for row in rows[1:]:
        tds = row.find_all("td")
        if not tds:
            continue
        entry = {}
        for i, td in enumerate(tds):
            col_name = headers[i] if i < len(headers) else f"col{i}"
            entry[col_name] = td.get_text(strip=True)
        data.append(entry)

    return headers, data


def scrape_predictions_page(soup):
    rows = []
    for bet in soup.find_all("div", class_="betWrapper"):
        header = bet.find("div", class_="betHeader")
        if not header: continue
        
        market_span = header.find("span", class_="market")
        market = market_span.get_text(strip=True) if market_span else ""
        
        title_div = header.find("div", class_="betHeaderTitle")
        fixture = ""
        if title_div:
            fixture = ''.join(node for node in title_div.find_all(string=True, recursive=False)).strip()
            
        meta_div = header.find("div", class_="betHeaderMeta")
        odds_val = ""
        if meta_div:
            odds_val = meta_div.get_text(strip=True).replace("To Play", "").strip()
            
        # Skip promo / junk blocks
        if not fixture or "see more" in fixture.lower() or "predictions" in fixture.lower():
            continue
        if not odds_val or odds_val in ["0.00", "0", "-", ""]:
            continue
            
        data_div = bet.find("div", class_="betData")
        league = ""
        date = ""
        win_pct_home = ""
        win_pct_away = ""
        ppg_home = ""
        ppg_away = ""
        avg_goals_home = ""
        avg_goals_away = ""

        if data_div:
            match_data = data_div.find("ul", class_="matchData")
            if match_data:
                for li in match_data.find_all("li"):
                    icon = li.find("i")
                    data_div_li = li.find("div", class_="data")
                    if icon and data_div_li:
                        icon_class = icon.get("class", [])
                        if "fa-calendar" in icon_class:
                            date = data_div_li.get_text(strip=True)
                        elif "fa-trophy" in icon_class:
                            league = data_div_li.get_text(strip=True)

            for sw in data_div.find_all("div", class_="statWrapper"):
                title = sw.find("div", class_="statTitle")
                if not title: continue
                title_text = title.get_text(strip=True)
                datas = sw.find_all("div", class_="statData")
                if len(datas) >= 2:
                    h_val = datas[0].get_text(strip=True)
                    a_val = datas[1].get_text(strip=True)
                    if "Win Percentage" in title_text:
                        win_pct_home, win_pct_away = h_val, a_val
                    elif "Points Per Game" in title_text:
                        ppg_home, ppg_away = h_val, a_val
                    elif "AVG Goals" in title_text:
                        avg_goals_home, avg_goals_away = h_val, a_val
                        
        rows.append({
            "Fixture": fixture,
            "Market": market,
            "Odds": odds_val,
            "Date": date,
            "League": league,
            "Win Pct (H)": win_pct_home,
            "Win Pct (A)": win_pct_away,
            "PPG (H)": ppg_home,
            "PPG (A)": ppg_away,
            "Goals (H)": avg_goals_home,
            "Goals (A)": avg_goals_away,
        })
        
    return [{"title": "Today's Predictions", "headers": ["Fixture", "Market", "Odds", "Date", "League", "Win Pct (H)", "Win Pct (A)", "PPG (H)", "PPG (A)", "Goals (H)", "Goals (A)"], "rows": rows}]


def extract_tables(soup):
    tables = []
    for table in soup.find_all("table", class_="full-league-table"):
        h2 = table.find_previous("h2")
        section_title = h2.get_text(strip=True) if h2 else "Unknown"
        headers, rows_data = parse_table(table)
        tables.append({"title": section_title, "headers": headers, "rows": rows_data})
    return tables


def classify_table(title):
    t = title.lower()
    if "potential" in t or "match" in t:
        return "potential"
    if "team" in t:
        return "top_teams"
    if "league" in t:
        return "top_leagues"
    return "other"


def scrape_all_footystats():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = MongoClient(mongo_url)
    db = client["football_prediction"]
    pages_col = db["footystats_pages"]
    flat_col = db["footystats_all"]

    # Drop existing data
    pages_col.drop()
    flat_col.drop()
    db["footystats_page_strategies"].drop()

    # Recreate indexes
    pages_col.create_index([("page", ASCENDING)], unique=True)

    driver = uc.Chrome(version_main=148)
    counter = 0

    for slug, page_title, path in STATS_PAGES:
        url = f"https://footystats.org{path}"
        try:
            driver.get(url)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            if slug == "predictions":
                tables = scrape_predictions_page(soup)
            else:
                tables = extract_tables(soup)

            doc = {
                "page": slug,
                "page_title": page_title,
                "url": url,
                "tables": tables,
            }
            pages_col.insert_one(doc)

            # Save to flat collection
            for tbl in tables:
                cls = classify_table(tbl["title"])
                for row in tbl["rows"]:
                    row["_stat_page"] = slug
                    row["_stat_title"] = page_title
                    row["_table_type"] = cls
                    row["_table_title"] = tbl["title"]
                if tbl["rows"]:
                    flat_col.insert_many(tbl["rows"])

            counter += 1
            if counter % 4 == 0:
                print("[scrapeFootyStats] Driver rotasiyasi: baglanir ve yeniden acilir...")
                driver.quit()
                driver = uc.Chrome(version_main=148)
                time.sleep(3)

        except Exception as e:
            print(f"[scrapeFootyStats] ERROR {slug}: {e}")

    driver.quit()
    client.close()


if __name__ == "__main__":
    scrape_all_footystats()

