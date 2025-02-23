from typing import Union, Dict, Any
from fastapi import FastAPI, Depends, Request, HTTPException, Security, Header
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2, OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import find_dotenv, load_dotenv
from functools import wraps
from openai import OpenAI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path  # Add this import
import json
from jose import jwt
from urllib.request import urlopen
from authlib.integrations.requests_client import OAuth2Session
from protectedroutes import sub_router  # Add this import
import requests
from pymongo import MongoClient
import pandas as pd
import logging
from fastapi.middleware.cors import CORSMiddleware
from components.schema_to_str import json_to_string
from fastapi.openapi.utils import get_openapi

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    tokenUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    refreshUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    scheme_name="Auth0",
    scopes={
        "openid": "OpenID Connect",
        "profile": "Profile",
        "email": "Email",
        "read:users": "Read user information"
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
        "usePkceWithAuthorizationCodeGrant": True,
        "additionalQueryStringParams": {
            "audience": os.getenv("AUTH0_AUDIENCE")
        }
    }
)

# Configure session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("APP_SECRET_KEY"),
    same_site="lax",   # Allows the cookie in cross-site requests during development
    https_only=False   # Disable secure flag for local HTTP testing
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"],  # Frontend URL
    allow_credentials=True,  # Important for cookies/session
    allow_methods=["*"],
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
        "scope": "openid profile email",  # Make sure 'email' is included
        "response_type": "code",
        "audience": os.getenv("AUTH0_AUDIENCE")
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
    use_state=False
)

#########################
# Authentication System #
#########################


ALGORITHMS = ["RS256"]
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('AUTH0_AUDIENCE')

def decode_jwt(token):
    # Decode the JWT token
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")



async def get_token(request: Request, authorization: str = Header(default=None)):
    """
    Get token from either Authorization header or session
    """
    token = None
    
    # Check Authorization header
    if authorization and isinstance(authorization, str) and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    # If no token in header, check session
    if not token:
        token = request.session.get("access_token")
        
    return token




# Replace the require_auth function with this updated version
async def require_auth(request: Request, token: str = Security(get_token)):
    # Log the token for debugging
    logger.info("Token from header or session: %s", token)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Get the JWKS from Auth0
        jwks = json.loads(urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").read())
        
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail = "Invalid Token: No matching key found")
            
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            request.state.user = payload
            return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid claims")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

#######################
# Authentication Flow #
#######################

# Authentication Flow Routes
@app.get("/login")
async def login(request: Request):
    """
    Initiates the OAuth2 authentication flow with Auth0.
    """
    try:
        redirect_uri = "http://localhost:8000/auth"
        logger.info(f"Login attempt with redirect URI: {redirect_uri}")
        
        return await oauth.auth0.authorize_redirect(
            request,
            redirect_uri,
            response_type="code",
            scope="openid profile email",
            audience=os.getenv("AUTH0_AUDIENCE")
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return RedirectResponse(url="http://localhost:5173?error=login_failed", status_code=302)

@app.get("/auth")
async def auth(request: Request):
    """
    OAuth2 callback endpoint that handles the response from Auth0.
    """
    try:
        token = await oauth.auth0.authorize_access_token(request)
        
        userinfo = await oauth.auth0.userinfo(token=token)
        
        # Verify the token and get claims
        access_token = token.get("access_token")
        if access_token:
            # Get the JWKS from Auth0
            jwks = json.loads(
                urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").read()
            )
            
            unverified_header = jwt.get_unverified_header(access_token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break

            if rsa_key:
                verified_claims = jwt.decode(
                    access_token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer=f"https://{AUTH0_DOMAIN}/"
                )
                # Merge verified claims with userinfo
                userinfo.update(verified_claims)
        
        # Store both token and verified userinfo in session
        request.session["user"] = {
            "sub": userinfo.get("sub"),
            "email": userinfo.get("email"),
            "nickname": userinfo.get("nickname"),
            "name": userinfo.get("name"),
            "picture": userinfo.get("picture")
        }
        request.session["access_token"] = access_token
        
        return RedirectResponse(url="http://localhost:5173/home")
    except Exception as e:
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
async def protected_route(request: Request, token_data: dict = Depends(require_auth)):
    """
    Protected route that requires authentication to access.
    """
    try:
        # Get the user info from the session
        user = request.session.get("user")
        
        if not user:
            logger.info("No user in session, using token data")
            # Instead of trying to fetch from Auth0 again, use the token_data
            # The token_data already contains the necessary user information
            user = {
                "sub": token_data.get("sub"),
                "email": token_data.get("email"),
                "nickname": token_data.get("nickname"),
                # Add any other relevant fields from token_data
            }
            # Store user info in session for future requests
            request.session["user"] = user
            
        return {
            "message": "This is a protected route",
            "token_data": token_data,
            "user_info": user,
            "login_provider": token_data.get('sub', '').split('|')[0]
        }
    except Exception as e:
        logger.error(f"Protected route error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/join-org")
async def join_org(
    invite_code: str,
    data: dict,
    request: Request):
    try:
        # Get the user from the session
        # user = request.session.get("user")
        # if not user:
        #     raise HTTPException(status_code=401, detail="Not authenticated")

        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["memberdb"]
        orgs_collection = db["organizations"]
        org_doc = orgs_collection.find_one({"invite_code": invite_code})

        if not org_doc:
            raise HTTPException(status_code=400, detail="Invalid Invite Code")
        
        org_name = org_doc["org_name"]
        collection_name = org_name.replace(" ", "_").lower()
        org_collection = db[collection_name]

        # get the schema for validation
        schema_collection = db["schemas"]
        schema_doc = schema_collection.find_one({"org_name": org_name})
        if not schema_doc:
            raise HTTPException(status_code=404, detail="Schema Not Found")

        # Update Auth0 user metadata with organization
        # auth0_client = await get_auth0_client()
        # auth0_response = auth0_client.patch(
        #     f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/users/{user['sub']}",
        #     json={
        #         "user_metadata": {
        #             "org_name": org_name
        #         }
        #     }
        # )

        # if not auth0_response.ok:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Failed to update user organization in Auth0"
        #     )
        
        required_fields = [field["name"] for field in schema_doc["fields"] if field["required"]]
        for field in required_fields:
            if field not in data or not data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")


        # Update session with new org_name
        # user['org_name'] = org_name
        # request.session["user"] = user
        # data["user_id"] = user["sub"]

        org_collection.insert_one(data)

        client.close()
        return {"message": f"You joined {org_name}"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/get-schema")
async def get_schema(invite_code: str):
    """
    We finna get org schema based on invite code
    """

    try:

        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["memberdb"]

        orgs_collection = db["organizations"]
        org_doc = orgs_collection.find_one({"invite_code": invite_code})

        if not org_doc:
            raise HTTPException(status_code=400, detail="Invalid Invite Code")
        
        org_name = org_doc["org_name"]

        schema_collection = db["schemas"]
        schema_doc = schema_collection.find_one({"org_name": org_name}, {"_id": 0})

        if not schema_doc:
            raise HTTPException(status_code=404, detail="Schema Not Found")
        
        return schema_doc
    
    except Exception as e:
        logging.error(f"Error fetching schema: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



# Include the subroutes under the /protected prefix
app.include_router(
    sub_router,
    prefix="/protected",
    dependencies=[Depends(require_auth)]
)



# OpenAI MQL generation endpoint
@app.post("/generate-mql")
async def generate_mql(request: Request):
    """
    Generates MongoDB query (MQL) based on natural language prompt using OpenAI
    Args:
        prompt: Natural language description of the desired MongoDB query
        schema: Optional collection schema information to guide query generation
    """
    try:
        data = await request.json()
        prompt = data.get("prompt")
        org_name = data.get("org_name")
        
        if not prompt or not org_name:
            raise HTTPException(status_code=400, detail="Missing Required Parameters")
        
        collection_name = org_name.replace(" ", "_").lower()

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Construct system message based on schema presence
        system_message = "You are a MongoDB expert. Generate only MongoDB query language (MQL) code without explanation."
        system_message += f"\nUse the following collection schema:\n{json_to_string('schema.json')}"
        system_message += "There are two cases: 1) The user is asking for a query to retrieve data. 2) the user is asking for something else"
        system_message += """If the user is asking for a query to retrieve data, generate the MQL query and 
        nothing else! If the user is asking for something else, generate the word NO in capital letters and 
        absolutely nothing else! Example query: 'Show members with GPA below 2.0' -> { 'gpa': { '$lt': 2.0 } }.
        ONLY return the query in JSON format, without explanation or additional text."""
        
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
        mql_query = response.choices[0].message.content.strip()

        try:
            mql_query = json.loads(mql_query)
        except:
            raise HTTPException(status_code=400, detail="Invalid MongoDB query generated")

        # Finna connect with databse
        mongo_client = MongoClient(os.getenv("MONGO_URI"))
        db = mongo_client["memberdb"]
        org_collection = db[collection_name]

        result = list(org_collection.find(eval(mql_query), {"_id": 0}))

        return {
            "query": mql_query,
            "result": result
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Failed to generate MongoDB query"
            }
        )
    
@app.get("/get-org-name")
async def get_org_name(request: Request):
    """
    Fetches the organization name of the currently logged-in user.
    """
    try:
        # Get token from request
        token = await get_token(request)
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Verify token and get claims
        token_data = await require_auth(request, token)
        
        # Connect to MongoDB
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["memberdb"]
        users_collection = db["users"]
        
        # Find user's organization
        user_doc = users_collection.find_one({"user_id": token_data["sub"]})
        if not user_doc or "org_name" not in user_doc:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return {"org_name": user_doc["org_name"]}

    except Exception as e:
        logger.error(f"Error fetching organization name: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/verify-session")
async def verify_session(request: Request):
    """
    Verifies that the user's session is valid.
    """
    try:
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        if "sub" not in user:
            raise HTTPException(status_code=401, detail=f"Missing 'sub' in session: {user}")

        return {
            "status": "valid",
            "user": user
        }
    except Exception as e:
      logger.error(f"Session verification error: {str(e)}")
      raise HTTPException(status_code=401, detail="Session verification failed")

async def get_auth0_client() -> OAuth2Session:
    """
    Creates an authenticated client for Auth0 Management API
    """
    # Create OAuth2 session with client credentials
    auth0_client = OAuth2Session(
        client_id=os.getenv("AUTH0_CLIENT_ID"),
        client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
        token_endpoint=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    )
    
    # Get access token for Management API
    token = auth0_client.fetch_token(
        url=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
        grant_type="client_credentials",
        audience=f"https://{os.getenv('AUTH0_DOMAIN')}/api/v2/"
    )
    
    return auth0_client
    
@app.get("/fetch-full-profile")
async def fetch_full_profile(request: Request):
    try:
        user = request.session.get("user")
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Check if user metadata is already in the session
        user_metadata = user.get('user_metadata')
        if user_metadata is None:
            # Fetch user metadata from an external service (e.g., Auth0)
            user_id = user["sub"]
            mgmt_token = await get_management_token()

            user_metadata = await fetch_user_metadata(user_id, mgmt_token)
            user['user_metadata'] = user_metadata
            request.session["user"] = user

        return {"user": user, "metadata": user_metadata}

    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    
async def get_management_token():
    token_url = f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token'
    token_payload = {
        'client_id': os.getenv('AUTH0_CLIENT_ID'),
        'client_secret': os.getenv('AUTH0_CLIENT_SECRET'),
        'audience': f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/',
        'grant_type': 'client_credentials',
        'scope': 'read:users'
    }

    response = requests.post(token_url, json=token_payload)
    response.raise_for_status()
    return response.json()['access_token']

async def fetch_user_metadata(user_id, mgmt_token):
    get_url = f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/users/{user_id}'
    response = requests.get(
        get_url,
        headers={'Authorization': f'Bearer {mgmt_token}'}
    )
    response.raise_for_status()
    return response.json().get('user_metadata', {})


@app.put("/update-nickname")
async def update_nickname(request: Request):
    try:
        data = await request.json()
        new_nickname = data.get('nickname')
        user_id = request.session["user"]["sub"]
        
        # Get Management API token
        token_response = requests.post(
            f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token',
            headers={'content-type': 'application/json'},
            json={
                'client_id': os.getenv('AUTH0_CLIENT_ID'),
                'client_secret': os.getenv('AUTH0_CLIENT_SECRET'),
                'audience': f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/',
                'grant_type': 'client_credentials'
            }
        )
        
        mgmt_token = token_response.json()['access_token']
        
        # Update user nickname
        update_response = requests.patch(
            f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/users/{user_id}',
            headers={
                'Authorization': f'Bearer {mgmt_token}',
                'Content-Type': 'application/json'
            },
            json={
                'nickname': new_nickname
            }
        )
        
        if update_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to update nickname")
            
        # Update session
        request.session["user"]["nickname"] = new_nickname
        
        return {"status": "success", "nickname": new_nickname}
        
    except Exception as e:
        logger.error(f"Error updating nickname: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update nickname")

@app.put("/complete-setup")
async def complete_setup(request: Request):
    """
    Marks user's setup as complete in Auth0, storing data in user_metadata if desired.
    """
    try:
        session_user = request.session.get("user")
        if not session_user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        user_id = session_user["sub"]
        body = await request.json()

        # Extract org_name from the request body
        org_name = body.get("org_name")
        if not org_name:
            raise HTTPException(status_code=400, detail="org_name is required")

        # Get existing user metadata first
        token_url = f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token'
        token_payload = {
            'client_id': os.getenv('AUTH0_CLIENT_ID'),
            'client_secret': os.getenv('AUTH0_CLIENT_SECRET'),
            'audience': f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/',
            'grant_type': 'client_credentials',
            'scope': 'update:users read:users'
        }

        token_response = requests.post(
            token_url,
            headers={'content-type': 'application/json'},
            json=token_payload
        )

        if not token_response.ok:
            raise HTTPException(status_code=500, detail="Could not get management token")

        mgmt_token = token_response.json()['access_token']

        # Get current user metadata
        get_url = f'https://{os.getenv("AUTH0_DOMAIN")}/api/v2/users/{user_id}'
        user_response = requests.get(
            get_url,
            headers={
                'Authorization': f'Bearer {mgmt_token}',
                'Content-Type': 'application/json'
            }
        )

        if not user_response.ok:
            raise HTTPException(status_code=400, detail="Failed to get current user metadata")


        # Merge existing metadata with new updates
        updated_metadata = {
            
        }

        # Patch user in Auth0 with merged metadata
        patch_response = requests.patch(
            get_url,
            headers={
                'Authorization': f'Bearer {mgmt_token}',
                'Content-Type': 'application/json'
            },
            json={
                "user_metadata": updated_metadata
            }
        )
        
        if not patch_response.ok:
            raise HTTPException(status_code=400, detail="Auth0 user update failed")

        # Update session with new metadata
        session_user['user_metadata'] = updated_metadata
        request.session["user"] = session_user

        return {"status": "success", "metadata": updated_metadata, "user": session_user}

    except HTTPException as e:
        raise e
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# Update the security definitions
app.openapi_schema = None  # Clear cached schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="OrgCRM",
        version="1.0.0",
        description="API with Auth0 authentication",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Auth0": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
                    "tokenUrl": f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
                    "refreshUrl": f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
                    "scopes": {
                        "openid": "OpenID Connect",
                        "profile": "Profile",
                        "email": "Email"
                    }
                }
            }
        }
    }
    
    # Add security requirement to all routes
    openapi_schema["security"] = [{"Auth0": ["openid", "profile", "email"]}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
