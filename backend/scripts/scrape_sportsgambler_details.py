import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
import random
import re
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

def parse_sportsgambler_details(soup):
    data = {}
    
    # 1. Match Prediction
    # <a href="..." class="tpbot_tip"><span>Under 2.5 Goals @ 2.07</span></a>
    tip_tag = soup.find("a", class_="tpbot_tip")
    if tip_tag:
        data["prediction"] = tip_tag.get_text(strip=True)
    
    # 2. Correct Score
    # <span class="cs-score ..."><span class="cs-score-box">0</span><span class="cs-score-box split">-</span><span class="cs-score-box">2</span></span>
    score_container = soup.find("span", class_="cs-score")
    if score_container:
        boxes = score_container.find_all("span", class_="cs-score-box")
        if len(boxes) >= 2:
            # First box is home, last box is away
            home_score = boxes[0].get_text(strip=True)
            away_score = boxes[-1].get_text(strip=True)
            data["correct_score"] = f"{home_score}-{away_score}"
            
    return data

def run():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    valid_dates = get_today_tomorrow_dates()
    print(f"[*] Tarix filteri: {valid_dates}")
    fixtures = list(db.fixtures.find({
        "predictions.sportsgambler_link": {"$exists": True, "$ne": ""},
        "date": {"$in": valid_dates},
        "predictions.sportsgambler_stats": {"$exists": False},
    }))
    
    if not fixtures:
        print("[!] Bugun/sabah ucun sportsgambler linki olan ve statistikasi olmayan fixture yoxdur.")
        client.close()
        return
    print(f"[*] {len(fixtures)} fixture tapildi.")

    _cleanup_stale_chromedriver()
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--incognito")
    driver = uc.Chrome(options=options, version_main=148)
    
    try:
        for f in fixtures:
            url = f["predictions"]["sportsgambler_link"]
            print(f"[*] Scraping SportsGambler: {f['home_team']} vs {f['away_team']}")
            
            try:
                driver.get(url)
                time.sleep(10) # Wait for CF
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                details = parse_sportsgambler_details(soup)
                
                if details:
                    db.fixtures.update_one(
                        {"_id": f["_id"]},
                        {"$set": {"predictions.sportsgambler_stats": details}}
                    )
                    print(f"    [+] Saved: {details}")
                else:
                    print("    [!] Could not parse details.")
                    
            except Exception as e:
                print(f"    [!] Error: {e}")
            
            time.sleep(random.uniform(5, 8))
            
    finally:
        driver.quit()
        client.close()

if __name__ == "__main__":
    run()
