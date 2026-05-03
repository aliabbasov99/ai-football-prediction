from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from bs4 import BeautifulSoup
import os
import re
from pymongo import MongoClient, UpdateOne
import datetime

def fetch_and_parse_standings(url, league_name):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Disabled so user can see it
    
    print(f"--- Processing {league_name} ---")
    print(f"Initializing Chrome Driver and navigating to {url}...")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        print("Waiting for page to load (7 seconds)...")
        time.sleep(7) 
        
        html_content = driver.page_source
        
        # Parse directly from variable
        standings_data = parse_standings_from_html(html_content, league_name)
        
        # Save to MongoDB
        if standings_data:
            save_to_mongodb(standings_data, league_name)
        else:
            print(f"No data extracted for {league_name}.")
            
    except Exception as e:
        print(f"An error occurred during process for {league_name}: {e}")
        
    finally:
        print("Closing the browser.")
        driver.quit()

def parse_standings_from_html(html_content, league_name):
    print(f"Parsing standings for {league_name}...")
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Locate the tbody with class 'standings'
    tbody = soup.find("tbody", class_="standings")
    
    if not tbody:
        print(f"Could not find tbody.standings for {league_name}. Searching for alternate structures...")
        table = soup.find("table", id=lambda x: x and "standings" in x and "grid" in x)
        if table:
            tbody = table.find("tbody")
    
    if not tbody:
        print(f"Could not find standings data for {league_name}.")
        return []

    standings = []
    rows = tbody.find_all("tr")
    print(f"Found {len(rows)} team rows.")

    for row in rows:
        try:
            # Rank
            rank_el = row.find("span", class_="box")
            rank = rank_el.text.strip() if rank_el else "N/A"

            # Team Name
            team_el = row.find("a", class_="team-link")
            team_name = team_el.text.strip() if team_el else "N/A"

            # Stats columns
            # played, won, drawn, lost, gf, ga, gd, pts
            played = row.find("td", class_="p").text.strip() if row.find("td", class_="p") else "0"
            won = row.find("td", class_="w").text.strip() if row.find("td", class_="w") else "0"
            drawn = row.find("td", class_="d").text.strip() if row.find("td", class_="d") else "0"
            lost = row.find("td", class_="l").text.strip() if row.find("td", class_="l") else "0"
            gf = row.find("td", class_="gf").text.strip() if row.find("td", class_="gf") else "0"
            ga = row.find("td", class_="ga").text.strip() if row.find("td", class_="ga") else "0"
            gd = row.find("td", class_="gd").text.strip() if row.find("td", class_="gd") else "0"
            pts = row.find("td", class_="pts").text.strip() if row.find("td", class_="pts") else "0"

            # Form (Last games)
            form_el = row.find("td", class_="form")
            form = [a.text.strip() for a in form_el.find_all("a")] if form_el else []
            
            # Structure the data
            team_data = {
                "rank": rank,
                "team": team_name,
                "played": int(played) if played.isdigit() else 0,
                "won": int(won) if won.isdigit() else 0,
                "drawn": int(drawn) if drawn.isdigit() else 0,
                "lost": int(lost) if lost.isdigit() else 0,
                "goals_for": int(gf) if gf.isdigit() else 0,
                "goals_against": int(ga) if ga.isdigit() else 0,
                "goal_difference": gd,
                "points": int(pts) if pts.isdigit() else 0,
                "last_games": form
            }
            standings.append(team_data)
        except Exception as e:
            print(f"Error parsing row: {e}")

    return standings

def save_to_mongodb(data, league_name):
    print(f"Saving data for {league_name} to MongoDB...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        collection = db["standings"]
        
        timestamp = datetime.datetime.now()
        operations = []
        for doc in data:
            doc["league_name"] = league_name
            doc["updated_at"] = timestamp
            
            operations.append(
                UpdateOne(
                    {"team": doc["team"], "league_name": league_name},
                    {"$set": doc},
                    upsert=True
                )
            )
            
        if operations:
            collection.bulk_write(operations)
            print(f"Successfully upserted {len(operations)} teams for {league_name} to MongoDB.")
        
    except Exception as e:
        print(f"An error occurred while saving to MongoDB: {e}")

def run_all_scrapers():
    print("Starting background scraping process...")
    leagues = [
        {
            "name": "Premier League",
            "url": "https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/10665/Stages/24867/Show/England-Premier-League-2025-2026"
        },
        {
            "name": "La Liga",
            "url": "https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/11833/Stages/27339/Show/Spain-La-Liga-2025-2026"
        },
        {
            "name": "Bundesliga",
            "url": "https://www.whoscored.com/regions/81/tournaments/3/seasons/10720/stages/24478/show/germany-bundesliga-2025-2026"
        },
        {
            "name": "Serie A",
            "url": "https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/10672/Stages/24874/Show/Italy-Serie-A-2025-2026"
        },
        {
            "name": "Ligue 1",
            "url": "https://www.whoscored.com/Regions/74/Tournaments/22/Seasons/10669/Stages/24871/Show/France-Ligue-1-2025-2026"
        },
        {
            "name": "Brasileirao",
            "url": "https://www.whoscored.com/Regions/31/Tournaments/95/Seasons/11756/Stages/27234/Show/Brazil-Serie-A-2025"
        },
        {
            "name": "Primeira Liga",
            "url": "https://www.whoscored.com/Regions/177/Tournaments/21/Seasons/10674/Stages/24877/Show/Portugal-Primera-Liga-2025-2026"
        },
        {
            "name": "Eredivisie",
            "url": "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/10670/Stages/24872/Show/Netherlands-Eredivisie-2025-2026"
        },
        {
            "name": "Primera Division",
            "url": "https://www.whoscored.com/Regions/11/Tournaments/68/Seasons/10893/Stages/25274/Show/Argentina-Primera-Division-2025"
        },
        {
            "name": "Pro League",
            "url": "https://www.whoscored.com/Regions/4/Tournaments/36/Seasons/10686/Stages/24893/Show/Belgium-First-Division-A-2025-2026"
        },
        {
            "name": "Super Lig",
            "url": "https://www.whoscored.com/Regions/215/Tournaments/17/Seasons/10888/Stages/25269/Show/Turkey-Super-Lig-2025-2026"
        },
        {
            "name": "EFL Championship",
            "url": "https://www.whoscored.com/Regions/252/Tournaments/7/Seasons/10666/Stages/24868/Show/England-Championship-2025-2026"
        },
        {
            "name": "Saudi Pro League",
            "url": "https://www.whoscored.com/Regions/195/Tournaments/349/Seasons/11390/Stages/26371/Show/Saudi-Arabia-Pro-League-2025-2026"
        },
        {
            "name": "MLS",
            "url": "https://www.whoscored.com/Regions/233/Tournaments/85/Seasons/11768/Stages/27248/Show/USA-Major-League-Soccer-2025"
        },
        {
            "name": "Czech First League",
            "url": "https://www.whoscored.com/Regions/44/Tournaments/37/Seasons/10691/Stages/24899/Show/Czech-Republic-1-Liga-2025-2026"
        },
        {
            "name": "Super League Greece",
            "url": "https://www.whoscored.com/Regions/85/Tournaments/53/Seasons/10785/Stages/24999/Show/Greece-Super-League-2025-2026"
        },
        {
            "name": "Liga Pro Ecuador",
            "url": "https://www.whoscored.com/Regions/60/Tournaments/447/Seasons/11800/Stages/27302/Show/Ecuador-Liga-Pro-2025"
        },
        {
            "name": "Danish Superliga",
            "url": "https://www.whoscored.com/Regions/47/Tournaments/50/Seasons/10754/Stages/24963/Show/Denmark-Superliga-2025-2026"
        },
        {
            "name": "Ekstraklasa",
            "url": "https://www.whoscored.com/Regions/173/Tournaments/84/Seasons/10783/Stages/24997/Show/Poland-Ekstraklasa-2025-2026"
        },
        {
            "name": "J1 League",
            "url": "https://www.whoscored.com/Regions/107/Tournaments/96/Seasons/11753/Stages/27231/Show/Japan-J1-League-2025"
        }
    ]

    for league in leagues:
        fetch_and_parse_standings(league['url'], league['name'])
    print("Background scraping process completed.")


# ---------------------------------------------------------------
# COMBINED LEAGUES LIST  (standings URL + fixtures URL birlikde)
# ---------------------------------------------------------------
COMBINED_LEAGUES = [
    {
        "name": "Premier League",
        "standings_url": "https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/10665/Stages/24867/Show/England-Premier-League-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/10665/Stages/24867/Fixtures/England-Premier-League-2025-2026",
    },
    {
        "name": "La Liga",
        "standings_url": "https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/11833/Stages/27339/Show/Spain-La-Liga-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/11833/Stages/27339/Fixtures/Spain-La-Liga-2025-2026",
    },
    {
        "name": "Bundesliga",
        "standings_url": "https://www.whoscored.com/regions/81/tournaments/3/seasons/10720/stages/24478/show/germany-bundesliga-2025-2026",
        "fixtures_url": "https://www.whoscored.com/regions/81/tournaments/3/seasons/10720/stages/24478/fixtures/germany-bundesliga-2025-2026",
    },
    {
        "name": "Serie A",
        "standings_url": "https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/10672/Stages/24874/Show/Italy-Serie-A-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/10672/Stages/24874/Fixtures/Italy-Serie-A-2025-2026",
    },
    {
        "name": "Ligue 1",
        "standings_url": "https://www.whoscored.com/Regions/74/Tournaments/22/Seasons/10669/Stages/24871/Show/France-Ligue-1-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/74/Tournaments/22/Seasons/10669/Stages/24871/Fixtures/France-Ligue-1-2025-2026",
    },
    {
        "name": "Brasileirao",
        "standings_url": "https://www.whoscored.com/Regions/31/Tournaments/95/Seasons/11756/Stages/27234/Show/Brazil-Serie-A-2025",
        "fixtures_url": "https://www.whoscored.com/Regions/31/Tournaments/95/Seasons/11756/Stages/27234/Fixtures/Brazil-Serie-A-2025",
    },
    {
        "name": "Primeira Liga",
        "standings_url": "https://www.whoscored.com/Regions/177/Tournaments/21/Seasons/10674/Stages/24877/Show/Portugal-Primera-Liga-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/177/Tournaments/21/Seasons/10674/Stages/24877/Fixtures/Portugal-Primera-Liga-2025-2026",
    },
    {
        "name": "Eredivisie",
        "standings_url": "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/10670/Stages/24872/Show/Netherlands-Eredivisie-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/10670/Stages/24872/Fixtures/Netherlands-Eredivisie-2025-2026",
    },
    {
        "name": "Primera Division",
        "standings_url": "https://www.whoscored.com/Regions/11/Tournaments/68/Seasons/10893/Stages/25274/Show/Argentina-Primera-Division-2025",
        "fixtures_url": "https://www.whoscored.com/Regions/11/Tournaments/68/Seasons/10893/Stages/25274/Fixtures/Argentina-Primera-Division-2025",
    },
    {
        "name": "Pro League",
        "standings_url": "https://www.whoscored.com/Regions/4/Tournaments/36/Seasons/10686/Stages/24893/Show/Belgium-First-Division-A-2025-2026",
        "fixtures_url": "https://www.whoscored.com/regions/22/tournaments/18/seasons/10759/stages/24549/fixtures/belgium-jupiler-pro-league-2025-2026",
    },
    {
        "name": "Super Lig",
        "standings_url": "https://www.whoscored.com/regions/22/tournaments/18/seasons/10759/stages/24549/show/belgium-jupiler-pro-league-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/215/Tournaments/17/Seasons/10888/Stages/25269/Fixtures/Turkey-Super-Lig-2025-2026",
    },
    {
        "name": "EFL Championship",
        "standings_url": "https://www.whoscored.com/Regions/252/Tournaments/7/Seasons/10666/Stages/24868/Show/England-Championship-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/252/Tournaments/7/Seasons/10666/Stages/24868/Fixtures/England-Championship-2025-2026",
    },
    {
        "name": "Saudi Pro League",
        "standings_url": "https://www.whoscored.com/regions/194/tournaments/282/seasons/10887/saudi-arabia-pro-league",
        "fixtures_url": "https://www.whoscored.com/regions/194/tournaments/282/seasons/10887/stages/24760/fixtures/saudi-arabia-pro-league-2025-2026",
    },
    {
        "name": "MLS",
        "standings_url": "https://www.whoscored.com/Regions/233/Tournaments/85/Seasons/11768/Stages/27248/Show/USA-Major-League-Soccer-2025",
        "fixtures_url": "https://www.whoscored.com/Regions/233/Tournaments/85/Seasons/11768/Stages/27248/Fixtures/USA-Major-League-Soccer-2025",
    },
    {
        "name": "Czech First League",
        "standings_url": "https://www.whoscored.com/regions/58/tournaments/78/seasons/10757/czech-republic-gambrinus-league",
        "fixtures_url": "https://www.whoscored.com/regions/58/tournaments/78/seasons/10757/stages/24547/fixtures/czech-republic-gambrinus-league-2025-2026",
    },
    {
        "name": "Super League Greece",
        "standings_url": "https://www.whoscored.com/regions/84/tournaments/65/greece-super-league",
        "fixtures_url": "https://www.whoscored.com/regions/84/tournaments/65/seasons/10776/stages/24570/fixtures/greece-super-league-2025-2026",
    },
    {
        "name": "Liga Pro Ecuador",
        "standings_url": "https://www.whoscored.com/Regions/60/Tournaments/447/Seasons/11800/Stages/27302/Show/Ecuador-Liga-Pro-2025",
        "fixtures_url": "https://www.whoscored.com/Regions/60/Tournaments/447/Seasons/11800/Stages/27302/Fixtures/Ecuador-Liga-Pro-2025",
    },
    {
        "name": "Danish Superliga",
        "standings_url": "https://www.whoscored.com/Regions/47/Tournaments/50/Seasons/10754/Stages/24963/Show/Denmark-Superliga-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/47/Tournaments/50/Seasons/10754/Stages/24963/Fixtures/Denmark-Superliga-2025-2026",
    },
    {
        "name": "Ekstraklasa",
        "standings_url": "https://www.whoscored.com/Regions/173/Tournaments/84/Seasons/10783/Stages/24997/Show/Poland-Ekstraklasa-2025-2026",
        "fixtures_url": "https://www.whoscored.com/Regions/173/Tournaments/84/Seasons/10783/Stages/24997/Fixtures/Poland-Ekstraklasa-2025-2026",
    },
    {
        "name": "J1 League",
        "standings_url": "https://www.whoscored.com/Regions/107/Tournaments/96/Seasons/11753/Stages/27231/Show/Japan-J1-League-2025",
        "fixtures_url": "https://www.whoscored.com/Regions/107/Tournaments/96/Seasons/11753/Stages/27231/Fixtures/Japan-J1-League-2025",
    },
]


def _parse_fixtures_from_html(html_content):
    """Parse fixtures from WhoScored HTML (same logic as getFixtureGames.py)."""
    soup = BeautifulSoup(html_content, "html.parser")
    accordions = soup.find_all(
        "div", class_=lambda x: x and "TournamentFixtures-module_accordion__" in x
    )

    fixtures_data = []
    for acc in accordions:
        btn = acc.find("button")
        group_name = btn.text.strip() if btn else "Unknown"
        games_list = []
        games_set = set()
        current_date = "Unknown"
        time_str = ""
        home_team = ""
        state = "search"

        for text in acc.stripped_strings:
            if re.match(
                r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2}\s+\d{4}$",
                text,
            ):
                current_date = text
            elif re.match(r"^\d{2}:\d{2}$", text):
                time_str = text
                state = "wait_home"
            elif state == "wait_home":
                if text not in ["-", "1", "X", "2", "FT"] and not re.match(r"^\d+\.\d{2}$", text):
                    home_team = text
                    state = "wait_away"
            elif state == "wait_away":
                if text not in ["-", "1", "X", "2", "FT"] and not re.match(r"^\d+\.\d{2}$", text):
                    away_team = text
                    key = f"{current_date}|{time_str}|{home_team}|{away_team}"
                    if key not in games_set:
                        games_set.add(key)
                        games_list.append(
                            {
                                "date": current_date,
                                "time": time_str,
                                "home": home_team,
                                "away": away_team,
                            }
                        )
                    state = "search"

        fixtures_data.append({"group": group_name, "raw_data": games_list})

    return fixtures_data


def _save_fixtures_to_mongodb(data, league_name):
    """Save parsed fixtures to MongoDB (mirrors getFixtureGames.save_to_mongodb)."""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        collection = db["fixtures"]
        collection.delete_many({"league_name": league_name})
        timestamp = datetime.datetime.now()
        docs = []
        for group in data:
            for game in group["raw_data"]:
                if isinstance(game, dict):
                    docs.append(
                        {
                            "league_name": league_name,
                            "group_name": group.get("group", ""),
                            "date": game.get("date", ""),
                            "time": game.get("time", ""),
                            "home_team": game.get("home", ""),
                            "away_team": game.get("away", ""),
                            "updated_at": timestamp,
                        }
                    )
        if docs:
            collection.insert_many(docs)
            print(f"[combined] {len(docs)} fixture {league_name} ucun MongoDB-ye yazildi.")
        else:
            print(f"[combined] {league_name} ucun fixture tapilmadi.")
    except Exception as e:
        print(f"[combined] Fixture MongoDB xetasi: {e}")


def run_all_combined():
    """
    Her liqa ucun tek bir Chrome sessiyasinda hem standings hem de
    fixtures-i goturup MongoDB-ye yazir.
    main.py-dakı /api/admin/scrape-all endpoint-i bunu cagirır.
    """
    print("[run_all_combined] Bashladi — standings + fixtures birlikde.")
    service = Service(ChromeDriverManager().install())

    for league in COMBINED_LEAGUES:
        league_name = league["name"]
        print(f"\n=== {league_name} ===")

        chrome_options = Options()
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # --- 1. STANDINGS ---
            print(f"[{league_name}] Standings yuklenir...")
            driver.get(league["standings_url"])
            time.sleep(7)
            standings_data = parse_standings_from_html(driver.page_source, league_name)
            if standings_data:
                save_to_mongodb(standings_data, league_name)
            else:
                print(f"[{league_name}] Standings tap\u0131lmad\u0131.")

            # --- 2. FIXTURES ---
            print(f"[{league_name}] Fixtures yuklenir...")
            driver.get(league["fixtures_url"])
            time.sleep(7)
            fixtures_data = _parse_fixtures_from_html(driver.page_source)
            if fixtures_data:
                _save_fixtures_to_mongodb(fixtures_data, league_name)
            else:
                print(f"[{league_name}] Fixture tap\u0131lmad\u0131.")

        except Exception as e:
            print(f"[{league_name}] Xeta: {e}")
        finally:
            driver.quit()

    print("\n[run_all_combined] Tamamlandi — standings + fixtures MongoDB-ye yazildi.")


if __name__ == "__main__":
    run_all_scrapers()