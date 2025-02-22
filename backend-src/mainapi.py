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

import logging
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Update FastAPI app configuration with proper CORS settings
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,  # Important for cookies/session
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)



# Configure OAuth for login flow
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
async def require_auth(request: Request, token: str = Security(auth0_scheme)):
    """
    Authentication dependency that protects routes from unauthorized access.
    Checks both session and token-based authentication.
    """
    # First check session-based auth
    user = request.session.get("user")
    logger.info(f"Session data: {request.session}")
    logger.info(f"User data from session: {user}")
    
    if user:
        return user
        
    # If no session, verify token
    if token:
        try:
            logger.info(f"Received token: {token[:10]}...")  # Log first 10 chars of token
            
            # Create token object expected by Auth0 client
            token_obj = {
                "access_token": token,
                "token_type": "Bearer"
            }
            
            # Log the full token object for debugging
            logger.info(f"Using token object: {token_obj}")
            
            # Try direct HTTP headers approach
            headers = {
                "Authorization": f"Bearer {token}"
            }
            logger.info(f"Using headers: {headers}")
            
            # Get user info from Auth0 using the client's HTTP session
            userinfo = await oauth.auth0._client.get(
                "userinfo",
                headers=headers,
                token=token_obj
            )
            logger.info(f"Successfully got userinfo: {userinfo}")
            
            # Store the user info in session
            request.session["user"] = userinfo
            return userinfo
            
        except Exception as e:
            logger.error(f"Token verification failed - Full error: {str(e)}")
            logger.error(f"Token type: {type(token)}")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Token verification failed",
                    "message": str(e),
                    "token_type": str(type(token))
                }
            )
    
    # If neither session nor token authentication worked
    raise HTTPException(
        status_code=401, 
        detail={
            "error": "Not authenticated",
            "message": "No valid session or token found. Please ensure you are logged in.",
            "session_exists": bool(request.session),
            "token_provided": bool(token)
        }
    )

#######################
# Authentication Flow #
#######################

# Authentication Flow Routes
@app.get("/login")
async def login(request: Request):
    """
    Initiates the OAuth2 authentication flow with Auth0.
    This endpoint starts the login process by redirecting to Auth0's Universal Login Page.
    
    Args:
        request: FastAPI Request object
    
    Returns:
        RedirectResponse: Redirects to Auth0 login
        
    Raises:
        HTTPException: If authentication initialization fails
    """
    try:
        redirect_uri = "http://localhost:8000/auth"
        logger.info(f"Login attempt with redirect URI: {redirect_uri}")
        
        return await oauth.auth0.authorize_redirect(
            request,
            redirect_uri,
            response_type="code",
            scope="openid profile email"
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return RedirectResponse(url="http://localhost:5173?error=login_failed", status_code=302)

@app.get("/auth")
async def auth(request: Request):
    """
    OAuth2 callback endpoint that handles the response from Auth0.
    This endpoint completes the authentication flow and establishes the user session.
    """
    try:
        logger.info("Starting auth callback processing")
        token = await oauth.auth0.authorize_access_token(request)
        
        # Get user info directly instead of parsing id_token
        userinfo = await oauth.auth0.userinfo(token=token)

        request.session["user"] = userinfo
        return RedirectResponse(url="http://localhost:5173/home")
    except Exception as e:
        logger.error(f"Auth callback error: {str(e)}")
        return RedirectResponse(url="http://localhost:5173?error=auth_failed", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    """
    Handles user logout by clearing both local and Auth0 sessions.
    """
    request.session.clear()
    
    # Redirect to Auth0 logout with frontend return URL
    return_url = "http://localhost:5173"
    logout_url = (
        f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        f"client_id={os.getenv('AUTH0_CLIENT_ID')}&"
        f"returnTo={return_url}"
    )
    
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

@app.get("/verify-session")
async def verify_session(request: Request):
    """
    Verifies that the user's session is valid.
    """
    try:
        logger.info("Verifying session")
        logger.info(f"Session contents: {request.session}")
        
        if "user" not in request.session:
            logger.error("No user in session")
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Return user info if session is valid
        return {
            "status": "valid",
            "user": request.session["user"]
        }
    except Exception as e:
        logger.error(f"Session verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Session verification failed")