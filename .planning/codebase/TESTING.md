# Testing Patterns

**Analysis Date:** 2026-04-09

## Test Framework

**Runner:**
- No test framework is installed or configured for either backend or frontend
- No `pytest`, `vitest`, `jest`, or any test runner
- No test configuration files exist (`pytest.ini`, `vitest.config.ts`, etc.)
- `.gitignore` includes `.pytest_cache/`, `.hypothesis/`, `htmlcov/`, `coverage.xml` — suggesting pytest is intended for future use

**Assertion Library:**
- None configured
- Python one-liner validation uses bare `assert` statements

**Run Commands:**
```bash
# No test commands currently available

# When pytest is added for backend:
cd 02-worktrees/webapp-ui/backend
uv add --dev pytest pytest-asyncio pytest-cov
uv run pytest

# When vitest is added for frontend:
cd 02-worktrees/webapp-ui/frontend
bun add -d vitest @testing-library/svelte
bun run test
```

## Current Testing Approach

This project uses **manual verification and UAT (User Acceptance Testing)** instead of automated tests.

### UAT Pattern

**Location:** `.planning/phases/{phase-name}/{phase}-UAT.md`

**Structure:**
- Each test has a numbered heading, `expected:` description, and `result:` field
- Summary tracks totals (passed, failed, issues, pending, skipped)
- Gaps section documents missing coverage
- YAML frontmatter tracks status, phase, source summary, timestamps

### Plan-Level Verification

**Location:** Within plan files (`NN-NN-PLAN.md`)

**Structure:**
- `<verify>` blocks contain shell one-liners for post-execution validation
- Shell commands: `test -s`, `grep -c`, `git status --porcelain`
- Python one-liners: `python3 -c "..."` with `assert` statements
- Each step checks one specific condition with clear pass/fail outcome

### Manual Webapp Testing

The webapp (webapp-ui) was tested manually during development:
- Backend API verified via Swagger UI (`http://localhost:8000/docs`)
- Frontend verified by visual inspection in browser
- LLM generation tested with each backend (Ollama, LM Studio, OpenAI, llama.cpp)
- Graph visualizer verified with screenshots in plan summaries

## Test File Organization

**Current state:**
- No test directory exists
- No `test_*.py`, `*.test.ts`, `*.spec.ts` files
- UAT documents in `.planning/phases/`
- Verification logic embedded in plan files

## What Needs Testing

### Backend (Priority Areas)

**LLM Service (high priority):**
- `create_llm_client()` — Verify correct client config for each backend
- `parse_structured()` — Verify structured output parsing with mock responses
- `list_models()` — Verify model listing for each backend
- `_normalize_base_url()` — URL normalization edge cases

**Story Service (high priority):**
- `run_cycle()` — Verify generation pipeline with mocked LLM client
- `extract_characters()` — Verify character name/role extraction from cast strings

**Story Router (medium priority):**
- CRUD operations (create, read, update, delete stories and nodes)
- Active path management (switch branches, path reconstruction)
- Tree endpoint (recursive tree building)
- Export endpoint (markdown generation)
- Edge cases: empty active_path, missing nodes, circular references

**WebSocket Handler (medium priority):**
- Generation flow (draft creation → streaming → completion)
- Cancel flow
- Accept/reject flow
- Error handling (missing story, no backend configured)

**Database (low priority):**
- Migration execution (idempotency)
- Cascade deletes (deleting story removes nodes + spans)
- Connection management (cleanup on error)

### Frontend (Priority Areas)

**Stores (medium priority):**
- `storyState` — CRUD operations, caching, active story management
- `generationState` — WebSocket connection lifecycle, state transitions
- `themeState` — Theme persistence and switching

**API Clients (medium priority):**
- REST client — Error handling, response parsing
- WebSocket client — Connection, reconnection, message parsing

**Components (low priority):**
- `NodeGraph` — Tree rendering, node interaction, path switching
- `Editor` — Tiptap initialization, provenance mark rendering
- `SettingsPanel` — Config form submission

## Recommended Testing Setup

### Backend (pytest)

```bash
cd 02-worktrees/webapp-ui/backend
uv add --dev pytest pytest-asyncio pytest-cov httpx
```

**Directory structure:**
```
backend/
├── tests/
│   ├── conftest.py           # Shared fixtures (test DB, mock clients)
│   ├── test_schemas.py       # Pydantic model validation
│   ├── test_services/
│   │   ├── test_llm.py       # LLM client factory, structured output
│   │   ├── test_story.py     # Generation pipeline, character extraction
│   │   └── test_export.py    # Markdown export
│   ├── test_routers/
│   │   ├── test_stories.py   # Story/node CRUD endpoints
│   │   ├── test_llm.py       # LLM config endpoints
│   │   └── test_ws.py        # WebSocket handler
│   └── test_database.py      # Migration, connection management
├── pyproject.toml            # [tool.pytest.ini_options] config
└── app/
```

**Key fixtures needed:**
- In-memory SQLite database (`aiosqlite.connect(":memory:")`)
- Mock OpenAI client (returns canned structured responses)
- Test client for FastAPI (`httpx.AsyncClient` with ASGI transport)

### Frontend (vitest)

```bash
cd 02-worktrees/webapp-ui/frontend
bun add -d vitest @testing-library/svelte jsdom
```

**Directory structure:**
```
frontend/
├── tests/
│   ├── stores/
│   │   ├── story.test.ts
│   │   ├── generation.test.ts
│   │   └── theme.test.ts
│   ├── api/
│   │   ├── rest.test.ts
│   │   └── ws.test.ts
│   └── components/
│       ├── Editor.test.ts
│       └── NodeGraph.test.ts
├── vitest.config.ts
└── src/
```

## Coverage

**Current:** 0% — No automated tests exist.

**Recommended minimum coverage when tests are added:**
- Backend services: 80%+ (LLM, story, export)
- Backend routers: 70%+ (API endpoint behavior)
- Frontend stores: 80%+ (state management)
- Frontend components: 50%+ (key interactions)

---

*Testing analysis: 2026-04-09*
