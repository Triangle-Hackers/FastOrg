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


async def require_auth(request: Request, token: str = Security(auth0_scheme)):

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
    1. Clear local session
    2. Construct absolute return URL
    3. Redirect to Auth0 logout with proper parameters
    
    Args:
        request: FastAPI Request object containing session to clear
    
    Returns:
        RedirectResponse: Redirects to Auth0's logout endpoint
    """
    # Clear the local session first
    request.session.clear()
    
    # Construct absolute return URL
    return_url = str(request.base_url)
    
    # Construct Auth0 logout URL with absolute return URL
    logout_url = (
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        f"client_id={os.getenv('AUTH0_CLIENT_ID')}&"
        f"returnTo={return_url}"
    )
    
    # Perform the redirect with explicit status code
    return RedirectResponse(url=logout_url, status_code=303)

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


# Protected route example that requires authentication
# Uses the require_auth dependency to ensure only authenticated users can access
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