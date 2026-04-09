# Technology Stack

**Analysis Date:** 2026-04-09

## Languages

**Primary:**
- Python 3.13 — All backend logic (FastAPI app, LLM services, story pipeline, database)
- TypeScript — Frontend application (SvelteKit components, stores, API clients)
- Svelte 5 — UI components using runes (`$state`, `$derived`, `$effect`)

**Secondary:**
- SQL — SQLite schema migrations and queries
- CSS — Custom properties for theming, Tailwind CSS 4 utility classes
- HTML — App shell (`app.html`)
- JSON — Configuration files, API payloads, lockfiles

## Runtime

**Backend:**
- Python 3.13 (pinned in `.python-version`)
- uv package manager with workspace support
- uvicorn with standard extras for auto-reload and WebSocket support

**Frontend:**
- Node.js 18+ (runtime for SvelteKit dev/build)
- bun as package manager
- Vite 7 dev server with proxy to backend

**Local LLM Runtime:**
- Ollama — Primary local model serving
- LM Studio — Alternative local backend (OpenAI-compatible at `http://localhost:1234/v1`)
- llama.cpp — Alternative local backend (OpenAI-compatible at `http://localhost:8080/v1`)
- OpenAI — Cloud backend option

## Frameworks

**Backend:**
- FastAPI 0.129+ — Async web framework with automatic OpenAPI docs
- Pydantic 2.11+ — Data validation, serialization, structured output schemas
- aiosqlite 0.22+ — Async SQLite driver
- uvicorn 0.40+ — ASGI server (with standard extras for hot reload)
- websockets 16+ — WebSocket protocol support

**Frontend:**
- SvelteKit 2 — Full-stack framework (using static adapter for SPA mode)
- Svelte 5 — UI framework with runes reactivity system
- Tailwind CSS 4 — Utility-first CSS framework
- Vite 7 — Build tool and dev server

**Rich Text Editor:**
- Tiptap 3 — ProseMirror-based rich text editor
  - `@tiptap/core` — Headless editor engine
  - `@tiptap/starter-kit` — Basic extensions (bold, italic, headings, etc.)
  - `@tiptap/extension-text-style` — Text styling support
  - `@tiptap/pm` — ProseMirror access

**Data Visualization:**
- d3-hierarchy 3 — Tree layout computation for node graph visualizer

**Layout:**
- svelte-splitpanes 8 — Resizable split pane layout

**Testing:**
- None. No test framework configured for backend or frontend.

## Key Dependencies

### Backend Python (backend/pyproject.toml)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.129.0 | Web framework, routing, middleware, WebSocket |
| `uvicorn[standard]` | >=0.40.0 | ASGI server with hot reload |
| `aiosqlite` | >=0.22.1 | Async SQLite driver |
| `pydantic` | >=2.11.7 | Data validation, structured output schemas |
| `openai` | >=2.21.0 | Universal LLM client for all backends |
| `ollama` | >=0.6.1 | Ollama model listing (native SDK) |
| `websockets` | >=16.0 | WebSocket protocol support |

### Frontend Node (frontend/package.json)

| Package | Version | Purpose |
|---------|---------|---------|
| `svelte` | ^5.49.2 | UI framework with runes |
| `@sveltejs/kit` | ^2.50.2 | Full-stack framework |
| `@sveltejs/adapter-static` | ^3.0.10 | Static SPA output |
| `@tiptap/core` | ^3.19.0 | Rich text editor engine |
| `@tiptap/starter-kit` | ^3.19.0 | Default editor extensions |
| `d3-hierarchy` | ^3.1.2 | Tree layout for graph visualizer |
| `svelte-splitpanes` | ^8.0.12 | Resizable pane layout |
| `tailwindcss` | ^4.1.18 | Utility CSS framework |
| `typescript` | ^5.9.3 | Type checking |

### Root Workspace (pyproject.toml)

Root `pyproject.toml` has minimal dependencies — just a uv workspace pointing to `backend/` as a member.

## Configuration

**Backend:**
- `backend/app/config.py` — Pydantic Settings with DATABASE_URL, CORS_ORIGINS, DEFAULT_BACKEND
- `backend/pyproject.toml` — Python project metadata and dependencies
- Database path: `sqlite:///./data/stories.db` (relative to backend/)

**Frontend:**
- `frontend/vite.config.ts` — Dev server proxy (`/api` → `localhost:8000`, `/ws` → WebSocket)
- `frontend/svelte.config.js` — Static adapter, prerender all
- `frontend/tsconfig.json` — TypeScript configuration
- `frontend/.npmrc` — npm configuration

**Environment Variables:**
- `OPENAI_API_KEY` — Optional, for OpenAI backend (can also be entered in UI)
- `OLLAMA_HOST` — Optional, overridden temporarily by backend for model listing
- No `.env` files committed or required

**Run Commands:**
```bash
# Backend
cd 02-worktrees/webapp-ui
uv sync
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd 02-worktrees/webapp-ui/frontend
bun install
bun run dev

# Legacy marimo app
cd 02-worktrees/demo-marimo-app
uv run marimo run app.py
```

## Database

**Engine:** SQLite with WAL mode and foreign keys enabled

**Tables:**
- `stories` — Top-level container (id, title, premise, active_path as JSON)
- `nodes` — Paragraph-level story tree nodes (parent_id adjacency list, is_draft flag)
- `provenance_spans` — Character-level source tracking (start_offset, end_offset, source)
- `character_mentions` — Character-to-node mapping (extracted from StoryAnalysis.cast)
- `node_analyses` — Persisted StoryAnalysis JSON per node

**Migrations:** Numbered SQL files in `backend/app/db/migrations/`, executed in order on startup.

## Platform Requirements

**Development:**
- Python 3.13+
- uv package manager
- Node.js 18+ and bun
- At least one LLM backend running (Ollama, LM Studio, llama.cpp, or OpenAI API key)
- Git 2.51+ (worktree support)

**Production:**
- Local-only application. No deployment target, no CI/CD.
- Backend: `uvicorn` serves FastAPI on localhost:8000
- Frontend: SvelteKit static build, served by Vite dev server (localhost:5173) or any static file server
- Database: SQLite file in `backend/data/`

---

*Stack analysis: 2026-04-09*
