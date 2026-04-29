# LAND.E — Local AI Novel Drafting Environment

## What This Is

A local-first AI story writing application that lets you generate, edit, and track narratives using local LLMs. Features a purpose-built webapp (FastAPI + SvelteKit SPA) with a Tiptap rich text editor, 4-color provenance tracking, WebSocket AI streaming, an interactive node graph visualizer, and SQLite persistence. Built on a git worktree-based project template that supports parallel experiment development.

**Inspired by** [NovelAI](https://novelai.net), based on the idea from the [original AI Invasion thread](https://forum.level1techs.com/t/bedhedds-ai-invasion/235812) and [DougDoug's AI Invasion series](https://youtube.com/playlist?list=PLzY2D6XUB8KfzQbQBRV2KVxrRJ3kO1Bwo&si=uh6k-siNpcEZMxbi).

## Core Value

Write stories with AI assistance while maintaining full control over provenance — every piece of text is color-coded by source (AI-generated, user-written, user-edited, initial prompt). Branch your narrative, explore alternatives with the interactive node graph, and steer generation with seed-guided prompts. All running locally with your choice of LLM backend.

## Current Milestone: v1.1 UI Fixes & Story Management

**Goal:** Fix the broken connection indicator and add story deletion capability

**Target features:**
- Delete story button with cascade cleanup and confirmation dialog
- Fix premise generation ("I'm Feeling Lucky") breaking WebSocket connection status

## Requirements

### Delivered (v1 — Template + Workflow)

- [x] Numbered directory convention for organization
- [x] Git worktree support via `02-worktrees/`
- [x] Dev log templates via `00-dev-log/` and Foam
- [x] Python 3.13 base environment on `00-experiments` branch
- [x] uv dependency management on `00-experiments` branch
- [x] Template README on `00-experiments` branch with placeholder sections
- [x] Workflow branches from `00-experiments` and creates worktree in `02-worktrees/`
- [x] Branch README populated with project context on new project init
- [x] `pyproject.toml` project name updated to match the experiment/feature
- [x] Root repo README updated to reference active branches/experiments

### Delivered (v2 — Webapp UI)

- [x] FastAPI backend with SQLite persistence (stories, nodes, provenance_spans, character_mentions, node_analyses)
- [x] SvelteKit SPA frontend with collapsible sidebars, split pane layout, dark/light theme
- [x] Tiptap rich text editor with custom provenance mark extension (4-color source tracking)
- [x] REST API for stories CRUD, nodes CRUD, LLM config, model listing, warmup
- [x] WebSocket streaming — AI-generated text appears token-by-token in the editor
- [x] Accept/reject AI drafts — accepted text persists, rejected drafts are removed
- [x] Analysis panel with structured StoryAnalysis cards (logline, cast, timeline, threads, etc.)
- [x] Stories persist in SQLite and restore with provenance on page refresh
- [x] Markdown export produces a downloadable .md file of the active story path
- [x] Interactive SVG node graph with d3-hierarchy (character supernodes, branch switching, seed-guided generation)
- [x] 4 LLM backends supported: LM Studio, Ollama, OpenAI, llama.cpp

### Active (v1.1)

- [ ] **DELE-01**: User can delete a story from the dashboard via a trash icon button with confirmation dialog
- [ ] **DELE-02**: Deleting a story cascades to remove all related records (nodes, provenance_spans, character_mentions, node_analyses, character_aliases, character_story_appearances)
- [ ] **CONN-01**: Clicking "I'm Feeling Lucky" does not cause the WebSocket connection indicator to show "disconnected"
- [ ] **CONN-02**: WebSocket connection state remains accurate after any REST API call

### Delivered (v1.0)

(See MILESTONES.md for shipped features)

### Out of Scope

- CI/CD pipelines — not needed for a personal local-first app
- Publishing/packaging — local only, not distributed
- Multi-user support — single-user application
- Cloud deployment — runs entirely on the developer's machine
- Graph layout switcher (yfiles-style) — deferred, current d3 layouts sufficient

## Context

### Application Architecture

The primary application lives in `02-worktrees/webapp-ui/` as a monorepo:

```
webapp-ui/
├── backend/           # FastAPI + SQLite
│   └── app/           # Routers, services, models, database migrations
└── frontend/          # SvelteKit SPA
    └── src/lib/       # Components, stores, API clients, Tiptap extensions
```

- **Backend:** FastAPI serves REST endpoints and WebSocket on port 8000. SQLite database auto-created at `backend/data/stories.db`.
- **Frontend:** SvelteKit SPA on port 5173 (Vite dev server proxies `/api` and `/ws` to backend).
- **Editor:** Tiptap 3 with custom `provenance` mark — inline style attributes survive copy/paste.
- **Graph:** d3-hierarchy computes SVG tree layout. Character supernodes show initials. Click nodes to switch branches. Click seed nodes for seed-guided generation.

### Repository Structure

- `00-experiments` branch is the base Python environment — all project branches fork from it
- `02-worktrees/` contains git worktree checkouts (gitignored except `README.md`)
- `master` branch has the root README with project demos and screenshots
- `development` branch has the GSD planning work
- `.planning/` contains all project management docs for AI orchestrator context

### Active Worktrees

| Worktree | Purpose |
|----------|---------|
| `webapp-ui` | Primary application (FastAPI + SvelteKit) |
| `demo-marimo-app` | Legacy marimo notebook prototype |
| `experiments-with-models` | LLM model testing notebooks |
| `source` | Exploration notebooks |
| `chinese-prompt` | Chinese language prompt experiments `|
| `presentation` | Presentation/outlining materials |

## Constraints

- **Local-first:** All LLM inference runs locally (Ollama, LM Studio, llama.cpp) or via OpenAI API key
- **Single-user:** No authentication, no multi-user support, module-level config state
- **Branching model:** All new projects branch from `00-experiments` to inherit Python/uv setup
- **Worktree location:** Worktrees live in `02-worktrees/` to keep the root clean
- **Self-contained branches:** Each branch's README fully describes the project independently

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Removed `03-app/` | Redundant with worktree-based workflow | ✓ Good |
| Replaced marimo with FastAPI + SvelteKit | Marimo was limited for custom UI (editor, graph, sidebars). SvelteKit gives full control over layout, styling, and interactivity | ✓ Good — full provenance tracking, graph visualizer, proper persistence |
| SQLite for persistence | Local single-user app — no need for Postgres. aiosqlite provides async access | ✓ Good — simple, zero-config, auto-created |
| OpenAI SDK as universal LLM client | All backends (LM Studio, Ollama, llama.cpp) expose OpenAI-compatible APIs | ✓ Good — one client pattern for 4 backends |
| Svelte 5 runes for state | Class-based stores with `$state`/`$derived` — clean, no external state library | ✓ Good — ThemeState, StoryState, GenerationState singletons |
| CSS custom properties for theming | Runtime theme switching without Tailwind dark: prefix rebuild | ✓ Good — instant toggle, no build step |
| Tiptap 3 for editor | ProseMirror-based, extensible marks for provenance tracking | ✓ Good — custom provenance mark with inline styles |
| d3-hierarchy for graph | Battle-tested tree layout algorithm | ✓ Good — handles branching narratives naturally |
| WebSocket for generation | Real-time character streaming, accept/reject flow | ✓ Good — visual typing effect, responsive UX |
| Branch from `00-experiments` not `master` | `00-experiments` has Python/uv setup ready to go | ✓ Good |
| Provenance via inline style attribute | Survives copy/paste between applications | ✓ Good — provenance travels with text |
| Schema docstrings as LLM system prompts | Pydantic model docstrings are injected into structured output API calls | ✓ Good — single source of truth for LLM instructions |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-28*
