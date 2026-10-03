import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .mongo import tips_collection
from .routers import analyze, auth, history, preferences, tips
from .seed_tips import seed as seed_tips

logger = logging.getLogger("outfit")

Base.metadata.create_all(bind=engine)

if tips_collection.count_documents({}) == 0:
    seed_tips()

if settings.jwt_secret == "change-me-in-production":
    logger.warning("JWT_SECRET is still the default value. Set a long random secret before deploying.")

app = FastAPI(title="Outfit Style Checker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(preferences.router)
app.include_router(tips.router)
app.include_router(analyze.router)
app.include_router(history.router)


@app.get("/api/health")
def health():
    return {"ok": True}


# In production the built React site lives in app/static and is served by this
# same app, so the website and the API share one address (no CORS problems).
_static_dir = Path(__file__).parent / "static"
if (_static_dir / "index.html").exists():
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
