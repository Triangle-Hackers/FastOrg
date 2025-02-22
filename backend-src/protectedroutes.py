# subroutes.py
from fastapi import APIRouter, HTTPException, Depends, Request
import os
import requests
from authlib.integrations.requests_client import OAuth2Session
from create_org_mongo import create_org_mongo
import logging

logger = logging.getLogger(__name__)

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
    request: Request
):
    try:
        # Get user data safely
        user = request.session.get("user")
        if not user:
            logger.error("No user found in session")
            raise HTTPException(status_code=401, detail="Not authenticated")
        
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
        
        return {
            "message": f"Organization '{org_name}' created successfully",
            "org_id": auth0_org['id']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
  
