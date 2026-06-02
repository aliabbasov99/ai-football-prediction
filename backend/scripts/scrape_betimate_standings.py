import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from pymongo import MongoClient


def _load_leagues():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["football_prediction"]
    configs = list(db["leagues_config"].find({"betimate_link": {"$ne": ""}}))
    client.close()
    return [{"name": c["name"], "betimate_link": c["betimate_link"], "league_id": str(c["_id"])} for c in configs]


def _first_match_url(driver, league_url):
    driver.get(league_url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    a_tag = soup.select_one("a.sports-team")
    if a_tag and a_tag.get("href"):
        href = a_tag["href"]
        if href.startswith("http"):
            return href
        return f"https://betimate.com{href}"
    return None


def scrape_all():
    print("[BetimateStandings] Basladi - betimate match page standings (sira ile).")

    leagues = _load_leagues()
    if not leagues:
        print("[BetimateStandings] Betimate linki olan liqa tapilmadi.")
        return

    service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for league in leagues:
            try:
                print(f"\n=== {league['name']} ===")
                league_url = league["betimate_link"] if league["betimate_link"].startswith("http") else f"https://betimate.com/en/football-predictions/{league['betimate_link']}"
                match_url = _first_match_url(driver, league_url)
                if not match_url:
                    print(f"  [{league['name']}] Hec bir oyun linki tapilmadi.")
                    continue
                print(f"  Match page: {match_url}")
                driver.get(match_url)
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                table = soup.find("table", class_="standing-table")
                if not table:
                    print(f"    [{league['name']}] standing-table tapilmadi.")
                    continue

                rows = table.find_all("tr", class_="table-league-row")
                if not rows:
                    print(f"    [{league['name']}] table-league-row tapilmadi.")
                    continue

                betimate_teams = []
                for row in rows:
                    pos_td = row.find("td", class_="pos")
                    team_td = row.find("td", class_="team")
                    if not pos_td or not team_td:
                        continue
                    a_tag = team_td.find("a")
                    if not a_tag:
                        continue
                    pos = pos_td.get_text(strip=True)
                    name = a_tag.get_text(strip=True)
                    betimate_teams.append((pos, name))

                if not betimate_teams:
                    print(f"    [{league['name']}] Betimate komanda adi tapilmadi.")
                    continue

                client = MongoClient("mongodb://localhost:27017/")
                db = client["football_prediction"]
                standings_col = db["standings"]
                teams_col = db["teams"]

                updated = 0
                for pos, bname in betimate_teams:
                    standing = standings_col.find_one({"league_name": league["name"], "rank": pos})
                    if not standing:
                        try:
                            standing = standings_col.find_one({"league_name": league["name"], "rank": str(int(pos))})
                        except ValueError:
                            pass
                    if not standing:
                        print(f"    [{league['name']}] #{pos} {bname} - standinqde tapilmadi")
                        continue

                    team_name = standing.get("team", "")
                    if not team_name:
                        continue

                    team_doc = teams_col.find_one({"name": team_name, "league_id": league["league_id"]})
                    if not team_doc:
                        print(f"    [{league['name']}] #{pos} {bname} -> {team_name} (teams-de yoxdur)")
                        continue

                    if bname not in team_doc.get("aliases", []):
                        teams_col.update_one({"_id": team_doc["_id"]}, {"$push": {"aliases": bname}})
                        print(f"    [{league['name']}] #{pos} {bname} -> {team_name} (alias)")
                        updated += 1
                    else:
                        print(f"    [{league['name']}] #{pos} {bname} -> {team_name} (var)")

                client.close()
                print(f"  [{league['name']}] {updated} yeni alias.")

            except Exception as e:
                print(f"[{league['name']}] Xeta: {e}")
    finally:
        driver.quit()

    print("\n[BetimateStandings] Tamamlandi.")


if __name__ == "__main__":
    scrape_all()
