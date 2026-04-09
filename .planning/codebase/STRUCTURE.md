# Codebase Structure

**Analysis Date:** 2026-04-09

## Directory Layout

```
LAND.E/                          # Root worktree (master branch)
├── .foam/                            # VS Code Foam extension templates
│   └── templates/                    # Note templates for daily logs
│       ├── daily-note.md             # Date-stamped daily note template
│       └── new-template.md           # Generic Foam template
├── .planning/                        # AI orchestrator planning system
│   ├── codebase/                     # Codebase analysis documents
│   │   ├── ARCHITECTURE.md           # Architecture patterns and data flows
│   │   ├── CONCERNS.md               # Tech debt, bugs, risks
│   │   ├── CONVENTIONS.md            # Coding and naming conventions
│   │   ├── INTEGRATIONS.md           # External service integrations
│   │   ├── STACK.md                  # Technology stack details
│   │   ├── STRUCTURE.md              # This file — directory layout
│   │   └── TESTING.md                # Testing patterns
│   ├── phases/                       # Execution phase plans and summaries
│   │   ├── 01-template-preparation/  # Phase 1 artifacts
│   │   └── 02-webapp-ui/            # Phase 4 artifacts (16 plans)
│   ├── research/                     # Domain research documents
│   ├── config.json                   # GSD configuration
│   ├── PROJECT.md                    # Project definition
│   ├── REQUIREMENTS.md               # Formal requirements
│   ├── ROADMAP.md                    # Phase definitions and progress
│   └── STATE.md                      # Current execution state
├── 00-dev-log/                       # Development journal entries
│   ├── 00-template.md
│   ├── 2025-12-28.md
│   ├── 2025-12-29.md
│   └── 2025-12-30.md
├── 00-supporting-files/              # Shared data and media assets
│   ├── data/
│   │   └── sample.env.file           # Environment variable template
│   └── images/                       # Screenshots organized by date/purpose
├── 01-dev-onboarding/                # Git submodule (empty on worktree branches)
├── 02-worktrees/                     # Git worktree container (contents gitignored)
│   ├── README.md
│   ├── 00-experiments/               # Base Python environment branch
│   ├── webapp-ui/                    # PRIMARY APPLICATION — FastAPI + SvelteKit
│   ├── demo-marimo-app/              # Legacy marimo notebook prototype
│   ├── experiments-with-models/      # LLM model testing notebooks
│   ├── source/                       # Exploration notebooks
│   ├── chinese-prompt/               # Chinese language prompt experiments
│   └── presentation/                 # Presentation/outlining materials
├── .bg-shell/                        # Background shell config
├── .pi/                              # pi coding agent config
├── .gitignore                        # Python-focused gitignore + worktree exclusions
├── .gitmodules                       # Submodule config
├── LICENSE                           # Project license
├── README.md                         # Root repo README with demos and screenshots
└── .venv/                            # Python virtual environment (root)
```

## Primary Application Structure (webapp-ui)

```
02-worktrees/webapp-ui/               # Main application worktree
├── pyproject.toml                    # uv workspace root config
├── uv.lock                          # Locked Python dependencies
├── sandbox.ipynb                    # Scratch notebook
├── README.md                        # App-specific documentation
├── .gitignore
├── .python-version                  # Python 3.13
├── backend/                         # FastAPI application
│   ├── main.py                      # uvicorn entry point (imports app.main)
│   ├── pyproject.toml               # Backend-specific deps
│   ├── README.md
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, CORS, lifespan
│   │   ├── config.py                # Settings (DB, CORS, default backend)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py          # SQLite init, migrations, async connection
│   │   │   └── schemas.py           # Pydantic models (209 lines)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── stories.py           # Story/node CRUD, tree, export (739 lines)
│   │   │   ├── llm.py               # LLM config, models, warmup (54 lines)
│   │   │   └── ws.py                # WebSocket generation streaming (307 lines)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm.py               # LLM client factory, structured output (214 lines)
│   │   │   ├── story.py             # Generation pipeline, character extraction (110 lines)
│   │   │   └── export.py            # Markdown export (85 lines)
│   │   └── db/
│   │       └── migrations/
│   │           ├── 001_initial.sql         # stories, nodes, provenance_spans
│   │           └── 002_graph_support.sql   # character_mentions, node_analyses
│   ├── data/
│   │   └── stories.db               # SQLite database (auto-created)
│   └── .venv/                       # Backend Python venv
└── frontend/                        # SvelteKit SPA
    ├── package.json                 # Node dependencies
    ├── package-lock.json            # Locked Node deps
    ├── bun.lock                     # Bun lockfile
    ├── svelte.config.js             # Static adapter config
    ├── vite.config.ts               # Dev server + API proxy
    ├── tsconfig.json                # TypeScript config
    ├── .npmrc
    ├── .gitignore
    ├── README.md
    ├── node_modules/
    ├── .svelte-kit/
    ├── static/                      # Static assets
    └── src/
        ├── app.html                 # HTML shell
        ├── app.css                  # Tailwind + CSS custom properties (theming)
        ├── app.d.ts                 # TypeScript declarations
        ├── routes/
        │   ├── +layout.svelte       # App shell: splitpanes, sidebars (193 lines)
        │   ├── +layout.ts           # Prerender config
        │   └── +page.svelte         # Main page: editor or welcome (105 lines)
        └── lib/
            ├── index.ts
            ├── components/
            │   ├── Editor.svelte            # Tiptap editor + provenance (358 lines)
            │   ├── EditorToolbar.svelte     # Formatting toolbar (227 lines)
            │   ├── GenerationControls.svelte # Accept/reject/generate (246 lines)
            │   ├── NodeGraph.svelte        # SVG tree visualizer (824 lines)
            │   ├── AnalysisPanel.svelte     # Story analysis cards (193 lines)
            │   ├── AnalysisCard.svelte      # Single analysis field (97 lines)
            │   ├── SettingsPanel.svelte     # LLM config, story mgmt (518 lines)
            │   └── Sidebar.svelte           # Collapsible sidebar (108 lines)
            ├── stores/
            │   ├── editor.svelte.ts         # Editor state (55 lines)
            │   ├── generation.svelte.ts     # WebSocket + generation state (134 lines)
            │   ├── graph.svelte.ts          # Graph tree data (44 lines)
            │   ├── settings.svelte.ts       # LLM config (14 lines)
            │   ├── story.svelte.ts          # Story CRUD (128 lines)
            │   └── theme.svelte.ts          # Dark/light theme (16 lines)
            ├── api/
            │   ├── rest.ts                  # REST API client (150 lines)
            │   └── ws.ts                    # WebSocket client (123 lines)
            ├── extensions/
            │   └── provenance.ts            # Tiptap provenance mark (39 lines)
            └── types/
                └── index.ts                 # TypeScript interfaces (98 lines)
```

## Codebase Size

| Area | Files | Lines |
|------|-------|-------|
| Backend Python | 13 source files | ~1,822 lines |
| Frontend TypeScript/Svelte | 21 source files | ~3,672 lines |
| Database migrations | 2 SQL files | ~65 lines |
| Planning documents | 50+ markdown files | ~5,000+ lines |
| **Total application code** | **~36 files** | **~5,500 lines** |

## Key File Locations

**Entry Points:**
- `02-worktrees/webapp-ui/backend/main.py` → `uv run uvicorn app.main:app --reload --port 8000`
- `02-worktrees/webapp-ui/frontend/src/routes/+page.svelte` → `bun run dev`
- `02-worktrees/demo-marimo-app/app.py` → `uv run marimo run app.py` (legacy)
- Root `README.md` → Project overview with demos

**Configuration:**
- `02-worktrees/webapp-ui/backend/app/config.py` → Backend settings (DB path, CORS, default LLM)
- `02-worktrees/webapp-ui/frontend/vite.config.ts` → API proxy to localhost:8000
- `02-worktrees/webapp-ui/frontend/svelte.config.js` → Static adapter, prerender
- `02-worktrees/webapp-ui/pyproject.toml` → uv workspace root
- `02-worktrees/webapp-ui/backend/pyproject.toml` → Backend Python deps
- `02-worktrees/webapp-ui/frontend/package.json` → Frontend Node deps
- `.planning/config.json` → GSD/pi configuration

**Database:**
- `02-worktrees/webapp-ui/backend/app/db/migrations/001_initial.sql` → Core schema (stories, nodes, provenance_spans)
- `02-worktrees/webapp-ui/backend/app/db/migrations/002_graph_support.sql` → Graph tables (character_mentions, node_analyses)
- `02-worktrees/webapp-ui/backend/data/stories.db` → SQLite database (auto-created)

**Core Backend Logic:**
- `backend/app/services/llm.py` → LLM client factory + structured output parsing
- `backend/app/services/story.py` → Generation pipeline (analyze → continue)
- `backend/app/routers/ws.py` → WebSocket generation streaming
- `backend/app/routers/stories.py` → Full CRUD REST API
- `backend/app/models/schemas.py` → All Pydantic models

**Core Frontend Logic:**
- `frontend/src/lib/components/NodeGraph.svelte` → SVG tree visualizer (largest component)
- `frontend/src/lib/components/Editor.svelte` → Tiptap editor with provenance marks
- `frontend/src/lib/components/SettingsPanel.svelte` → LLM config + story management
- `frontend/src/lib/stores/generation.svelte.ts` → WebSocket state machine
- `frontend/src/lib/stores/story.svelte.ts` → Story CRUD with caching
- `frontend/src/routes/+layout.svelte` → App shell layout

## Where to Add New Code

**New Backend Endpoint:**
- Router: `backend/app/routers/` (add to existing or create new router)
- Schema: `backend/app/models/schemas.py` (Pydantic models)
- Service: `backend/app/services/` (business logic)
- Migration: `backend/app/db/migrations/NNN_name.sql` (schema changes)

**New Frontend Component:**
- Component: `frontend/src/lib/components/NewComponent.svelte`
- Store: `frontend/src/lib/store/new-store.svelte.ts` (if stateful)
- Types: `frontend/src/lib/types/index.ts` (TypeScript interfaces)

**New Experiment/Feature Project:**
- Create via: `git worktree add -b <name> 02-worktrees/<name> 00-experiments`
- Primary code: `02-worktrees/<name>/`

**New Dev Log Entry:**
- Location: `00-dev-log/YYYY-MM-DD.md`
- Screenshots: `00-supporting-files/images/YYYY-MM-DD/`

## Naming Conventions

**Files:**
- Markdown docs: `UPPERCASE.md` for GSD system docs
- Dev logs: `YYYY-MM-DD.md`
- Phase plans: `NN-NN-PLAN.md`
- Python: `snake_case.py`
- TypeScript/Svelte: `PascalCase.svelte` for components, `camelCase.ts` for utilities
- Database migrations: `NNN_descriptive_name.sql`

**Directories:**
- Root directories: `NN-descriptive-name` numbered prefix
- Backend: `app/` with `models/`, `routers/`, `services/`, `db/`
- Frontend: `src/lib/` with `components/`, `stores/`, `api/`, `extensions/`, `types/`
- Phase dirs: `NN-phase-name/`

**Branches:**
- `00-experiments`: Base environment
- Project branches: `kebab-case` (e.g., `webapp-ui`, `demo-marimo-app`)
- Template branches: `master`, `development`

## Special Directories

**`02-worktrees/webapp-ui/`:**
- Purpose: Primary application worktree
- Generated: Partially (node_modules, .venv, data/stories.db auto-created)
- Committed: Source code yes; runtime artifacts no
- Backend: Python/FastAPI with SQLite
- Frontend: SvelteKit SPA with Tiptap editor

**`02-worktrees/demo-marimo-app/`:**
- Purpose: Legacy marimo notebook prototype (reference implementation)
- Still functional but superseded by `webapp-ui`

**`02-worktrees/`:**
- Purpose: Container for all git worktree checkouts
- Contents: Gitignored except `README.md`

**`.planning/`:**
- Purpose: AI orchestrator working directory
- Committed: Yes — essential for context continuity

**`.venv/`:**
- Purpose: Python virtual environment (one per worktree)
- Committed: No — gitignored

## Branch-Specific File Trees

**`master` branch (root worktree):**
```
.bg-shell/, .foam/, .pi/, .planning/, 00-dev-log/, 00-supporting-files/,
01-dev-onboarding/, 02-worktrees/,
.gitignore, .gitmodules, LICENSE, README.md
```

**`00-experiments` branch (base for all projects):**
```
.gitignore, .python-version, pyproject.toml, sandbox.ipynb,
uv.lock, README.md (template with $placeholders)
```

**`webapp-ui` branch (primary application):**
```
backend/ (FastAPI app), frontend/ (SvelteKit SPA),
pyproject.toml, uv.lock, sandbox.ipynb, README.md
```

**`demo-marimo-app` branch (legacy):**
```
app.py, custom.css, head.html, layouts/, pyproject.toml, README.md
```

---

*Structure analysis: 2026-04-09*
