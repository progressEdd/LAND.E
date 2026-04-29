`# Architecture

**Analysis Date:** 2026-04-09

## Pattern Overview

**Overall:** Multi-branch template repository with git worktree-based parallel development. The primary application is a full-stack story writer webapp (FastAPI + SvelteKit SPA) that replaced an earlier marimo notebook prototype.

**Key Characteristics:**
- Two distinct branch families with completely different file trees: template branches (`master`, `development`) and project branches (forked from `00-experiments`)
- Git worktrees enable simultaneous work on multiple experiment/feature branches without checkout switching
- The `webapp-ui` worktree is the active application — a FastAPI backend with SvelteKit frontend SPA
- SQLite persistence with provenance tracking, WebSocket streaming, and interactive node graph visualizer
- Each project branch is self-contained and self-documenting after creation
- GSD AI orchestrator / pi serves as the automation layer — workflow is encoded in `.planning/` docs

## Branch Families

**Template Family (`master`, `development`):**
- Purpose: Repository scaffolding, dev logs, supporting files, worktree container, GSD planning
- Location: Root worktree at `.`
- Contains: Numbered directories (`00-dev-log/`, `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`), `.planning/`, `.foam/`, `LICENSE`, root `README.md`
- `master` is the current active branch on the root worktree
- `development` branch has the GSD planning work (ahead of master)

**Base Environment (`00-experiments`):**
- Purpose: Inheritable Python 3.13 + uv development environment that all new project branches start from
- Location: `02-worktrees/00-experiments/` (worktree)
- Contains: `pyproject.toml`, `uv.lock`, `.python-version`, `sandbox.ipynb`, `.gitignore`

**Primary Application (`webapp-ui`):**
- Purpose: Purpose-built AI story writer webapp replacing the original marimo notebook
- Location: `02-worktrees/webapp-ui/`
- Architecture: Monorepo with `backend/` (FastAPI) and `frontend/` (SvelteKit SPA)
- Database: SQLite with 5 tables (stories, nodes, provenance_spans, character_mentions, node_analyses)
- Key features: Tiptap rich text editor, 4-color provenance tracking, WebSocket AI streaming, interactive SVG node graph, markdown export

**Other Project Branches:**
- `demo-marimo-app` — Original marimo notebook prototype (reference/legacy)
- `experiments-with-models` — Jupyter notebooks for testing LLM models
- `source` — Exploration notebooks and model experiments
- `chinese-prompt` — Chinese language prompt experiments
- `presentation` — Presentation/outlining materials

## Layers

### Webapp Backend (FastAPI)

```
backend/
├── main.py                    # uvicorn entry point
├── pyproject.toml             # Python deps (fastapi, aiosqlite, openai, ollama, pydantic, uvicorn, websockets)
├── app/
│   ├── main.py                # FastAPI app, CORS, lifespan, router registration
│   ├── config.py              # Settings (DB path, CORS origins, default backend)
│   ├── models/
│   │   ├── database.py        # SQLite init, migrations, async connection manager
│   │   └── schemas.py         # Pydantic models (StoryStart, StoryContinue, StoryAnalysis, etc.)
│   ├── routers/
│   │   ├── stories.py         # REST: story/node CRUD, tree, active-path switching, export, random premise
│   │   ├── llm.py             # REST: LLM config get/set, model listing, warmup
│   │   └── ws.py              # WebSocket: AI generation streaming, accept/reject/cancel
│   ├── services/
│   │   ├── llm.py             # LLM client factory, structured output parsing, model discovery
│   │   ├── story.py           # Generation pipeline (analyze → continue → CycleResult)
│   │   └── export.py          # Markdown export from active path
│   └── db/
│       └── migrations/
│           ├── 001_initial.sql       # stories, nodes, provenance_spans tables
│           └── 002_graph_support.sql # character_mentions, node_analyses tables
└── data/
    └── stories.db              # SQLite database (auto-created on startup)
```

### Webapp Frontend (SvelteKit SPA)

```
frontend/
├── package.json                # Node deps (svelte, @tiptap/*, d3-hierarchy, svelte-splitpanes, tailwindcss)
├── svelte.config.js            # Static adapter, prerender all
├── vite.config.ts              # API/WS proxy to backend
├── src/
│   ├── app.html                # HTML shell
│   ├── app.css                 # Tailwind + CSS custom properties for theming
│   ├── app.d.ts                # TypeScript declarations
│   ├── routes/
│   │   ├── +layout.svelte      # App shell: splitpanes, sidebars, theme toggle
│   │   ├── +layout.ts          # Prerender config
│   │   └── +page.svelte        # Main page: editor or welcome state
│   └── lib/
│       ├── components/
│       │   ├── Editor.svelte           # Tiptap editor with provenance marks
│       │   ├── EditorToolbar.svelte    # Formatting toolbar (bold, italic, etc.)
│       │   ├── GenerationControls.svelte # Accept/reject/generate buttons
│       │   ├── NodeGraph.svelte        # Interactive SVG tree visualizer (d3-hierarchy)
│       │   ├── AnalysisPanel.svelte    # StoryAnalysis card display
│       │   ├── AnalysisCard.svelte     # Individual analysis field card
│       │   ├── SettingsPanel.svelte    # LLM config, story management
│       │   └── Sidebar.svelte          # Collapsible sidebar wrapper
│       ├── stores/
│       │   ├── editor.svelte.ts        # Editor state (Tiptap instance)
│       │   ├── generation.svelte.ts    # WebSocket connection, generation state
│       │   ├── graph.svelte.ts         # Graph tree data
│       │   ├── settings.svelte.ts      # LLM config state
│       │   ├── story.svelte.ts         # Story list, active story, CRUD
│       │   └── theme.svelte.ts         # Dark/light theme (CSS custom properties)
│       ├── api/
│       │   ├── rest.ts                 # Fetch wrapper for REST endpoints
│       │   └── ws.ts                   # WebSocket client for generation
│       ├── extensions/
│       │   └── provenance.ts           # Custom Tiptap mark (4-color provenance)
│       └── types/
│           └── index.ts                # TypeScript interfaces matching backend schemas
└── static/
```

### Planning & Documentation Layer

- Purpose: Project management, roadmapping, research, codebase analysis for AI orchestration
- Location: `.planning/`
- Contains: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `config.json`, `research/`, `phases/`, `codebase/`

### Dev Log Layer

- Purpose: Daily development notes, progress tracking
- Location: `00-dev-log/`
- Contains: Date-stamped markdown files (`YYYY-MM-DD.md`), a template (`00-template.md`)

## Data Flow

### AI Generation Cycle (primary flow)

```
User clicks "Generate"
    → Frontend sends WebSocket {type: "generate", story_id, model, seed?}
    → Backend loads story + active_path from SQLite
    → Backend builds story_text by concatenating nodes along active_path
    → Backend creates empty draft node in SQLite (is_draft=1)
    → Backend sends WebSocket {type: "draft_created", node_id}
    → Backend runs run_cycle():
        1. StoryAnalysis via parse_structured() → analysis (cast, threads, seeds, etc.)
        2. StoryContinue via parse_structured() → next_paragraph
    → Backend streams draft text char-by-char via WebSocket {type: "token", content}
    → Backend persists content, provenance span, analysis, character mentions to SQLite
    → Backend sends WebSocket {type: "complete", analysis}
    → Frontend renders text with provenance marks in Tiptap editor
    → User clicks "Accept" or "Reject"
    → Accept: marks is_draft=0, updates active_path, persists user edits
    → Reject: deletes draft node (cascading)
```

### Story Persistence & Restoration

```
Page load:
    → Frontend loads story list from GET /api/stories
    → Auto-selects last active story from localStorage
    → GET /api/stories/{id} returns full story with nodes, spans, mentions, analyses
    → EditorState restores content with provenance marks from spans

Story switching:
    → Frontend caches loaded stories in storyState.loadedStories map
    → setActiveStory(id) auto-loads from API if not cached
```

### Node Graph Rendering

```
GET /api/stories/{id}/tree
    → Returns recursive TreeNodeResponse with children, spans, mentions, analyses
    → Returns aggregated CharacterSummary list for supernode rendering
    → Frontend uses d3-hierarchy to compute SVG layout
    → Character supernodes rendered with initials badges
    → Clicking a node switches active path via PATCH /api/stories/{id}/active-path
    → Seed nodes are clickable for seed-guided generation
```

### New Story Creation (template workflow)

1. GSD reads `.planning/PROJECT.md`, `REQUIREMENTS.md`, and `ROADMAP.md` to understand the template system
2. Pre-flight: `git fetch origin 00-experiments` + `git worktree list --porcelain` to check for duplicates
3. Atomic branch+worktree: `git worktree add -b <name> 02-worktrees/<name> 00-experiments`
4. README population: `string.Template.safe_substitute()` replaces `$placeholder` variables
5. pyproject.toml update: `re.sub()` replaces `name` field with project name
6. Environment setup: `uv sync` creates `.venv` in the worktree
7. Commit on the new branch

## Key Abstractions

### Provenance Mark (Tiptap Custom Extension)

- Purpose: Track authorship at character-level within the rich text editor
- Implementation: Custom ProseMirror mark with inline `style` attribute (survives copy/paste)
- Sources: `ai_generated` (white), `user_written` (blue), `user_edited` (pink), `initial_prompt` (cream)
- Storage: `provenance_spans` table with `start_offset`, `end_offset`, `source` per node

### Story Tree Structure

- Purpose: Branching narrative where each node is a paragraph with multiple AI-drafted alternatives
- Implementation: `nodes` table with `parent_id` (adjacency list), `position` (sibling ordering), `is_draft` flag
- `active_path` on `stories` table stores the currently selected branch as a JSON array of node IDs
- Switching branches walks up the tree from target to root and updates `active_path`

### LLM Client Factory

- Purpose: Universal interface to 4 LLM backends via OpenAI-compatible API
- Implementation: `create_llm_client()` returns `openai.OpenAI` with different `base_url`/`api_key` per backend
- Backends: LM Studio, Ollama, OpenAI, llama.cpp
- Structured output: `client.beta.chat.completions.parse()` with Pydantic schemas

### Svelte 5 Runes State Management

- Purpose: Reactive state without external state management library
- Implementation: Class-based singletons using `$state` and `$derived` runes
- Stores: `ThemeState`, `SettingsState`, `StoryState`, `EditorState`, `GenerationState`, `GraphState`
- Pattern: `export const storyState = new StoryState()` — single instance per store

### CSS Custom Properties Theming

- Purpose: Runtime theme switching (dark/light) without Tailwind dark: prefix
- Implementation: `:root` and `[data-theme="light"]` CSS custom property overrides
- Variables: `--panel-bg`, `--text-primary`, `--text-secondary`, `--text-muted`, etc.

## Entry Points

**Webapp Backend:**
- `cd 02-worktrees/webapp-ui/backend && uv run uvicorn app.main:app --reload --port 8000`
- FastAPI auto-initializes SQLite DB on startup via lifespan context manager

**Webapp Frontend:**
- `cd 02-worktrees/webapp-ui/frontend && bun run dev`
- Vite dev server at `http://localhost:5173`, proxies `/api` and `/ws` to backend port 8000

**Legacy Marimo App:**
- `cd 02-worktrees/demo-marimo-app && uv run marimo run app.py`
- Original prototype, still functional

**Root Worktree (template/scaffolding):**
- Branch: `master` (currently checked out)
- Responsibilities: GSD planning, dev logs, supporting files, worktree management

## Error Handling

**Strategy:** Prevention via pre-flight checks + idempotency guards (template workflow), try/except with WebSocket error messages (webapp)

**Webapp patterns:**
- WebSocket errors sent as `{type: "error", message: "..."}` to frontend
- HTTP exceptions via FastAPI `HTTPException` with status codes (404, 400)
- LLM client errors caught in `run_cycle()` and surfaced to the user
- `aiosqlite` connections use context managers for automatic cleanup

**Template workflow patterns:**
- Duplicate branch/worktree detection via `git worktree list --porcelain`
- Sentinel-based idempotency for README population
- Atomic `git worktree add -b` — no partial state on failure

## Cross-Cutting Concerns

**Logging:** No structured logging. Errors displayed in UI (marimo callouts or WebSocket messages).

**Validation:** Pydantic schemas validate all API request/response bodies. SQLite CHECK constraints on provenance spans (start >= 0, end > start). Pre-flight checks before worktree creation.

**Authentication:** Not applicable — local single-user application. LLM API keys entered at runtime via UI or environment variables.

**Database:** SQLite with WAL mode, foreign keys enabled. Schema migrations via numbered SQL files (`001_initial.sql`, `002_graph_support.sql`). All database access through async `get_db()` context manager.

**Submodule Isolation:** `01-dev-onboarding` submodule exists on `master` only. `00-experiments` branch has no `.gitmodules`.

---

*Architecture analysis: 2026-04-09*
