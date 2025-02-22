import csv
from dotenv import find_dotenv, load_dotenv
import os
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

def load_schema(schema_path="schema.txt"):
    """
    Loads the schema mapping from schema.txt file.
    Each line in schema.txt represents a field name that maps to CSV columns.
    Args:
        schema_path: Path to the schema definition file
        
    Returns:
        list: List of field names to map from CSV to MongoDB
        
    Note:
        The schema file should contain one field name per line,
        matching the order of CSV columns
    """
    try:
        with open(schema_path, 'r') as f:
            # Remove empty lines and whitespace
            schema = [line.strip() for line in f.readlines() if line.strip()]
        return schema
    except Exception as e:
        print(f"Error loading schema: {str(e)}")
        return None
    
def main():
    uri = os.getenv("MONGO_URI")
    
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    db = client["memberdb"]
    collection = db["members"]
    
    csv_path = "form_responses.csv" #Configure
    
    documents = []
    
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        schema = json.load(open("schema.json"))
        
        for row in reader:
            checkEmail = row["Email"]
            if not collection.find_one({"email": checkEmail}):
                doc = { 
                    mongo_field: row[csv_field] 
                    for mongo_field, csv_field in schema.items()
                }
            
                documents.append(doc)
    
    if documents:
        collection.insert_many(documents)
    else:
        print("No CSV file or CSV empty")
    
    client.close()

if __name__ == "__main__":
    main()