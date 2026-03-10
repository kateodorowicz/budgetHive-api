"""BudgetHive API - FastAPI backend."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth, budgets, activities, revisions, shares, budget_analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="BudgetHive API",
    description="Backend for BudgetHive - budget storage and retrieval",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Lovable frontend
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Routes
app.include_router(auth.router)
app.include_router(budgets.router)
app.include_router(activities.router)
app.include_router(revisions.router)
app.include_router(shares.router)
app.include_router(budget_analysis.router)


@app.get("/")
def root():
    return {"message": "BudgetHive API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
