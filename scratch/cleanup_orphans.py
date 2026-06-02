"""
Orphan teams silinir: əgər adı başqa bir komandanın alias-larındadırsa.
"""
from pymongo import MongoClient

c = MongoClient()
db = c["football_prediction"]
deleted = 0

leagues = list(db.leagues_config.find({}))
for league in leagues:
    lid = str(league["_id"])
    teams = list(db.teams.find({"league_id": lid}))
    for t in teams:
        tname = t["name"]
        # Check if this name exists as an alias for another team in the same league
        for other in teams:
            if other["_id"] == t["_id"]:
                continue
            if tname in (other.get("aliases") or []):
                db.teams.delete_one({"_id": t["_id"]})
                print(f"Deleted orphan: {tname} ({league['name']}) - alias of {other['name']}")
                deleted += 1
                break

print(f"\nTotal deleted: {deleted}")
c.close()
