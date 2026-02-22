from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.db.database import engine, Base

# Import all models so SQLAlchemy creates tables
from app.models import user, market, price_entry  # noqa

app = FastAPI(
    title="FairPrice Tracker API",
    description="Crowd-sourced retail price tracking for Mumbai local markets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Update origins in production to your Vercel frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://your-app.vercel.app"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Create Tables ───────────────────────────────────────────────────────────
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


# ─── Routes ──────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "FairPrice Tracker", "version": "1.0.0"}
