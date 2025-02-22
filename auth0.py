from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from dotenv import find_dotenv, load_dotenv
import os

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("APP_SECRET_KEY") 
)

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

# Auth routes
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")  # This creates the redirect URL dynamically
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.auth0.authorize_access_token(request)
        request.session["user"] = token
        return RedirectResponse(url="/")
    except Exception as e:
        return RedirectResponse(url="/login")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url=f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout?"
        f"client_id={os.getenv('AUTH0_CLIENT_ID')}&"
        f"returnTo={request.url_for('home')}"
    )

@app.get("/")
async def home(request: Request):
    user = request.session.get("user")
    if user:
        return {"user": user}
    return {"message": "Not logged in"}