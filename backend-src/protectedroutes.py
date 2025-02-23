# subroutes.py
from fastapi import APIRouter, HTTPException, Depends, Request
import os
import requests
import secrets
import smtplib, ssl 
from authlib.integrations.requests_client import OAuth2Session
from create_org_mongo import create_org_mongo
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

@sub_router.get("/create-org/{org_name}")
async def create_org(
    org_name: str,
    request: Request):
    try:
        # User is already authenticated due to the require_auth dependency
        user = request.session["user"]
        
        domain = os.getenv("AUTH0_DOMAIN")
        client_id = os.getenv("AUTH0_CLIENT_ID")
        client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        
        # Get access token using the regular application credentials
        token_url = f"https://{domain}/oauth/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": f"https://{domain}/api/v2/",
            "grant_type": "client_credentials"
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
                'name': org_name,
                'display_name': org_name,
            }
        )
        
        if org_response.ok:
            auth0_org = org_response.json()
        elif org_response.status_code == 409:  # Conflict - org already exists
            # Get existing organization details
            get_org_response = requests.get(
                f"https://{domain}/api/v2/organizations/name/{org_name}",
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
        create_org_mongo(org_name)

        # Generate a new unique code for each org
        invite_code = secrets.token_urlsafe(8)
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["memberdb"]
        orgs_collection = db["organizations"]

        existing_code = orgs_collection.find_one({"invite_code": invite_code})
        while existing_code:
            invite_code = secrets.token_urlsafe(8)
            existing_code = orgs_collection.find_one({"invite_code": invite_code})

        # Saving the invite code
        orgs_collection.insert_one({
            "org_name": org_name,
            "invite_code": invite_code
        })

        client.close()
        
        return {
            "message": f"Organization '{org_name}' created successfully",
            "org_id": auth0_org['id'],
            "invite_code": invite_code
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))