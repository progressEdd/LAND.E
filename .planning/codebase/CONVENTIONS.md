# Coding Conventions

**Analysis Date:** 2026-04-09

## Overview

The project has two distinct codebases with different conventions: the **Python backend** (FastAPI) and the **TypeScript/Svelte frontend** (SvelteKit SPA). Both live in the `02-worktrees/webapp-ui/` worktree. The root repository follows its own organizational conventions for planning, dev logs, and supporting files.

## Backend Conventions (Python/FastAPI)

### Code Style

- **Formatting:** No linter or formatter configured (no ruff, black, or isort config)
- **Indentation:** 4-space indentation (PEP 8 standard)
- **String quotes:** Single quotes for short strings, double quotes for multi-line or strings containing apostrophes
- **Line length:** No enforced limit, but most lines stay under 120 characters
- **Type hints:** Used extensively — function signatures include parameter and return types

### Import Organization

1. Standard library first (`asyncio`, `json`, `os`, `time`, `uuid`, etc.)
2. Third-party packages second (`from fastapi import ...`, `from openai import OpenAI`, `from pydantic import ...`)
3. Local imports third (`from app.models.database import ...`, `from app.services.llm import ...`)

### Error Handling

- FastAPI `HTTPException` for REST endpoint errors with appropriate status codes (404, 400)
- WebSocket errors sent as JSON `{type: "error", message: "..."}` messages
- LLM client errors caught with broad `except Exception` and surfaced to user
- Database operations use async context managers (`async with get_db() as db:`)
- Try/except blocks in generation pipeline wrap OpenAI SDK calls

### Module Organization

```
app/
├── main.py          # App factory, middleware, lifespan
├── config.py        # Pydantic Settings singleton
├── models/          # Data layer
│   ├── database.py  # SQLite connection management
│   └── schemas.py   # All Pydantic models in one file
├── routers/         # API endpoints (one file per domain)
│   ├── stories.py   # Story + node CRUD
│   ├── llm.py       # LLM configuration
│   └── ws.py        # WebSocket generation
├── services/        # Business logic (separated from routers)
│   ├── llm.py       # LLM client factory + structured output
│   ├── story.py     # Generation pipeline
│   └── export.py    # Markdown export
└── db/migrations/   # Numbered SQL migration files
```

### Patterns

- **Router pattern:** Each router file defines an `APIRouter` with a prefix and tags
- **Service pattern:** Business logic in `services/`, routers delegate to services
- **Pydantic for everything:** Request bodies, response models, settings — all Pydantic
- **Module-level state:** LLM config stored as `_current_config = LLMBackendConfig()` (single-user app, no DB persistence needed)
- **Async everywhere:** All I/O operations are async (aiosqlite, asyncio.to_thread for OpenAI SDK)

### Docstrings

- Module-level docstrings describe the file's purpose
- Function docstrings use triple-quoted strings with brief descriptions
- Pydantic model docstrings serve as LLM system prompts (the `StoryStart`, `StoryContinue`, `StoryAnalysis` docstrings are injected into the structured output API calls)
- Porting notes reference source location: "Ported from app.py lines XXX-XXX"

## Frontend Conventions (TypeScript/Svelte)

### Code Style

- **Formatting:** No Prettier or ESLint configured
- **Indentation:** Tab-based indentation (Svelte default)
- **TypeScript:** Strict mode with explicit types for stores, API responses, and component props
- **Svelte 5 runes:** Uses `$state()`, `$derived()`, `$effect()` (no legacy `$:` syntax)

### Component Structure

```svelte
<script lang="ts">
  // Imports
  // Props
  // State ($state, $derived)
  // Lifecycle (onMount, onDestroy)
  // Functions
</script>

<!-- HTML template -->

<style>
  /* Scoped CSS with CSS custom properties */
</style>
```

### Store Pattern

Each store is a TypeScript class exported as a singleton:

```typescript
// stores/example.svelte.ts
class ExampleState {
  value = $state<string>('');
  derived = $derived(this.value.toUpperCase());

  method() { ... }
}

export const exampleState = new ExampleState();
```

Stores:
- `ThemeState` — Dark/light theme toggle, persists to localStorage
- `SettingsState` — LLM backend configuration
- `StoryState` — Story list, active story, CRUD operations, loaded stories cache
- `EditorState` — Tiptap editor instance, content management
- `GenerationState` — WebSocket connection, streaming state, accept/reject
- `GraphState` — Tree data for node graph visualizer

### Event Handling

- Svelte 5 event handler: `onclick={handler}` (not `on:click={handler}`)
- Stop propagation: `onclick={(e) => { e.stopPropagation(); ... }}` (not `|stopPropagation` modifier)
- $effect() for reactive side effects (initial data loading, state synchronization)

### CSS Conventions

- CSS custom properties for theming (defined in `app.css` `:root` and `[data-theme="light"]`)
- Scoped styles per component using `<style>` blocks
- Tailwind CSS 4 utility classes for layout
- Color variables: `--panel-bg`, `--text-primary`, `--text-secondary`, `--text-muted`, etc.
- Provenance colors defined as inline styles on Tiptap marks (survives copy/paste)

### File Naming

- Components: `PascalCase.svelte` (e.g., `Editor.svelte`, `NodeGraph.svelte`)
- Stores: `camelCase.svelte.ts` (e.g., `story.svelte.ts`, `generation.svelte.ts`)
- API clients: `camelCase.ts` (e.g., `rest.ts`, `ws.ts`)
- Extensions: `camelCase.ts` (e.g., `provenance.ts`)
- Types: `index.ts` (barrel file)

## Root Repository Conventions

### Directory Naming

- `XX-descriptive-name` numbered prefix for top-level directories
- Prefix `00-` for shared/template resources
- `02-worktrees/` for git worktree checkouts

### Branch Naming

- `00-experiments` for base environment
- Project branches: `kebab-case` (e.g., `webapp-ui`, `demo-marimo-app`)
- Template branches: `master`, `development`

### File Naming

- Planning docs: `UPPERCASE.md` (`PROJECT.md`, `ROADMAP.md`, `STATE.md`)
- Dev logs: `YYYY-MM-DD.md`
- Phase plans: `NN-NN-PLAN.md`
- Phase summaries: `NN-NN-SUMMARY.md`
- UAT files: `NN-UAT.md`
- Config files: lowercase (`config.json`, `pyproject.toml`)

### Markdown Style

- ATX-style headings (`#`, `##`, `###`)
- `- ` for unordered lists
- `1. ` for ordered lists
- Fenced code blocks with language identifiers
- Tables with `|` pipe syntax
- `---` separator before metadata footers

## Git Conventions

### Commit Messages

- Lowercase, imperative mood, no period at end
- Short and descriptive: `add README template with placeholder variables`
- Optional conventional commit prefixes: `docs:`, `test:`, `chore:`, `assets:`
- Plan references: `docs(02-16): graph polish — enlarged nodes, theme-aware seeds`
- Em dash for inline explanations: `mark all v1 phases complete — 10/10 requirements delivered`

### Branching

- All project branches fork from `00-experiments` (never from `master`)
- `git worktree add -b <name> 02-worktrees/<name> 00-experiments` for atomic creation
- Fetch before branching: `git fetch origin 00-experiments`

### Gitignore

- Comprehensive Python `.gitignore`
- `02-worktrees/*` gitignored except `README.md`
- `.env` files gitignored
- `__marimo__/`, `node_modules/`, `.svelte-kit/` gitignored
- `data/stories.db` gitignored (auto-created)

## Dependency Management

### Backend (Python/uv)

```bash
cd 02-worktrees/webapp-ui
uv sync                    # Install all workspace dependencies
cd backend
uv add <package>           # Add a dependency to backend
uv run uvicorn app.main:app --reload --port 8000  # Run
```

### Frontend (Node/bun)

```bash
cd 02-worktrees/webapp-ui/frontend
bun install                # Install dependencies
bun run dev                # Dev server
bun run build              # Production build
```

---

*Convention analysis: 2026-04-09*
