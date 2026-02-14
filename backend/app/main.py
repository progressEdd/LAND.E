"""FastAPI application entry point with CORS middleware."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — initialize database on startup."""
    await init_db()
    yield


app = FastAPI(title="AI Invasion", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
