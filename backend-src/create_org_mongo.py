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

        collection_name = org_name.replace(" ", "_").lower()
        org_collection = db[collection_name]

        # Schemas to be stored
        schema_collection = db["schemas"]
        schema_document = {
            "org_name": org_name,
            "fields": [
                {"name": "name", "label": "Enter your name", "type": "text", "required": True},
                {"name": "class", "label": "Year/Class", "type": "text", "required": True},
                {"name": "address", "label": "Home address", "type": "text", "required": False},
                {"name": "gpa", "label": "GPA", "type": "number", "required": False},
                {"name": "major", "label": "Major", "type": "text", "required": False},
                {"name": "grad", "label": "Expected Graduating Date", "type": "text", "required": True},
                {"name": "phone", "label": "Phone Number", "type": "text", "required": False},
                {"name": "email", "label": "Email Address", "type": "email", "required": True},
                {"name": "shirt", "label": "T-Shirt Size", "type": "text", "required": False}
            ]
        }

        existing_schema = schema_collection.find_one({"org_name": org_name})
        if not existing_schema:
            schema_collection.insert_one(schema_document)

        if org_collection.count_documents({}) == 0:
            org_collection.insert_one({"initialized": True})  # Placeholder document


        return True
        
    except Exception as e:
        print(f"Error creating organization: {e}")
        return False
        
    finally:
        client.close() 