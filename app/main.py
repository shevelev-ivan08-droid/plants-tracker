from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY, SESSION_COOKIE
from app.routers import auth, plants, waterings

app = FastAPI(title="Plant Watering Tracker")

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY, 
    session_cookie=SESSION_COOKIE
)

app.include_router(auth.router)
app.include_router(plants.router)
app.include_router(waterings.router)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(STATIC_DIR / "login.html")

@app.get("/register", include_in_schema=False)
def register_page():
    return FileResponse(STATIC_DIR / "register.html")