---
phase: 02-webapp-ui
plan: 01
subsystem: api
tags: [fastapi, sqlite, aiosqlite, pydantic, openai, ollama, llm, structured-output]

# Dependency graph
requires:
  - phase: none
    provides: marimo app source code as reference (02-worktrees/demo-marimo-app/app.py)
provides:
  - FastAPI application entry point with CORS and health endpoint
  - SQLite database with stories, nodes, provenance_spans tables (adjacency list tree model)
  - LLM client factory supporting 4 backends (lmstudio, ollama, openai, llamacpp)
  - Async parse_structured() for Pydantic schema-based LLM output
  - Async run_cycle() story generation pipeline (analysis → continuation)
  - Pydantic schemas: StoryStart, StoryContinue, StoryAnalysis, LLMBackendConfig
affects: [02-02, 02-03, 02-04, 02-05, 02-06]

# Tech tracking
tech-stack:
  added: [fastapi, uvicorn, aiosqlite, openai, ollama, pydantic, websockets]
  patterns: [lifespan-based startup, async context manager for DB, threadpool for sync SDK calls]

key-files:
  created:
    - 02-worktrees/webapp-ui/backend/app/main.py
    - 02-worktrees/webapp-ui/backend/app/config.py
    - 02-worktrees/webapp-ui/backend/app/models/database.py
    - 02-worktrees/webapp-ui/backend/app/models/schemas.py
    - 02-worktrees/webapp-ui/backend/app/services/llm.py
    - 02-worktrees/webapp-ui/backend/app/services/story.py
    - 02-worktrees/webapp-ui/backend/app/db/migrations/001_initial.sql
    - 02-worktrees/webapp-ui/backend/pyproject.toml
  modified:
    - 02-worktrees/webapp-ui/pyproject.toml
    - 02-worktrees/webapp-ui/uv.lock

key-decisions:
  - "Used FastAPI lifespan context manager instead of deprecated on_event('startup')"
  - "Preserved schema docstrings exactly from marimo app — they serve as LLM system prompts"
  - "Used asyncio.to_thread() to wrap synchronous OpenAI SDK calls for async FastAPI"

patterns-established:
  - "Lifespan pattern: database initialization via async context manager on app startup"
  - "LLM client factory pattern: single create_llm_client() function returns OpenAI client for any backend"
  - "Structured output pattern: parse_structured() wraps OpenAI beta API with Pydantic schema validation"

# Metrics
duration: 3min
completed: 2026-02-14
---

# Phase 02 Plan 01: Backend Scaffold Summary

**FastAPI backend with SQLite adjacency-list story tree, 4-backend LLM client factory, and async story generation pipeline ported from marimo app**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-14T03:36:21Z
- **Completed:** 2026-02-14T03:39:56Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments
- FastAPI server with CORS middleware, health endpoint, and SQLite auto-initialization on startup
- SQLite database schema with stories, nodes, provenance_spans tables supporting tree-based branching (adjacency list with sibling ordering and character-level provenance)
- LLM service layer ported from marimo app: client factory for 4 backends, async structured output parsing, model listing, model warmup
- Story generation pipeline: async run_cycle() that analyzes story context then generates next paragraph

## Task Commits

Each task was committed atomically:

1. **Task 1: Initialize backend project and create database schema** - `ff3e93b` (feat)
2. **Task 2: Port LLM service and story generation pipeline** - `c1f0513` (feat)

## Files Created/Modified
- `backend/pyproject.toml` - Python project config with FastAPI and LLM dependencies
- `backend/app/main.py` - FastAPI application entry point with CORS and health endpoint
- `backend/app/config.py` - Settings class (DB URL, CORS origins, default backend)
- `backend/app/models/database.py` - aiosqlite connection management with WAL mode and migration runner
- `backend/app/models/schemas.py` - Pydantic schemas (StoryStart, StoryContinue, StoryAnalysis, LLMBackendConfig, API models)
- `backend/app/services/llm.py` - LLM client factory, parse_structured(), model listing, warmup
- `backend/app/services/story.py` - run_cycle() generation pipeline with CycleResult dataclass
- `backend/app/db/migrations/001_initial.sql` - SQLite schema with 3 tables, 3 indexes, and constraints

## Decisions Made
- Used FastAPI lifespan context manager (not deprecated `on_event`) for database initialization
- Preserved schema docstrings exactly as-is from marimo app — they are the LLM system prompts
- Used `asyncio.to_thread()` to wrap synchronous OpenAI SDK calls for async compatibility
- Backend directory initialized as a uv workspace member of the parent worktree

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Backend scaffold complete, ready for 02-02-PLAN.md (Frontend scaffold: SvelteKit SPA)
- All service layer functions ready for API endpoints (02-04-PLAN.md)
- Database schema ready for story CRUD operations

## Self-Check: PASSED

- All 9 key files verified on disk
- Both task commits found in git history (ff3e93b, c1f0513)

---
*Phase: 02-webapp-ui*
*Completed: 2026-02-14*
