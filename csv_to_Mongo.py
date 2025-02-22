import csv
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def main():
    uri = "mongodb+srv://cadenedam:z2G3nyHF0Hfpn7UE@cluster0.e1ur4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
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