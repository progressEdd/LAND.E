# External Integrations

**Analysis Date:** 2026-02-13

## APIs & External Services

**LLM Inference (Local-First):**

All LLM backends are accessed via the marimo app at `02-worktrees/demo-marimo-app/app.py`. The app uses a radio button to select the active backend.

- **Ollama** - Primary local LLM backend
  - SDK/Client: `ollama` Python package (>=0.5.3) for model listing; `openai.OpenAI` client with Ollama's OpenAI-compatible endpoint for chat completions
  - Default host: `http://localhost:11434`
  - Model listing: `ollama.list().model_dump()` (native SDK)
  - Chat: `OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` (OpenAI-compatible API)
  - Auth: None (local service, dummy API key `"ollama"` passed to satisfy SDK requirement)
  - Models tested: `gemma2:9b-instruct-fp16`, `gemma2:27b-instruct-q6_K`, `gemma3:12b-it-q8_0`, `gemma3:27b-it-q4_K_M`, `qwen3:30b-a3b-instruct-2507-q4_K_M`, `gpt-oss:latest`, and others (see `02-worktrees/experiments-with-models/`)

- **LM Studio** - Alternative local LLM backend
  - SDK/Client: `openai.OpenAI` with LM Studio's OpenAI-compatible endpoint
  - Default host: `http://localhost:1234/v1`
  - Auth: Dummy API key `"lm-studio"` (required by SDK, ignored by server)
  - Configuration: Via marimo UI form in `02-worktrees/demo-marimo-app/app.py`

- **llama.cpp** - Alternative local LLM backend
  - SDK/Client: `openai.OpenAI` with llama.cpp's OpenAI-compatible endpoint
  - Default host: `http://localhost:8080/v1`
  - Auth: Dummy API key `"sk-no-key-required"` (required by SDK, ignored by server)
  - Configuration: Via marimo UI form in `02-worktrees/demo-marimo-app/app.py`

**LLM Inference (Cloud):**

- **OpenAI API** - Cloud LLM backend option
  - SDK/Client: `openai.OpenAI` (>=1.101.0)
  - Auth: `OPENAI_API_KEY` environment variable or entered via marimo UI password field
  - Used for: `client.beta.chat.completions.parse()` structured output with Pydantic schemas
  - Configuration: Via marimo UI form in `02-worktrees/demo-marimo-app/app.py`

- **Azure OpenAI** - Cloud LLM backend option
  - SDK/Client: `openai.AzureOpenAI` (part of `openai` package)
  - Auth: `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` environment variables or entered via marimo UI
  - API version: `2024-08-01-preview` (default, configurable)
  - Models: User-provided comma-separated deployment names (Azure uses deployment names, not model IDs)
  - Configuration: Via marimo UI form in `02-worktrees/demo-marimo-app/app.py`

## Data Storage

**Databases:**
- None. No database is used. All state is in-memory within the marimo reactive session.

**File Storage:**
- Local filesystem only
- Marimo layout stored as JSON: `02-worktrees/demo-marimo-app/layouts/app.grid.json`
- Marimo session state: `02-worktrees/demo-marimo-app/__marimo__/session/app.py.json`
- Experiment notebooks stored as `.ipynb` files on the `experiments-with-models` branch
- No file upload/download functionality in the app

**Caching:**
- None. No caching layer. Each LLM call is a fresh HTTP request.

## Authentication & Identity

**Auth Provider:**
- None. No user authentication. The app is a local single-user tool.
- LLM API keys are entered at runtime via marimo UI forms or read from environment variables (`OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`)
- Local backends (Ollama, LM Studio, llama.cpp) require no authentication

## Monitoring & Observability

**Error Tracking:**
- None. Errors are caught in try/except blocks and displayed in the marimo UI as `mo.md()` callouts.
- Error pattern in `02-worktrees/demo-marimo-app/app.py`:
  ```python
  try:
      _start = parse_structured(...)
  except Exception as e:
      set_start_err(f"{type(e).__name__}: {e}")
      status_ui = mo.md(f"**Error:** `{get_start_err()}`")
  ```

**Logs:**
- No logging framework. No `logging` module usage.
- Model warm-up timing displayed in marimo UI via progress bar.

## CI/CD & Deployment

**Hosting:**
- Local only. No deployment target. Run via `uv run marimo run app.py`.

**CI Pipeline:**
- None. No GitHub Actions, no CI configuration files.

**Deployment process:**
- Clone repo, set up worktree, `uv sync`, run marimo. No build step.

## Environment Configuration

**Required env vars:**
- None are strictly required. All API keys can be entered via the marimo UI at runtime.

**Optional env vars:**
- `OPENAI_API_KEY` - Used by `openai.OpenAI()` if no key provided in UI
- `AZURE_OPENAI_API_KEY` - Used by `openai.AzureOpenAI()` if no key provided in UI
- `AZURE_OPENAI_ENDPOINT` - Used by `openai.AzureOpenAI()` if no endpoint provided in UI
- `OLLAMA_HOST` - Temporarily set by the app when listing Ollama models (restored after call)

**Secrets location:**
- No `.env` files committed or present locally
- `00-supporting-files/data/sample.env.file` exists as a reference template (not used at runtime)
- All secrets entered via marimo UI password fields or read from shell environment

## Webhooks & Callbacks

**Incoming:**
- None. The app does not expose any HTTP endpoints.

**Outgoing:**
- None. All external communication is client-initiated HTTP requests to LLM APIs.

## Integration Patterns

**Universal Client Pattern:**
All backends (except Ollama model listing) use the `openai.OpenAI` client with different `base_url` values. This is the key integration pattern in `02-worktrees/demo-marimo-app/app.py`:

```python
# All local backends use OpenAI SDK with custom base_url
llm_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")  # LM Studio
llm_client = OpenAI(base_url="http://localhost:8080/v1", api_key="sk-no-key-required")  # llama.cpp
llm_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # Ollama

# Cloud backends use their own constructors
llm_client = OpenAI(api_key=api_key)  # OpenAI
llm_client = AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version=api_version)  # Azure
```

**Structured Output Pattern:**
All LLM calls go through `parse_structured()` which uses `client.beta.chat.completions.parse()` with Pydantic `BaseModel` schemas as `response_format`. This returns typed, validated objects:

```python
parsed = client.beta.chat.completions.parse(
    model=model,
    response_format=schema,  # Pydantic BaseModel class
    messages=messages,
    temperature=temperature,
).choices[0].message.parsed

return schema.model_validate(parsed)
```

**Git Submodule:**
- `01-dev-onboarding` submodule points to `https://github.com/progressEdd/dev-onboarding.git` (master branch)
- Only exists on the `master`/`development` branches, not on experiment branches

**Git Template Remote:**
- `template` remote points to `git@github.com-primary:progressEdd/project-template.git`
- Used to pull template repo updates into the project via `git merge template/<branch>`

---

*Integration audit: 2026-02-13*
