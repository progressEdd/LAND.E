"""LLM client factory, structured output parsing, and model discovery.

Ported from 02-worktrees/demo-marimo-app/app.py with async support for FastAPI.
"""

import asyncio
import os
import time
from typing import Any, Dict, Iterable, Sequence, Type, TypeVar

from openai import AsyncOpenAI, OpenAI

from app.models.schemas import LLMBackendConfig


T = TypeVar("T")


def _normalize_base_url(url: str) -> str:
    """Normalize a base URL to end with /v1.

    Ported from app.py lines 84-88.
    """
    url = (url or "").strip().rstrip("/")
    if not url:
        return url
    return url if url.endswith("/v1") else f"{url}/v1"


def _extract_ids(items: Iterable[Any]) -> list[str]:
    """Extract model IDs from an iterable of model objects or dicts.

    Ported from app.py lines 90-105.
    """
    out: list[str] = []
    for it in items or []:
        mid = getattr(it, "id", None)
        if mid is None and isinstance(it, dict):
            mid = it.get("id") or it.get("model")
        if isinstance(mid, str) and mid.strip():
            out.append(mid.strip())
    # stable order, unique
    seen: set[str] = set()
    uniq: list[str] = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def _try_client_models_list(client: Any) -> tuple[list[str], str | None]:
    """Try to list models via the OpenAI-compatible client.

    Ported from app.py lines 107-115.
    """
    try:
        resp = client.models.list()
        data = getattr(resp, "data", None)
        if data is None and isinstance(resp, dict):
            data = resp.get("data")
        return _extract_ids(data), None
    except Exception as e:
        return [], f"{type(e).__name__}: {e}"


def _try_ollama_list_models(ollama_host_url: str) -> tuple[list[str], str | None]:
    """List models via the Ollama Python SDK.

    Ported from app.py lines 117-152. Uses ollama.list().model_dump()
    and returns the `model` fields.
    """
    try:
        import ollama  # type: ignore
    except Exception as e:
        return [], f"ollama import failed: {type(e).__name__}: {e}"

    host = (ollama_host_url or "").strip().rstrip("/")
    # OLLAMA_HOST expects scheme+host+port (no /v1)
    prev = os.environ.get("OLLAMA_HOST")
    if host:
        os.environ["OLLAMA_HOST"] = host
    try:
        payload = ollama.list().model_dump()
        models: list[str] = []
        for m in (payload or {}).get("models", []):
            name = (m or {}).get("model")
            if isinstance(name, str) and name.strip():
                models.append(name.strip())
        # unique + keep order
        seen: set[str] = set()
        uniq: list[str] = []
        for x in models:
            if x not in seen:
                seen.add(x)
                uniq.append(x)
        return uniq, None
    except Exception as e:
        return [], f"{type(e).__name__}: {e}"
    finally:
        if prev is None:
            os.environ.pop("OLLAMA_HOST", None)
        else:
            os.environ["OLLAMA_HOST"] = prev


def create_llm_client(config: LLMBackendConfig) -> OpenAI:
    """Factory for sync LLM clients — supports lmstudio, ollama, openai, llamacpp.

    Ported from app.py lines 160-206 (excluding azure).
    """
    backend = config.backend

    if backend == "llamacpp":
        base_url = _normalize_base_url(config.base_url or "http://localhost:8080/v1")
        return OpenAI(base_url=base_url, api_key="sk-no-key-required")

    elif backend == "lmstudio":
        base_url = _normalize_base_url(config.base_url or "http://localhost:1234/v1")
        return OpenAI(base_url=base_url, api_key="lm-studio")

    elif backend == "ollama":
        host = (config.host or "").strip() or "http://localhost:11434"
        base_url = _normalize_base_url(host)
        return OpenAI(base_url=base_url, api_key="ollama")

    elif backend == "openai":
        return OpenAI(api_key=config.api_key or os.environ.get("OPENAI_API_KEY"))

    raise ValueError(f"Unknown backend: {backend}")


def create_async_llm_client(config: LLMBackendConfig) -> AsyncOpenAI:
    """Factory for async LLM clients — same backends as create_llm_client."""
    backend = config.backend

    if backend == "llamacpp":
        base_url = _normalize_base_url(config.base_url or "http://localhost:8080/v1")
        return AsyncOpenAI(base_url=base_url, api_key="sk-no-key-required")

    elif backend == "lmstudio":
        base_url = _normalize_base_url(config.base_url or "http://localhost:1234/v1")
        return AsyncOpenAI(base_url=base_url, api_key="lm-studio")

    elif backend == "ollama":
        host = (config.host or "").strip() or "http://localhost:11434"
        base_url = _normalize_base_url(host)
        return AsyncOpenAI(base_url=base_url, api_key="ollama")

    elif backend == "openai":
        return AsyncOpenAI(api_key=config.api_key or os.environ.get("OPENAI_API_KEY"))

    raise ValueError(f"Unknown backend: {backend}")


async def list_models(
    config: LLMBackendConfig,
) -> tuple[list[str], str | None]:
    """Create a client and return available models.

    For ollama, uses the native ollama SDK for model listing.
    For all others, uses the OpenAI-compatible models.list() endpoint.
    """
    if config.backend == "ollama":
        host = (config.host or "").strip() or "http://localhost:11434"
        return await asyncio.to_thread(_try_ollama_list_models, host)

    client = create_llm_client(config)

    if config.backend == "openai" and not (
        config.api_key or os.environ.get("OPENAI_API_KEY")
    ):
        return [], "No API key provided."

    return await asyncio.to_thread(_try_client_models_list, client)


async def parse_structured(
    client: OpenAI | AsyncOpenAI,
    *,
    model: str,
    schema: Type[T],
    user_content: str,
    system_content: str = "You are a helpful assistant. Follow the response model docstring.",
    temperature: float = 0.2,
    extra_messages: Sequence[Dict[str, str]] = (),
) -> T:
    """Parse structured output from the LLM using beta.chat.completions.parse.

    Works with both sync OpenAI and AsyncOpenAI clients.
    Sync clients are run in a threadpool.
    """
    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    messages += list(extra_messages)
    messages += [{"role": "user", "content": user_content}]

    if isinstance(client, AsyncOpenAI):
        response = await client.beta.chat.completions.parse(
            model=model,
            response_format=schema,
            messages=messages,
            temperature=temperature,
        )
        parsed = response.choices[0].message.parsed
    else:
        parsed = await asyncio.to_thread(
            lambda: client.beta.chat.completions.parse(
                model=model,
                response_format=schema,
                messages=messages,
                temperature=temperature,
            )
            .choices[0]
            .message.parsed
        )
    return schema.model_validate(parsed)


async def warmup_model(config: LLMBackendConfig, model: str) -> tuple[bool, str, float]:
    """Send a tiny request to warm up the model and return timing info.

    Ported from app.py lines 299-313.
    Returns (success, info_message, elapsed_seconds).
    """
    client = create_llm_client(config)

    def _warmup() -> tuple[bool, str]:
        t0 = time.time()
        try:
            client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helper."},
                    {"role": "user", "content": "hi"},
                ],
                temperature=0,
                max_tokens=1,
            )
            return True, f"{time.time() - t0:.2f}s"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

    t_start = time.time()
    success, info = await asyncio.to_thread(_warmup)
    elapsed = time.time() - t_start
    return success, info, elapsed
