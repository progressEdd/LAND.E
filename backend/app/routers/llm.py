"""REST API endpoints for LLM backend configuration and model management."""

from pydantic import BaseModel
from fastapi import APIRouter

from app.models.schemas import LLMBackendConfig
from app.services.llm import list_models, warmup_model


router = APIRouter(prefix="/api/llm", tags=["llm"])


# Server-side state for LLM config (single-user app)
_current_config = LLMBackendConfig()


# ---------- Request models ----------


class WarmupRequest(BaseModel):
    """Request body for model warmup."""

    model: str


# ---------- Endpoints ----------


@router.post("/config", response_model=LLMBackendConfig)
async def set_llm_config(config: LLMBackendConfig):
    """Set the LLM backend configuration."""
    global _current_config
    _current_config = config
    return _current_config


@router.get("/config", response_model=LLMBackendConfig)
async def get_llm_config():
    """Get the current LLM backend configuration."""
    return _current_config


@router.get("/models")
async def get_models():
    """List available models for the current backend."""
    models, error = await list_models(_current_config)
    return {"models": models, "error": error}


@router.post("/warmup")
async def do_warmup(req: WarmupRequest):
    """Warm up the current model."""
    success, message, elapsed = await warmup_model(_current_config, req.model)
    return {"success": success, "message": message, "elapsed": elapsed}
