"""
Protected Routes Module

This module contains routes that require authentication to access.
These routes are mounted under the /protected prefix in the main application.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
import os
import requests
from authlib.integrations.requests_client import OAuth2Session
from create_org_mongo import create_org_mongo

#######################
# Router Configuration #
#######################

sub_router = APIRouter()

#########################
# Auth0 Management API  #
#########################

async def get_auth0_client():
    """
    Creates an authenticated Auth0 Management API client.
    
    Flow:
    1. Get Auth0 management credentials from environment
    2. Request access token from Auth0
    3. Create OAuth2 session with token
    
    Returns:
        OAuth2Session: Authenticated client for Auth0 Management API
    
    Raises:
        HTTPException: If token acquisition fails or response is invalid
    """
    try:
        domain = os.getenv("AUTH0_DOMAIN")
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
        
        # Create and return authenticated session
        return OAuth2Session(token={"access_token": token_data["access_token"]})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth0 client creation failed: {str(e)}")

#######################
# Organization Routes #
#######################

@sub_router.get("/create-org/{org_name}")
async def create_org(
    org_name: str,
    request: Request
):
    """
    Creates a new organization in both Auth0 and MongoDB.
    
    Flow:
    1. Get authenticated user from session
    2. Get Auth0 access token
    3. Create organization in Auth0
    4. Add current user as admin
    5. Create organization in MongoDB
    
    Args:
        org_name: Name of the organization to create
        request: FastAPI Request object containing user session
    
    Returns:
        dict: Organization creation confirmation with org ID
    
    Raises:
        HTTPException: If any step of organization creation fails
    
    Note:
        - Requires authenticated user (handled by require_auth dependency)
        - Creates matching records in both Auth0 and MongoDB
        - Handles duplicate organization names
    """
    try:
        # Get authenticated user from session
        user = request.session["user"]
        
        # Get Auth0 application credentials
        domain = os.getenv("AUTH0_DOMAIN")
        client_id = os.getenv("AUTH0_CLIENT_ID")
        client_secret = os.getenv("AUTH0_CLIENT_SECRET")
        
        # Get access token
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
        
        # Set up request headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Create or get organization in Auth0
        auth0_org = None
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
        elif org_response.status_code == 409:  # Organization already exists
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
        
        # Add current user as organization admin
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
  
