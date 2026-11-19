from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY, SESSION_COOKIE
from app.routers import auth

app = FastAPI(title="Plant Watering Tracker")

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY, 
    session_cookie=SESSION_COOKIE
)

app.include_router(auth.router)