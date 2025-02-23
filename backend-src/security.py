import os
import json
from jose import jwt
from urllib.request import urlopen
from fastapi import HTTPException, Request, Security, Header
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ALGORITHMS = ["RS256"]
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_AUDIENCE = os.getenv('AUTH0_AUDIENCE')

# Your auth0_scheme definition can remain here too.
class OAuth2AuthorizationCodeBearer(OAuth2):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        refreshUrl: str = None,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = False,  # Allow fallback
    ):
        flows = OAuthFlowsModel(
            authorizationCode={
                "authorizationUrl": authorizationUrl,
                "tokenUrl": tokenUrl,
                "refreshUrl": refreshUrl,
                "scopes": scopes or {},
            }
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

auth0_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/authorize",
    tokenUrl=f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
    scopes={
        "openid": "OpenID Connect",
        "profile": "Profile",
        "email": "Email"
    },
    auto_error=False
)

async def get_token_with_fallback(
    request: Request,
    token: str = Security(auth0_scheme)  # Swagger uses auth0_scheme here
):
    if token:
        logger.info("Token received from header: %s", token[:30] + "..." if len(token) > 30 else token)
        return token
    token = request.session.get("access_token")
    if token:
        logger.info("Token retrieved from session: %s", token[:30] + "..." if len(token) > 30 else token)
    else:
        logger.error("No token found in header or session.")
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token


async def require_auth(
    request: Request,
    token: str = Security(get_token_with_fallback)
):
    if token:
        logger.info("Token received: %s", token[:30] + "..." if len(token) > 30 else token)
    else:
        logger.error("No token found.")
    logger.info("Validating token: %s", token[:30] + "..." if len(token) > 30 else token)
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        logger.info("Fetching JWKS from: %s", jwks_url)
        jwks = json.loads(urlopen(jwks_url).read())
        logger.info("JWKS fetched successfully.")
        
        try:
            unverified_header = jwt.get_unverified_header(token)
            logger.info("Unverified header: %s", unverified_header)
        except Exception as e:
            logger.error("Error decoding token headers: %s", str(e))
            raise HTTPException(status_code=401, detail="Error decoding token headers.")
        
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if rsa_key:
            logger.info("RSA key found; decoding token.")
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            logger.info("Token decoded successfully. Payload: %s", payload)
            request.state.user = payload
            return payload
        else:
            logger.error("Unable to find appropriate RSA key for token header: %s", unverified_header)
            raise HTTPException(status_code=401, detail="Unable to find appropriate RSA key.")
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired.")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        logger.error("Invalid token claims.")
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except Exception as e:
        logger.exception("Error validating token:")
        raise HTTPException(status_code=401, detail=str(e))