from typing import Union
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import find_dotenv, load_dotenv
from functools import wraps

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = FastAPI()

# Configure session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("APP_SECRET_KEY")
)

# Setup OAuth for login flow
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email"
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Auth dependency for protected routes
async def require_auth(request: Request):
    """
    Dependency that checks if user is authenticated.
    Raises HTTPException if user is not logged in.
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

#######################
# Authentication Flow #
#######################

# Initiates the login process by redirecting to Auth0's Universal Login Page
# This is the entry point for user authentication
# Flow: User clicks login -> Redirected to Auth0 -> User authenticates -> Redirected back to /auth
@app.get("/login")
async def login(request: Request):
    """Initiates Auth0 authentication flow"""
    redirect_uri = request.url_for("auth")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

# Handles the callback from Auth0 after successful authentication
# This endpoint receives the authentication result and creates a user session
# Flow: Auth0 redirects here -> Verify token -> Create session -> Redirect to home
@app.get("/auth")
async def auth(request: Request):
    """
    Callback endpoint for Auth0 authentication.
    Stores user info in session upon successful login.
    """
    try:
        token = await oauth.auth0.authorize_access_token(request)
        userinfo = await oauth.auth0.parse_id_token(request, token)
        request.session["user"] = userinfo
        return RedirectResponse(url="/")
    except Exception as e:
        return RedirectResponse(url="/login")

# Handles user logout by clearing the session and redirecting to Auth0's logout endpoint
# This ensures both local and Auth0 sessions are terminated
# Flow: User clicks logout -> Clear local session -> Redirect to Auth0 logout -> Return to home
@app.get("/logout")
async def logout(request: Request):
    """
    Clears session and redirects to Auth0 logout endpoint
    """
    request.session.clear()
    return RedirectResponse(
        url=f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        f"client_id={os.getenv('AUTH0_CLIENT_ID')}&"
        f"returnTo={request.base_url}home"
    )

################
# API Routes   #
################

# Public homepage that displays different content based on authentication status
# Demonstrates conditional rendering without requiring authentication
@app.get("/")
async def home(request: Request):
    """
    Public route that shows different content for authenticated/unauthenticated users
    """
    user = request.session.get("user")
    if user:
        return {"message": "Welcome!", "user": user}
    return {"message": "Please log in"}

# Protected route example that requires authentication
# Uses the require_auth dependency to ensure only authenticated users can access
# Also extracts and returns the authentication provider information
@app.get("/protected")
async def protected_route(user: dict = Depends(require_auth)):
    """
    Protected route that requires authentication
    """
    return {
        "message": "This is a protected route",
        "user": user,
        "login_provider": user.get('sub', '').split('|')[0]
    }