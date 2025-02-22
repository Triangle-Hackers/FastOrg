from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://cadenedam:z2G3nyHF0Hfpn7UE@cluster0.e1ur4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

print("Databases:")
for db_name  in client.list_database_names():
    print(f"- {db_name}")