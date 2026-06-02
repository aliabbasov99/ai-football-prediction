"""
Birinci run-da yaranmış dublikat komandaları təmizləyir.
- "Arsenal" (əvvəldən var) + "Arsenal FC" (footystats əlavə edib) => birləşdir
- Qısa adlı saxlanılır, footystats adı alias-a əlavə edilir
- Footystats loqosu varsa və əskikdirsə, köçürülür
"""

from pymongo import MongoClient
import re

c = MongoClient()
db = c["football_prediction"]

leagues = list(db.leagues_config.find({}))
total_merged = 0
total_deleted = 0

for league in leagues:
    lid = str(league["_id"])
    teams = list(db.teams.find({"league_id": lid}))
    if len(teams) < 2:
        continue

    # Group by normalized name prefix
    by_prefix = {}
    for t in teams:
        n = t["name"]
        prefix = re.sub(r"\s*(FC|AFC|FK|SK|BK|IF|IK|IL|US|SC|FF|EC|CA|CR|CSD|AA|UMF|FH|KR|ÍF)\s*$", "", n).strip().lower()
        prefix = re.sub(r"[^a-z0-9]", "", prefix)
        by_prefix.setdefault(prefix, []).append(t)

    for prefix, group in by_prefix.items():
        if len(group) < 2:
            continue
        # Sort by name length - shorter is the "original"
        group.sort(key=lambda t: len(t["name"]))
        keeper = group[0]
        for dupe in group[1:]:
            update = {}
            # Merge footystats logo if keeper has none
            if dupe.get("logo") and not keeper.get("logo"):
                update["logo"] = dupe["logo"]
            # Merge aliases
            aliases_set = set(keeper.get("aliases") or [])
            for a in dupe.get("aliases", []):
                if a not in aliases_set:
                    aliases_set.add(a)
            if dupe["name"] not in aliases_set:
                aliases_set.add(dupe["name"])
            if aliases_set != set(keeper.get("aliases") or []) or update:
                update["aliases"] = list(aliases_set)
            if update:
                db.teams.update_one({"_id": keeper["_id"]}, {"$set": update})
                print(f"Merged {dupe['name']} -> {keeper['name']} ({league['name']})")
                total_merged += 1
            # Delete duplicate
            db.teams.delete_one({"_id": dupe["_id"]})
            print(f"  Deleted: {dupe['name']}")
            total_deleted += 1

print(f"\nDone! Merged: {total_merged}, Deleted: {total_deleted}")
c.close()
