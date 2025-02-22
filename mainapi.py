from typing import Union
from fastapi import FastAPI, Depends, Request, HTTPException, Security
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import find_dotenv, load_dotenv
from functools import wraps
from openai import OpenAI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from protectedroutes import sub_router  # Add this import

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Add OAuth2 scheme for Swagger UI
class OAuth2AuthorizationCodeBearer(OAuth2):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        refreshUrl: str = None,
        scheme_name: str = None,
        scopes: dict = None,
    ):
        flows = OAuthFlowsModel(
            authorizationCode={
                "authorizationUrl": authorizationUrl,
                "tokenUrl": tokenUrl,
                "refreshUrl": refreshUrl,
                "scopes": scopes or {},
            }
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=True)

# Configure OAuth2 scheme
auth0_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    tokenUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    scopes={
        "openid": "OpenID Connect",
        "profile": "Profile",
        "email": "Email"
    }
)

# Update FastAPI app configuration
app = FastAPI(
    title="OrgCRM",
    description="API with Auth0 authentication",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "clientId": os.getenv("AUTH0_CLIENT_ID"),
        "clientSecret": os.getenv("AUTH0_CLIENT_SECRET"),
        "scopes": ["openid", "profile", "email"],
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

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
        "scope": "openid profile email",
        "response_type": "code",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Update the require_auth dependency to use the OAuth2 scheme
async def require_auth(request: Request, token: str = Security(auth0_scheme)):
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
        userinfo = await oauth.auth0.userinfo(token=token)
        request.session["user"] = userinfo
        return RedirectResponse(url="/")
    except Exception as e:
        print(f"Auth error: {str(e)}")  # Add logging for debugging
        return RedirectResponse(url="/login")

# Handles user logout by clearing the session and redirecting to Auth0's logout endpoint
# This ensures both local and Auth0 sessions are terminated
# Flow: User clicks logout -> Clear local session -> Redirect to Auth0 logout -> Return to home
@app.get("/logout")
async def logout(request: Request):
    """
    Clears session and redirects to Auth0 logout endpoint
    """
    try:
        request.session.clear()
        # Ensure we're using the correct Auth0 domain and parameters
        logout_url = (
            f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
            f"client_id={os.getenv('AUTH0_CLIENT_ID')}&"
            f"returnTo=http://localhost:8000"
        )
        print(f"Redirecting to: {logout_url}")  # Debug log
        return RedirectResponse(
            url=logout_url,
            status_code=302
        )
    except Exception as e:
        print(f"Logout error: {str(e)}")  # Debug log
        # Fallback to home page if something goes wrong
        return RedirectResponse(url="/", status_code=302)

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
    return {"message": "Welcome!", "user": user} if user else {"message": "Please log in"}

# Protected route example that requires authentication
# Uses the require_auth dependency to ensure only authenticated users can access
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

# Include the subroutes under the /protected prefix
app.include_router(
    sub_router,
    prefix="/protected",
    dependencies=[Depends(require_auth)]
)

# OpenAI MQL generation endpoint
@app.post("/generate-mql")
async def generate_mql(prompt: str, schema: Union[str, None] = None):
    """
    Generates MongoDB query (MQL) based on natural language prompt using OpenAI
    Args:
        prompt: Natural language description of the desired MongoDB query
        schema: Optional collection schema information to guide query generation
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Construct system message based on schema presence
        system_message = "You are a MongoDB expert. Generate only MongoDB query language (MQL) code without explanation."
        if schema:
            system_message += f"\nUse the following collection schema:\n{schema}"
        
        # Create the completion request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Generate MongoDB query for: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the MQL from response
        mql = response.choices[0].message.content.strip()
        
        return {
            "mql": mql,
            "prompt": prompt,
            "schema": schema
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Failed to generate MongoDB query"
            }
        )