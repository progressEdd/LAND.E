# Technology Stack

**Analysis Date:** 2026-02-13

## Languages

**Primary:**
- Python 3.13 - All application logic, notebooks, and the marimo app (`02-worktrees/demo-marimo-app/app.py`, `02-worktrees/experiments-with-models/*.ipynb`)

**Secondary:**
- CSS - Custom marimo styling overrides (`02-worktrees/demo-marimo-app/custom.css`)
- HTML/JavaScript - Screenshot toggle utility (`02-worktrees/demo-marimo-app/head.html`)
- JSON - Marimo layout files (`02-worktrees/demo-marimo-app/layouts/app.grid.json`), marimo session state (`02-worktrees/demo-marimo-app/__marimo__/`)

## Runtime

**Environment:**
- Python 3.13.0 (pinned in `.python-version`, declared in `pyproject.toml` as `requires-python = ">=3.13"`)
- Runs locally on macOS (darwin platform)

**Package Manager:**
- uv 0.9.18
- Lockfile: `uv.lock` — present and committed on all branches

**Local LLM Runtime:**
- Ollama 0.13.4 — required for local model serving (primary LLM backend)
- LM Studio — supported as alternative local backend (OpenAI-compatible API at `http://localhost:1234/v1`)
- llama.cpp — supported as alternative local backend (OpenAI-compatible API at `http://localhost:8080/v1`)

## Frameworks

**Core:**
- marimo >=0.18.4 - Reactive notebook framework used as both the application UI and development environment. The main app is a marimo script, not a traditional web app.
- pydantic (transitive via openai) - Data validation and structured output schemas (`StoryStart`, `StoryContinue`, `StoryAnalysis` in `02-worktrees/demo-marimo-app/app.py`)

**Testing:**
- None detected. No test framework, no test files, no test configuration.

**Build/Dev:**
- uv 0.9.18 - Dependency management, virtual environment creation, and script running
- ipykernel >=6.30.1 - Jupyter kernel support for `.ipynb` notebooks on the `experiments-with-models` branch
- Foam (VS Code extension) - Note-taking templates in `.foam/templates/`

## Key Dependencies

**Critical (declared in `pyproject.toml`):**
- `marimo>=0.18.4` - The entire UI/app framework. The app runs via `uv run marimo run <app>.py`
- `ollama>=0.5.3` - Python SDK for Ollama local model server. Used for model listing (`ollama.list()`) and direct chat (`ollama.chat()`)
- `openai>=1.101.0` - OpenAI Python SDK. Used as the universal LLM client for all backends (OpenAI, Azure, LM Studio, llama.cpp, and Ollama via OpenAI-compatible API). Provides `client.beta.chat.completions.parse()` for structured outputs.
- `ipykernel>=6.30.1` - Jupyter kernel for running `.ipynb` notebooks interactively

**Transitive (via openai/pydantic):**
- `pydantic` - Used directly for `BaseModel` schemas and `Field` definitions in `02-worktrees/demo-marimo-app/app.py`
- `httpx` - HTTP transport for the OpenAI SDK (transitive)
- `anyio` - Async I/O used by OpenAI SDK (transitive)

**Infrastructure:**
- `git` 2.51.2 - Version control, worktree management, branch-per-project workflow

## Configuration

**Environment:**
- No `.env` files present anywhere in the repository
- `sample.env.file` exists at `00-supporting-files/data/sample.env.file` (reference only, blocked from reading)
- API keys are entered at runtime through the marimo UI forms (OpenAI API key, Azure endpoint/key), not stored in files
- Ollama host URL configured via UI radio buttons, defaults to `http://localhost:11434`
- LM Studio URL defaults to `http://localhost:1234/v1`
- llama.cpp URL defaults to `http://localhost:8080/v1`

**Build:**
- `pyproject.toml` - Project metadata, Python version, and dependencies (identical across all branches)
- `.python-version` - Pins Python 3.13 for uv/pyenv
- `uv.lock` - Locked dependency resolution, committed to git

**Run Commands:**
```bash
# Run the marimo app (primary)
uv run marimo run 02-worktrees/demo-marimo-app/app.py

# Run marimo in edit mode (development)
uv run marimo edit 02-worktrees/demo-marimo-app/app.py

# Sync dependencies in a worktree
uv sync  # from within a worktree directory

# Run Jupyter notebooks (experiments branch)
uv run jupyter notebook  # from within 02-worktrees/experiments-with-models/
```

## Platform Requirements

**Development:**
- macOS (primary development platform, darwin)
- Python 3.13+ (pinned via `.python-version`)
- uv package manager (0.9.18+)
- Ollama installed locally (or LM Studio / llama.cpp as alternatives)
- At least one local LLM model downloaded (e.g., `gemma3:12b-it-q8_0`, `qwen3:30b-a3b-instruct-2507-q4_K_M`)
- Git 2.51+ (worktree support required)

**Production:**
- Local-only application. No deployment target, no CI/CD, no hosting.
- Runs entirely on the developer's machine via `uv run marimo run`

## Repository Structure (Multi-Branch)

**Branch architecture:**
- `development` - Current main branch (root worktree). Contains template structure, planning docs, dev logs.
- `master` - Original branch. Template repo structure.
- `00-experiments` - Base Python environment. All project branches fork from here.
- `demo-marimo-app` - The main application (marimo-based story writer)
- `experiments-with-models` - Jupyter notebooks for testing different LLM models
- `marimo-tests` - Marimo sandbox experiments

**Git remotes:**
- `origin` → `git@github.com-primary:progressEdd/LAND.E.git`
- `template` → `git@github.com-primary:progressEdd/project-template.git` (upstream template repo)

---

*Stack analysis: 2026-02-13*
