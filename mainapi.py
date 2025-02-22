from typing import Union
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import find_dotenv, load_dotenv
from functools import wraps
from openai import OpenAI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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
        "scope": "openid profile email",
        "response_type": "code",
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

#########################
# Authentication System #
#########################

# Auth dependency for protected routes
async def require_auth(request: Request):
    """
    Authentication dependency that protects routes from unauthorized access.
    Used as a FastAPI dependency to enforce authentication on protected endpoints.
    
    Args:
        request: FastAPI Request object containing session data
    
    Returns:
        dict: User object from session if authenticated
    
    Raises:
        HTTPException: 401 error if user is not authenticated
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(require_auth)):
            return {"user": user}
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

#######################
# Authentication Flow #
#######################

# Authentication Flow Routes
@app.get("/login")
async def login(request: Request):
    """
    Initiates the OAuth2 authentication flow with Auth0.
    This endpoint starts the login process by redirecting to Auth0's Universal Login Page.
    
    Flow:
    1. User accesses /login endpoint
    2. Generate callback URL for Auth0 to return to
    3. Redirect user to Auth0's login page with proper OAuth2 parameters
    4. Auth0 handles user authentication
    5. User is redirected back to /auth endpoint after successful login
    
    Args:
        request: FastAPI Request object
    
    Returns:
        RedirectResponse: Redirects to Auth0's login page
    """
    redirect_uri = request.url_for("auth")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    """
    OAuth2 callback endpoint that handles the response from Auth0 after successful authentication.
    This endpoint completes the authentication flow and establishes the user session.
    
    Flow:
    1. Auth0 redirects user back to this endpoint with auth code
    2. Exchange auth code for access token
    3. Use access token to get user information
    4. Create user session
    5. Redirect to homepage
    
    Args:
        request: FastAPI Request object containing Auth0 callback data
    
    Returns:
        RedirectResponse: Redirects to homepage on success or login page on failure
    
    Error Handling:
        - Logs authentication errors
        - Redirects to login page if authentication fails
    """
    try:
        token = await oauth.auth0.authorize_access_token(request)
        userinfo = await oauth.auth0.userinfo(token=token)
        request.session["user"] = userinfo
        return RedirectResponse(url="/")
    except Exception as e:
        print(f"Auth error: {str(e)}")  # Log any authentication errors
        return RedirectResponse(url="/login")

@app.get("/logout")
async def logout(request: Request):
    """
    Handles user logout by clearing both local and Auth0 sessions.
    This endpoint ensures complete logout from both the application and Auth0.
    
    Flow:
    1. Clear local session data
    2. Redirect to Auth0's logout endpoint
    3. Auth0 clears its session
    4. User is logged out from both systems
    
    Args:
        request: FastAPI Request object containing session to clear
    
    Returns:
        RedirectResponse: Redirects to Auth0's logout endpoint
    
    Note:
        The Auth0 logout endpoint handles the final redirect back to the application
    """
    request.session.clear()
    return RedirectResponse(
        url=f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        f"client_id={os.getenv('AUTH0_CLIENT_ID')}"
    )

################
# API Routes   #
################

@app.get("/")
async def home(request: Request):
    """
    Public homepage endpoint that handles both authenticated and unauthenticated users.
    Demonstrates conditional response based on authentication status.
    
    Args:
        request: FastAPI Request object containing session data
    
    Returns:
        dict: Response containing welcome message and user data if authenticated
    """
    user = request.session.get("user")
    return {"message": "Welcome!", "user": user} if user else {"message": "Please log in"}

@app.get("/protected")
async def protected_route(user: dict = Depends(require_auth)):
    """
    Protected route that requires authentication to access.
    Demonstrates use of the require_auth dependency for route protection.
    
    Args:
        user: Dict containing user information, injected by require_auth dependency
    
    Returns:
        dict: Protected content including user info and authentication provider
    
    Note:
        The login_provider is extracted from the Auth0 'sub' claim which follows
        the format 'provider|user_id'
    """
    return {
        "message": "This is a protected route",
        "user": user,
        "login_provider": user.get('sub', '').split('|')[0]
    }

@app.post("/generate-sql")
async def generate_sql(prompt: str):
    """
    OpenAI-powered endpoint that generates SQL queries from natural language prompts.
    Uses GPT-3.5-turbo to convert English descriptions into SQL queries.
    
    Args:
        prompt: String containing natural language description of desired SQL query
    
    Returns:
        dict: Contains generated SQL and original prompt on success
        JSONResponse: Contains error details on failure
    
    Error Handling:
        - Returns 500 status code with error details if generation fails
        - Includes both error message and original error for debugging
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Configure and send request to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate only SQL code without explanation."},
                {"role": "user", "content": f"Generate SQL query for: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and return the generated SQL
        sql = response.choices[0].message.content.strip()
        return {
            "sql": sql,
            "prompt": prompt
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Failed to generate SQL"
            }
        )