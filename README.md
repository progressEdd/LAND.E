# AI Invasion — Story Writer Webapp

A purpose-built story writer with AI generation, inline provenance tracking, structured narrative analysis, and SQLite persistence. Replaces the original marimo notebook prototype.

## What It Does

- Write and edit stories in a rich text editor (Tiptap) with full formatting support
- Generate AI story continuations via WebSocket streaming — text appears token-by-token in the editor
- Track authorship with 4-color provenance marking: AI-generated (white), user-written (blue), user-edited (pink), initial prompt (cream)
- Accept or reject AI drafts — accepted text persists, rejected text is removed
- View structured narrative analysis after each generation (logline, cast, world rules, POV, timeline, active threads, continuity issues, and more)
- Export stories as markdown files
- Switch between multiple stories with full provenance restoration
- Supports 4 LLM backends: LM Studio, Ollama, OpenAI, llama.cpp

## Architecture

```
webapp-ui/
├── backend/           # FastAPI + SQLite
│   └── app/
│       ├── main.py          # Application entry point
│       ├── config.py        # Settings (DB path, CORS, default backend)
│       ├── models/          # Database (aiosqlite) + Pydantic schemas
│       ├── routers/         # REST (stories, llm) + WebSocket (ws)
│       ├── services/        # LLM client factory, story pipeline, export
│       └── db/migrations/   # SQLite schema (stories, nodes, provenance_spans)
├── frontend/          # SvelteKit SPA
│   └── src/
│       ├── routes/          # App shell + main page
│       └── lib/
│           ├── components/  # Editor, Toolbar, Sidebars, Settings, Analysis
│           ├── stores/      # Svelte 5 runes state (editor, story, generation, settings, theme)
│           ├── extensions/  # Tiptap custom provenance mark
│           ├── api/         # REST client + WebSocket client
│           └── types/       # TypeScript interfaces matching backend schemas
├── pyproject.toml     # uv workspace root
└── uv.lock
```

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+ and bun
- At least one LLM backend running (see [LLM Backends](#llm-backends))

## Getting Started

### 1. Install backend dependencies

```bash
cd 02-worktrees/webapp-ui
uv sync
```

This installs dependencies for the workspace root and the `backend/` member.

### 2. Install frontend dependencies

```bash
cd frontend
bun install
```

### 3. Start the backend

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. SQLite database is created automatically at `backend/data/stories.db` on first startup.

API docs: `http://localhost:8000/docs`

### 4. Start the frontend

In a separate terminal:

```bash
cd frontend
bun run dev
```

The app is available at `http://localhost:5173`. The Vite dev server proxies `/api` and `/ws` requests to the backend on port 8000.

## LLM Backends

The app supports 4 backends, all accessed through the OpenAI-compatible API pattern. Select your backend in the Settings panel (left sidebar).

| Backend | Default URL | Setup |
|---------|-------------|-------|
| **LM Studio** | `http://localhost:1234` | Install [LM Studio](https://lmstudio.ai/), load a model, start the server |
| **Ollama** | `http://localhost:11434` | Install [Ollama](https://ollama.com/), pull a model (`ollama pull <model>`) |
| **llama.cpp** | `http://localhost:8080` | Run [llama.cpp server](https://github.com/ggml-org/llama.cpp) with a GGUF model |
| **OpenAI** | OpenAI default | Set `OPENAI_API_KEY` environment variable or enter API key in Settings |

The default backend is LM Studio. You can change the backend, connection URL, and model from the Settings panel at any time.

## Tech Stack

**Backend:** FastAPI, SQLite (aiosqlite), Pydantic, OpenAI SDK, Ollama SDK, WebSockets

**Frontend:** SvelteKit 2, Svelte 5 (runes), Tailwind CSS 4, Tiptap 3 (ProseMirror), svelte-splitpanes
