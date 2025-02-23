import re
import os
from typing import Any, Union
import json
from pymongo import MongoClient

def execute_mql(query_input: str) -> Union[Any, str]:
    """
    1. If 'query_input' is 'NO', return a specific message.
    2. If 'query_input' is recognized as a valid MQL query 
       (naively, if it starts with 'db.'), attempt to run that query 
       (here, we'll just simulate).
    3. Otherwise, return 'please try again'.
    """

    # Case 1: The user typed "NO"
    if query_input.strip() == "NO":
        return "Please type a valid goal related to your database"

    # Case 2: Naive check for MQL (e.g., starts with 'db.collection')
    # This is just a simplistic example: real logic would parse out
    # the collection name, the method (find, insert, etc.), and the arguments.
    # For demonstration, we'll check if it starts with 'db.' 
    # and has parentheses following the method call.
    
    # Example valid: db.users.find({ GPA: { $gt: 3 } })
    mql_pattern = r"^db\.\w+\.\w+\([^)]*\)$"
    match = re.match(mql_pattern, query_input.strip())
    if match:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["memberdb"]

        query_str = match.group(2)

        try:
            # Convert the query string to a dictionary
            query_dict = json.loads(query_str)

            # Perform the query
            collection = db["organizations"]
            results = collection.find(query_dict)

            # Convert results to a list and return
            return list(results)

        except json.JSONDecodeError:
            return ""

    # Case 3: Neither "NO" nor recognized as MQL
    return "Please try again"