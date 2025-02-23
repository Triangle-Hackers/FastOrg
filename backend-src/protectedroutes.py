# subroutes.py
from fastapi import APIRouter, HTTPException, Depends, Request
import os
import requests
import secrets
import smtplib, ssl 
from authlib.integrations.requests_client import OAuth2Session
from create_org_mongo import create_org_mongo
import logging
import re

logger = logging.getLogger(__name__)
from pymongo import MongoClient


sub_router = APIRouter()

async def get_auth0_client():
    domain = os.getenv("AUTH0_DOMAIN")
    # Use Management API specific credentials
    client_id = os.getenv("AUTH0_MGMT_CLIENT_ID")
    client_secret = os.getenv("AUTH0_MGMT_CLIENT_SECRET")

    # Get management API access token
    token_url = f"https://{domain}/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": f"https://{domain}/api/v2/",
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, json=payload)

    # Add error handling for the token request
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to get Auth0 access token: {response.text}"
        )

    token_data = response.json()
    if 'access_token' not in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Auth0 response: {token_data}"
        )

    # Create OAuth2Session with the access token
    client = OAuth2Session(token={"access_token": token_data["access_token"]})
    return client

@sub_router.post("/create-org")
async def create_org(request: Request):
    try:
        # Get the request body
        body = await request.json()
        org_name = body.get("org_name")
        
        if not org_name:
            raise HTTPException(status_code=400, detail="Organization name is required")

        # Rest of your existing code...
        user = request.session.get("user")
        user_id = user['sub']
        formatted_org_name = re.sub(r'[^a-zA-Z0-9_-]', '', org_name).lower()

        if len(formatted_org_name) < 3:
            raise HTTPException(status_code=400, detail="Organization name must be at least 3 characters long.")
        
        if not user:
            logger.error("No user found in session")
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["memberdb"]
        orgs_collection = db["organizations"]
        schema_collection = db["schemas"]

        # checks to see if org alr exists
        existing_org = orgs_collection.find_one({"org_name": formatted_org_name})
        if existing_org:
            raise HTTPException(status_code=409, detail=f"Organization '{formatted_org_name}' already exists.") 

        domain = os.getenv("AUTH0_DOMAIN")
        client_id = os.getenv("AUTH0_CLIENT_ID")
        client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        
        # Get access token using the regular application credentials
        token_url = f"https://{domain}/oauth/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": f"https://{domain}/api/v2/",
            "grant_type": "client_credentials",
            "scope": "read:organizations read:users update:users"
        }
        
        response = requests.post(token_url, json=payload)
        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get access token: {response.text}"
            )
        
        token_data = response.json()
        access_token = token_data["access_token"]
        
        # Create organization using the access token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        auth0_org = None

        # Create organization in Auth0
        org_response = requests.post(
            f"https://{domain}/api/v2/organizations",
            headers=headers,
            json={
                'name': formatted_org_name,
                'display_name': org_name,
            }
        )
        
        if org_response.ok:
            auth0_org = org_response.json()
        elif org_response.status_code == 409:  # Conflict - org already exists
            # Get existing organization details
            get_org_response = requests.get(
                f"https://{domain}/api/v2/organizations/name/{formatted_org_name}",
                headers=headers
            )
            if not get_org_response.ok:
                raise HTTPException(
                    status_code=get_org_response.status_code,
                    detail=f"Failed to get existing organization: {get_org_response.text}"
                )
            auth0_org = get_org_response.json()
        else:
            raise HTTPException(
                status_code=org_response.status_code,
                detail=f"Failed to create organization: {org_response.text}"
            )
        
        # Add the current user as admin of the organization
        member_response = requests.post(
            f"https://{domain}/api/v2/organizations/{auth0_org['id']}/members",
            headers=headers,
            json={
                "members": [user['sub']]
            }
        )
        
        if not member_response.ok:
            raise HTTPException(
                status_code=member_response.status_code,
                detail=f"Failed to add member to organization: {member_response.text}"
            )
        
        # Create organization in MongoDB
        created = create_org_mongo(formatted_org_name)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to Create Organization in MongoDB")

        # Generate a new unique code for each org
        invite_code = secrets.token_urlsafe(8)

        existing_code = orgs_collection.find_one({"invite_code": invite_code})
        while existing_code:
            invite_code = secrets.token_urlsafe(8)
            existing_code = orgs_collection.find_one({"invite_code": invite_code})

        # Saving the invite code
        orgs_collection.insert_one({
            "org_name": formatted_org_name,
            "invite_code": invite_code
        })

        updated_metadata = {
            "org_name": formatted_org_name, "completed_setup": True
        }

        get_url = f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/users/{user_id}'
        patch_response = requests.patch(
            get_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={
                "user_metadata": updated_metadata
            }
        )
        
        if not patch_response.ok:
            raise HTTPException(
                status_code=patch_response.status_code,
                detail=f"Failed to update user metadata: {patch_response.text}"
            )
        
        schema_data = {
            "org_name": formatted_org_name,
                "fields": [
                    { "name": "name", "label": "Enter your name", "type": "text", "required": True },
                    { "name": "class", "label": "Year/Class", "type": "text", "required": True },
                    { "name": "address", "label": "Home address", "type": "text", "required": False },
                    { "name": "gpa", "label": "GPA", "type": "number", "required": False },
                    { "name": "major", "label": "Major", "type": "text", "required": False },
                    { "name": "grad", "label": "Expected Graduating Date", "type": "text", "required": True },
                    { "name": "phone", "label": "Phone Number", "type": "text", "required": False },
                    { "name": "email", "label": "Email Address", "type": "email", "required": True },
                    { "name": "shirt", "label": "T-Shirt Size", "type": "text", "required": False }
                    ]
        }

        existing_schema = schema_collection.find_one({"org_name": formatted_org_name})

        if not existing_schema:
            schema_collection.insert_one(schema_data)
        
        user['user_metadata'] = updated_metadata
        request.session["user"] = user

        client.close()
        
        return {
            "message": f"Organization '{org_name}' created successfully",
            "org_id": auth0_org['id'],
            "invite_code": invite_code
        }
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    
    
@sub_router.get("/get-roster")
async def get_roster(request: Request):
    """
    Retrieves the full roster of the authenticated user's organization.
    """
    user = request.session.get("user")
    
    # Log the saved user data
    logger.info(f"User data: {user}")
    
    if not user:
        logger.error("No user found in session")
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Log the user metadata to check its structure
    logger.info(f"User metadata: {user.get('user_metadata')}")  # Log user metadata

    # Get organization from user metadata
    org_name = user.get("user_metadata", {}).get("org_name")  # Access org_name from user_metadata
    logger.info(f"Retrieved organization name: {org_name}")  # Log the organization name

    if not org_name:
        logger.error("User is not part of any organization")
        raise HTTPException(status_code=400, detail="User is not part of any organization")

    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["memberdb"]
    org_collection = db[org_name.lower().replace(" ", "")]

    # Fetch all members
    members = list(org_collection.find({}, {"_id": 0}))  # Exclude MongoDB ObjectId

    client.close()

    return {"organization": org_name, "roster": members}