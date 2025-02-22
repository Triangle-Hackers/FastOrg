from pymongo import MongoClient
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URI"))
db = client["memberdb"]
alerts_collection = db["alerts"]

alerts_collection.delete_many({})

alerts = []

# Through all orgs
for collection_name in db.list_collection_names():
    if collection_name == "alerts":
        continue

    collection = db[collection_name]

    for member in collection.find():
        gpa = float(member.get("GPA", 4.0))
        grad_year = member.get("Graduation Year", "")

        if gpa < 2.0:
            alerts.append({
                "organization_name": collection_name,
                "member_name": member["Name"],
                "alert_type": "low_gpa",
                "details": {"GPA": gpa},
                "timestamp": datetime.now()
            })

        curr_year = datetime.now().year
        if grad_year == str(curr_year):
            alerts.append({
                "organization": collection_name,
                "member_name": member['Name'],
                "alert_type": "graduation",
                "details": {"Graduation Year": grad_year},
                "timestamp": datetime.now()
            })

if alerts:
    alerts_collection.insert_many(alerts)