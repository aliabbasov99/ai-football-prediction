from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from bs4 import BeautifulSoup
import os
from pymongo import MongoClient
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
        print("Waiting for page to load (15 seconds)...")
        time.sleep(15) 
        
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
        
        # Clear existing standings for this league
        collection.delete_many({"league_name": league_name})
        
        timestamp = datetime.datetime.now()
        for doc in data:
            doc["league_name"] = league_name
            doc["updated_at"] = timestamp
            
        if data:
            collection.insert_many(data)
            print(f"Successfully saved {len(data)} teams for {league_name} to MongoDB.")
        
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
            "name": "Eredivisie",
            "url": "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/10670/Stages/24872/Show/Netherlands-Eredivisie-2025-2026"
        }
    ]

    for league in leagues:
        fetch_and_parse_standings(league['url'], league['name'])
    print("Background scraping process completed.")

if __name__ == "__main__":
    run_all_scrapers()