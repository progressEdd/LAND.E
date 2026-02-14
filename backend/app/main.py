"""FastAPI application entry point with CORS middleware."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db
from app.routers.stories import router as stories_router
from app.routers.llm import router as llm_router
from app.routers.ws import router as ws_router


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

# Include routers
app.include_router(stories_router)
app.include_router(llm_router)
app.include_router(ws_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
