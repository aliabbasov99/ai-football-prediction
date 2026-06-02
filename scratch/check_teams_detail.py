from pymongo import MongoClient

c = MongoClient()
db = c["football_prediction"]

# Find Premier League config
pl = db.leagues_config.find_one({"name": "Premier League"})
if pl:
    lid = str(pl["_id"])
    teams = list(db.teams.find({"league_id": lid}))
    print(f"Premier League teams ({len(teams)}):")
    for t in teams:
        logo_preview = t.get("logo", "")[:60]
        aliases = ", ".join(t.get("aliases", []))
        print(f'  {t["name"]:40s} logo={logo_preview:60s} aliases=[{aliases}]')

    # Check for duplicates by name
    from collections import Counter
    names = [t["name"] for t in teams]
    dupes = [(n, c) for n, c in Counter(names).items() if c > 1]
    if dupes:
        print(f"\nDuplicate names: {dupes}")
    else:
        print("\nNo duplicate names found")

c.close()
