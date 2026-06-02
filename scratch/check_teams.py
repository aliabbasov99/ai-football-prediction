from pymongo import MongoClient

c = MongoClient()
db = c["football_prediction"]
total = db.teams.count_documents({})
by_league = list(
    db.teams.aggregate([{"$group": {"_id": "$league_id", "count": {"$sum": 1}}}])
)
league_names = {
    str(l["_id"]): l["name"] for l in db.leagues_config.find({}, {"_id": 1, "name": 1})
}
print(f"Total teams: {total}")
for b in sorted(by_league, key=lambda x: -x["count"]):
    name = league_names.get(b["_id"], b["_id"])
    print(f"  {name}: {b['count']}")
c.close()
