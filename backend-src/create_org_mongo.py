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


def create_org_mongo(org_name):
    if not org_name or not isinstance(org_name, str):
        raise ValueError("Organization name must be a non-empty string")

    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MongoDB URI not found in environment variables")

    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Test the connection
        client.admin.command('ping')
        
        db = client["memberdb"]
        create_new_collection(db, org_name)
        return True
        
    except Exception as e:
        print(f"Error creating organization: {e}")
        return False
        
    finally:
        client.close() 