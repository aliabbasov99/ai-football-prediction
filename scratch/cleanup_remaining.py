from pymongo import MongoClient
import re

c = MongoClient()
db = c["football_prediction"]

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

leagues = list(db.leagues_config.find({}))
total_merged = 0
total_deleted = 0

for league in leagues:
    lid = str(league["_id"])
    teams = list(db.teams.find({"league_id": lid}))
    if len(teams) < 2:
        continue

    processed = set()
    for i, t in enumerate(teams):
        if str(t["_id"]) in processed:
            continue
        tn = norm(t["name"])
        for j, other in enumerate(teams):
            if i >= j or str(other["_id"]) in processed:
                continue
            on = norm(other["name"])
            if tn != on and (tn in on or on in tn):
                if len(t["name"]) > len(other["name"]):
                    dupe, keeper = t, other
                else:
                    dupe, keeper = other, t

                update = {}
                if dupe.get("logo") and not keeper.get("logo"):
                    update["logo"] = dupe["logo"]
                aliases_set = set(keeper.get("aliases") or [])
                for a in dupe.get("aliases", []):
                    if a not in aliases_set:
                        aliases_set.add(a)
                if dupe["name"] not in aliases_set:
                    aliases_set.add(dupe["name"])
                if aliases_set != set(keeper.get("aliases") or []):
                    update["aliases"] = list(aliases_set)
                if update:
                    db.teams.update_one({"_id": keeper["_id"]}, {"$set": update})
                    print(f"Merged {dupe['name']} -> {keeper['name']} ({league['name']})")
                    total_merged += 1
                db.teams.delete_one({"_id": dupe["_id"]})
                print(f"  Deleted: {dupe['name']}")
                total_deleted += 1
                processed.add(str(dupe["_id"]))
                break

print(f"\nDone! Merged: {total_merged}, Deleted: {total_deleted}")
c.close()
