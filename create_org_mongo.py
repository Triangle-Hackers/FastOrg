from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def create_new_collection(db, name):
    collection_name = name.replace(" ", "_").lower()
    existing_collections = db.list_collection_names()
    
    if collection_name not in existing_collections:
        db.create_collection(collection_name)
    else:
        print("Name taken/Organization already exists!")

uri = "mongodb+srv://cadenedam:z2G3nyHF0Hfpn7UE@cluster0.e1ur4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["memberdb"]

org_name = "test" #gotta receive from user input
create_new_collection(db, org_name) 