import re as re2
from pymongo import MongoClient

c = MongoClient()
db = c["football_prediction"]

deleted_fs = 0
all_teams = list(db.teams.find({}))
for t in all_teams:
    logo = t.get("logo", "")
    if "cdn.footystats.org" in logo:
        db.teams.delete_one({"_id": t["_id"]})
        deleted_fs += 1
        print(f"Deleted: {t['name']}")

print(f"\nDeleted footystats-logo teams: {deleted_fs}")

deleted_orphans = 0
leagues = list(db.leagues_config.find({}))
for league in leagues:
    lid = str(league["_id"])
    teams = list(db.teams.find({"league_id": lid}))
    for t in teams:
        tname = t["name"]
        for other in teams:
            if other["_id"] == t["_id"]:
                continue
            if tname in (other.get("aliases") or []):
                db.teams.delete_one({"_id": t["_id"]})
                deleted_orphans += 1
                print(f"Deleted orphan: {tname} ({league['name']})")
                break

print(f"\nTotal: {deleted_fs} FS + {deleted_orphans} orphans")

c.close()
