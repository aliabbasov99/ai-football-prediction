import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import re
import unicodedata

# Config
DB_NAME = "football_prediction"
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")


def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def fuzzy_match(name1, name2):
    n1 = normalize_text(name1)
    n2 = normalize_text(name2)
    return n1 in n2 or n2 in n1

def run():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        print("[*] Fetching SportsGambler links from tips page...")
        url = "https://www.sportsgambler.com/betting-tips/"
        driver.get(url)
        time.sleep(15)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all("a", class_="betlist-item")
        print(f"[*] Found {len(items)} possible match links.")
        
        updated = 0
        for item in items:
            league_tag = item.find("span", class_="betlist-league")
            if not league_tag: continue
            sg_league = league_tag.get_text(strip=True)
            
            teams_span = item.find("span", class_="betlist-teams")
            if not teams_span: continue
            tags = teams_span.find_all("span")
            if len(tags) < 2: continue
            
            h_name = tags[0].get_text(strip=True)
            a_name = tags[1].get_text(strip=True)
            link = item.get("href")
            
            # Find matching fixtures in DB
            # We filter by any league for now
            fixtures = list(db.fixtures.find({}))
            for f in fixtures:
                if fuzzy_match(f["home_team"], h_name) and fuzzy_match(f["away_team"], a_name):
                    db.fixtures.update_one(
                        {"_id": f["_id"]},
                        {"$set": {"predictions.sportsgambler_link": f"https://www.sportsgambler.com{link}"}}
                    )
                    print(f"    [+] Linked: {f['home_team']} vs {f['away_team']}")
                    updated += 1
                    break
        print(f"[*] Finished. Total links updated: {updated}")
        
    finally:
        driver.quit()
        client.close()

if __name__ == "__main__":
    run()
