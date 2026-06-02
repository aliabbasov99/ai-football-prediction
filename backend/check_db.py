from pymongo import MongoClient
import os

mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = MongoClient(mongo_url)
db = client["football_prediction"]
pages_col = db["footystats_pages"]

doc = pages_col.find_one({"page": "predictions"})
if doc:
    print("Found predictions page doc!")
    print("Tables count:", len(doc.get("tables", [])))
    if doc.get("tables"):
        t = doc["tables"][0]
        print("Table Title:", t.get("title"))
        print("Rows count:", len(t.get("rows", [])))
        if t.get("rows"):
            print("First row:", t["rows"][0])
else:
    print("Predictions page doc not found!")

# Print all page slugs in DB
print("All pages in DB:")
for d in pages_col.find({}, {"page": 1, "page_title": 1}):
    print(f"- {d.get('page')}: {d.get('page_title')}")
client.close()
