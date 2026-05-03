from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import os
from pymongo import MongoClient
import datetime

def save_to_mongodb(data, league_name):
    print(f"{league_name} melumatlari MongoDB-ye yazilir...")
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["football_prediction"]
        collection = db["fixtures"]
        
        # Əvvəlki oyunları təmizləyək ki, təkrarlanma olmasın
        collection.delete_many({"league_name": league_name})
        
        timestamp = datetime.datetime.now()
        
        # WhoScored-dan gələn qrupları (Həftə/Ay) cəmləyək
        documents_to_insert = []
        for group in data:
            for game in group["raw_data"]:
                if isinstance(game, dict):  # Əgər oyun düzgün formatdadırsa
                    doc = {
                        "league_name": league_name,
                        "group_name": group.get("group", ""),
                        "date": game.get("date", ""),
                        "time": game.get("time", ""),
                        "home_team": game.get("home", ""),
                        "away_team": game.get("away", ""),
                        "updated_at": timestamp
                    }
                    documents_to_insert.append(doc)
                    
        if documents_to_insert:
            collection.insert_many(documents_to_insert)
            print(f"{len(documents_to_insert)} oyun {league_name} uchun ugurla MongoDB-ye elave edildi.")
        else:
            print(f"{league_name} uchun uygun oyun tapilmadi.")
            
    except Exception as e:
        print(f"MongoDB-ye yazilarken xeta: {e}")

def fetch_and_parse_fixtures(url, league_name):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Commented out so you can see it if needed
    
    print(f"--- Processing Fixtures for {league_name} ---")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    fixtures_data = []

    try:
        driver.get(url)
        print("Sehife yuklenir, gozleyin (7 saniye)...")
        time.sleep(7) 
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        accordions = soup.find_all("div", class_=lambda x: x and "TournamentFixtures-module_accordion__" in x)
        
        print(f"Tapildi {len(accordions)} qrup oyunlar (Hefte ve ya Ay).")

        for acc in accordions:
            btn = acc.find("button")
            group_name = btn.text.strip() if btn else "Bilinmeyen Hefte/Ay"
            
            games_list = []
            
            import re
            
            # Səhifədəki bütün təmizlənmiş yazıları ardıcıl yığaq
            all_texts = list(acc.stripped_strings)
            
            # Unikal oyunları yığmaq üçün set kimi işlədəcəyik
            games_set = set()
            
            current_date = "Tarix tapilmadi"
            time_str = ""
            home_team = ""
            away_team = ""
            state = 'search'

            for text in all_texts:
                # Tarix blokunu aşkarlamaq: məs. "Saturday, Apr 18 2026"
                if re.match(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+[A-Za-z]+\s+\d{1,2}\s+\d{4}$", text):
                    current_date = text
                
                # Oyun vaxtını aşkarlamaq məs. "14:30"
                elif re.match(r"^\d{2}:\d{2}$", text):
                    time_str = text
                    state = 'wait_home'
                    
                # Ev sahibi komandanı gözləyərkən
                elif state == 'wait_home':
                    if text not in ['-', '1', 'X', '2', 'FT'] and not re.match(r"^\d+\.\d{2}$", text):
                        home_team = text
                        state = 'wait_away'
                        
                # Qonaq komandanı gözləyərkən
                elif state == 'wait_away':
                    if text not in ['-', '1', 'X', '2', 'FT'] and not re.match(r"^\d+\.\d{2}$", text):
                        away_team = text
                        
                        # Oyunu yaddaşa yazırıq
                        game_str = f"{current_date}|{time_str}|{home_team}|{away_team}"
                        if game_str not in games_set:
                            games_set.add(game_str)
                            games_list.append({
                                "date": current_date,
                                "time": time_str,
                                "home": home_team,
                                "away": away_team
                            })
                        state = 'search'
                        
            # Əgər əlavə edilmədisə
            if not games_list:
               games_list = ["Tapa bilmedik ve ya xususi format"]

            fixtures_data.append({
                "group": group_name,
                "raw_data": games_list
            })
            
    except Exception as e:
        print(f"Xeta bash verdi: {e}")
        
    finally:
        driver.quit()

    return fixtures_data

def run_all_fixture_scrapers():
    print("Oyunlarin (Fixtures) proqrami avtomatik bashladi...")
    leagues = [
        {
            "name": "Premier League",
            "url": "https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/10665/Stages/24867/Fixtures/England-Premier-League-2025-2026"
        },
        {
            "name": "La Liga",
            "url": "https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/11833/Stages/27339/Fixtures/Spain-La-Liga-2025-2026"
        },
        {
            "name": "Bundesliga",
            "url": "https://www.whoscored.com/regions/81/tournaments/3/seasons/10720/stages/24478/fixtures/germany-bundesliga-2025-2026"
        },
        {
            "name": "Serie A",
            "url": "https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/10672/Stages/24874/Fixtures/Italy-Serie-A-2025-2026"
        },
        {
            "name": "Ligue 1",
            "url": "https://www.whoscored.com/Regions/74/Tournaments/22/Seasons/10669/Stages/24871/Fixtures/France-Ligue-1-2025-2026"
        },
        {
            "name": "Brasileirao",
            "url": "https://www.whoscored.com/Regions/31/Tournaments/95/Seasons/11756/Stages/27234/Fixtures/Brazil-Serie-A-2025"
        },
        {
            "name": "Primeira Liga",
            "url": "https://www.whoscored.com/Regions/177/Tournaments/21/Seasons/10674/Stages/24877/Fixtures/Portugal-Primera-Liga-2025-2026"
        },
        {
            "name": "Eredivisie",
            "url": "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/10670/Stages/24872/Fixtures/Netherlands-Eredivisie-2025-2026"
        },
        {
            "name": "Primera Division",
            "url": "https://www.whoscored.com/Regions/11/Tournaments/68/Seasons/10893/Stages/25274/Fixtures/Argentina-Primera-Division-2025"
        },
        {
            "name": "Pro League",
            "url": "https://www.whoscored.com/Regions/4/Tournaments/36/Seasons/10686/Stages/24893/Fixtures/Belgium-First-Division-A-2025-2026"
        },
        {
            "name": "Super Lig",
            "url": "https://www.whoscored.com/Regions/215/Tournaments/17/Seasons/10888/Stages/25269/Fixtures/Turkey-Super-Lig-2025-2026"
        },
        {
            "name": "EFL Championship",
            "url": "https://www.whoscored.com/Regions/252/Tournaments/7/Seasons/10666/Stages/24868/Fixtures/England-Championship-2025-2026"
        },
        {
            "name": "Saudi Pro League",
            "url": "https://www.whoscored.com/Regions/195/Tournaments/349/Seasons/11390/Stages/26371/Fixtures/Saudi-Arabia-Pro-League-2025-2026"
        },
        {
            "name": "MLS",
            "url": "https://www.whoscored.com/Regions/233/Tournaments/85/Seasons/11768/Stages/27248/Fixtures/USA-Major-League-Soccer-2025"
        },
        {
            "name": "Czech First League",
            "url": "https://www.whoscored.com/Regions/44/Tournaments/37/Seasons/10691/Stages/24899/Fixtures/Czech-Republic-1-Liga-2025-2026"
        },
        {
            "name": "Super League Greece",
            "url": "https://www.whoscored.com/Regions/85/Tournaments/53/Seasons/10785/Stages/24999/Fixtures/Greece-Super-League-2025-2026"
        },
        {
            "name": "Liga Pro Ecuador",
            "url": "https://www.whoscored.com/Regions/60/Tournaments/447/Seasons/11800/Stages/27302/Fixtures/Ecuador-Liga-Pro-2025"
        },
        {
            "name": "Danish Superliga",
            "url": "https://www.whoscored.com/Regions/47/Tournaments/50/Seasons/10754/Stages/24963/Fixtures/Denmark-Superliga-2025-2026"
        },
        {
            "name": "Ekstraklasa",
            "url": "https://www.whoscored.com/Regions/173/Tournaments/84/Seasons/10783/Stages/24997/Fixtures/Poland-Ekstraklasa-2025-2026"
        },
        {
            "name": "J1 League",
            "url": "https://www.whoscored.com/Regions/107/Tournaments/96/Seasons/11753/Stages/27231/Fixtures/Japan-J1-League-2025"
        }
    ]

    all_data = {}
    
    for league in leagues:
        league_name = league["name"]
        league_url = league["url"]
        print(f"Bashlayiriq: {league_name}")
        fetched_data = fetch_and_parse_fixtures(league_url, league_name)
        all_data[league_name] = fetched_data
        
        # Save to MongoDB
        if fetched_data:
            save_to_mongodb(fetched_data, league_name)
        
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "all_fixtures_test.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        
    print("Butun fixture ugurla 'all_fixtures_test.json' faylina ve MongoDB-ye yazildi.")

if __name__ == "__main__":
    run_all_fixture_scrapers()
