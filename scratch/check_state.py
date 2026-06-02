from pymongo import MongoClient
from collections import Counter

c = MongoClient()
db = c["football_prediction"]

# Check Premier League
pl = db.leagues_config.find_one({"name": "Premier League"})
if pl:
    lid = str(pl["_id"])
    teams = db.teams.find({"league_id": lid}).sort("name", 1)
    print(f"=== Premier League ({db.teams.count_documents({'league_id': lid})} teams) ===")
    for t in teams:
        fs_logo = "FS" if "cdn.footystats" in (t.get("logo") or "") else "--"
        print(f"  #{t.get('name'):40s} logo={fs_logo} aliases={t.get('aliases', [])}")

# Check total and source of teams
total = db.teams.count_documents({})
fs_logo_count = db.teams.count_documents({"logo": {"$regex": "cdn\\.footystats"}})
print(f"\nTotal: {total}")
print(f"Footystats logo: {fs_logo_count}")

c.close()
