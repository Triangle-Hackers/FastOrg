from dotenv import find_dotenv, load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def create_new_collection(db, name):
    collection_name = name.replace(" ", "_").lower()
    existing_collections = db.list_collection_names()
    
    if collection_name not in existing_collections:
        db.create_collection(collection_name)
    else:
        print("Name taken/Organization already exists!")

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["memberdb"]

org_name = "test" #gotta receive from user input
create_new_collection(db, org_name) 