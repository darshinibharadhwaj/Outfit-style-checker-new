from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .config import settings
from .routers import users, tips, analyze, history
from .mongo import tips_collection
from .seed_tips import seed as seed_tips

Base.metadata.create_all(bind=engine)

if tips_collection.count_documents({}) == 0:
    seed_tips()

app = FastAPI(title="Outfit Style Checker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(tips.router)
app.include_router(analyze.router)
app.include_router(history.router)


@app.get("/api/health")
def health():
    return {"ok": True}
