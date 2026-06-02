from pymongo import MongoClient
import os

mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = MongoClient(mongo_url)
db = client["football_prediction"]
pages_col = db["footystats_pages"]

doc = pages_col.find_one({"page": "predictions"})
if doc and doc.get("tables"):
    print("Fixtures in DB predictions:")
    for row in doc["tables"][0]["rows"]:
        print(f"- {row.get('Fixture')} | Market: {row.get('Market')} | Odds: {row.get('Odds')}")
client.close()
