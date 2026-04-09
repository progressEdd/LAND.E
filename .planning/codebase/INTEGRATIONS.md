# External Integrations

**Analysis Date:** 2026-04-09

## APIs & External Services

### LLM Inference (Local-First)

All LLM backends are accessed through the webapp's settings panel. The backend uses a factory pattern to create `openai.OpenAI` clients with different `base_url` values.

- **Ollama** — Primary local LLM backend
  - SDK/Client: `ollama` Python package (>=0.6.1) for model listing; `openai.OpenAI` client with Ollama's OpenAI-compatible endpoint for chat completions
  - Default host: `http://localhost:11434`
  - Model listing: `ollama.list().model_dump()` (native SDK)
  - Chat: `OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` (OpenAI-compatible API)
  - Auth: None (local service, dummy API key `"ollama"`)

- **LM Studio** — Alternative local LLM backend (default)
  - SDK/Client: `openai.OpenAI` with LM Studio's OpenAI-compatible endpoint
  - Default host: `http://localhost:1234`
  - Auth: Dummy API key `"lm-studio"` (required by SDK, ignored by server)

- **llama.cpp** — Alternative local LLM backend
  - SDK/Client: `openai.OpenAI` with llama.cpp's OpenAI-compatible endpoint
  - Default host: `http://localhost:8080`
  - Auth: Dummy API key `"sk-no-key-required"` (required by SDK, ignored by server)

- **OpenAI** — Cloud LLM backend option
  - SDK/Client: `openai.OpenAI` (>=2.21.0)
  - Auth: `OPENAI_API_KEY` environment variable or entered via settings UI
  - Used for: `client.beta.chat.completions.parse()` structured output with Pydantic schemas

## Data Storage

### SQLite Database

- **Engine:** aiosqlite (async SQLite driver)
- **Location:** `backend/data/stories.db` (auto-created on startup)
- **Mode:** WAL journal mode, foreign keys enabled
- **Schema:** 5 tables managed by numbered migration SQL files
- **Size:** Grows with story count; typically small (KB to low MB)

### File Storage

- SQLite database file in `backend/data/`
- No file upload/download functionality
- Markdown export is generated in-memory and sent as HTTP response
- Frontend static assets in `frontend/static/`

### Caching

- Frontend caches loaded stories in `storyState.loadedStories` Map — avoids redundant API calls when switching stories
- No server-side caching — each request hits SQLite directly
- No Redis or external cache layer

## Authentication & Identity

- None. No user authentication. Local single-user application.
- LLM API keys entered at runtime via settings panel or read from environment variables
- Local backends (Ollama, LM Studio, llama.cpp) require no authentication

## Monitoring & Observability

### Error Tracking

- Backend: FastAPI `HTTPException` for REST errors, WebSocket `{type: "error"}` messages for generation failures
- Frontend: Error states displayed in UI components
- No error tracking service (Sentry, etc.)

### Logs

- No logging framework configured
- `uvicorn` outputs access logs to stdout when running
- No structured logging

## API Architecture

### REST Endpoints

**Stories (`/api/stories`):**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/stories` | List all stories (summaries) |
| POST | `/api/stories` | Create new story with root node |
| GET | `/api/stories/{id}` | Get story with full node tree |
| GET | `/api/stories/{id}/tree` | Get recursive tree for graph visualizer |
| DELETE | `/api/stories/{id}` | Delete story (cascading) |
| GET | `/api/stories/{id}/export` | Export as markdown file |
| PATCH | `/api/stories/{id}/active-path` | Switch active branch |
| POST | `/api/stories/{id}/nodes` | Create new node |
| PATCH | `/api/stories/{id}/nodes/{nid}` | Update node content + spans |
| POST | `/api/stories/{id}/nodes/{nid}/accept` | Accept draft node |
| POST | `/api/stories/{id}/nodes/{nid}/reject` | Reject draft node |
| GET | `/api/stories/random-premise` | Random story premise from pool |

**LLM (`/api/llm`):**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/llm/config` | Get current LLM config |
| POST | `/api/llm/config` | Set LLM backend config |
| GET | `/api/llm/models` | List available models |
| POST | `/api/llm/warmup` | Warm up a model |

**Health:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |

### WebSocket Endpoint

**`/ws/generate`** — AI generation streaming

Message types (client → server):
- `{type: "generate", story_id, model, node_id?, seed?}` — Start generation
- `{type: "cancel"}` — Cancel in-progress generation
- `{type: "accept", node_id, content, provenance_spans}` — Accept draft
- `{type: "reject", node_id}` — Reject draft

Message types (server → client):
- `{type: "draft_created", node_id}` — Draft node created in DB
- `{type: "token", content}` — Single character streamed to editor
- `{type: "complete", node_id, analysis}` — Generation finished with StoryAnalysis
- `{type: "cancelled", node_id}` — Generation was cancelled
- `{type: "accepted", node_id}` — Draft accepted
- `{type: "rejected", node_id}` — Draft rejected
- `{type: "error", message}` — Error occurred

### API Documentation

- OpenAPI/Swagger UI: `http://localhost:8000/docs` (auto-generated by FastAPI)

## Integration Patterns

### Universal LLM Client Pattern

All backends use the `openai.OpenAI` client with different `base_url` values:

```python
# Factory pattern in backend/app/services/llm.py
def create_llm_client(config: LLMBackendConfig) -> OpenAI:
    if config.backend == "lmstudio":
        return OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    elif config.backend == "ollama":
        return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    elif config.backend == "llamacpp":
        return OpenAI(base_url="http://localhost:8080/v1", api_key="sk-no-key-required")
    elif config.backend == "openai":
        return OpenAI(api_key=config.api_key)
```

### Structured Output Pattern

All LLM calls use OpenAI's beta structured output API with Pydantic schemas:

```python
parsed = await asyncio.to_thread(
    lambda: client.beta.chat.completions.parse(
        model=model,
        response_format=schema,  # Pydantic BaseModel class
        messages=messages,
        temperature=temperature,
    ).choices[0].message.parsed
)
return schema.model_validate(parsed)
```

### Async Wrapping Pattern

The OpenAI SDK is synchronous, so all calls are wrapped in `asyncio.to_thread()` for use with FastAPI's async handlers:

```python
result = await asyncio.to_thread(synchronous_llm_call, ...)
```

### Character Streaming Pattern

Generated text is streamed character-by-character with a 10ms delay for visual effect:

```python
for char in draft_text:
    if cancel_flag:
        break
    accumulated += char
    await websocket.send_json({"type": "token", "content": char})
    await asyncio.sleep(0.01)
```

### Git Submodule

- `01-dev-onboarding` submodule points to `https://github.com/progressEdd/dev-onboarding.git`
- Only exists on `master`/`development` branches, not on experiment branches

---

*Integration audit: 2026-04-09*
