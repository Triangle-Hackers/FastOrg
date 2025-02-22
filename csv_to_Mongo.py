import csv
from dotenv import find_dotenv, load_dotenv
import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def main():
    uri = os.getenv("MONGO_URI")
    
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    db = client["memberdb"]
    collection = db["members"]
    
    csv_path = "form_responses.csv" #Configure
    
    documents = []
    
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            checkEmail = row["Email"]
            if not collection.find_one({"email": checkEmail}):
                doc = {
                    "name": row["Enter your name"],
                    "class": row["Year/Class"],
                    "address": row["Home address"],
                    "gpa": row["GPA"],
                    "major": row["Major"],
                    "grad": row["Expected Graduating Date"],
                    "phone": row["Phone Number"],
                    "email": row["Email Address"],
                    "shirt": row["T-Shirt Size"]
                }
            
                documents.append(doc)
    
    if documents:
        collection.insert_many(documents)
    else:
        print("No CSV file or CSV empty")
    
    client.close()

if __name__ == "__main__":
    main()