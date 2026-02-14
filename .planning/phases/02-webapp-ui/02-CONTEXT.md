# Phase 02: Webapp UI — Discussion Context

## Overview

Replace the current marimo notebook story writer with a purpose-built webapp. The existing Pydantic structured output pipeline (`StoryStart`, `StoryContinue`, `StoryAnalysis`) stays as the core engine; the webapp provides a proper editor-centric UI inspired by NovelAI's interface, with branching story support designed in from the start.

## Decisions

### Tech Stack

| Decision | Choice | Notes |
|----------|--------|-------|
| Backend | FastAPI + Uvicorn | Python, ports existing LLM client/structured output code |
| Frontend | Svelte + Tailwind CSS | |
| Repo structure | Monorepo | `backend/` and `frontend/` in same branch |

### Editor Experience

| Decision | Choice | Notes |
|----------|--------|-------|
| Draft flow | Inline display | AI text appears in editor visually distinguished (color/opacity) until accepted/rejected. No separate draft textarea. |
| Editing | Rich text editor | Click anywhere to edit, supports markdown formatting |
| Color-coding by source | v1, per character span | AI-generated=white, user-written=blue, user-edits=pink, initial prompt=cream. Tracked at the character span level (not paragraph level). |
| Node graph | v2 for rendering, v1 for data model | ComfyUI / Unreal Blueprints style. Data model must fully support branching from v1; visual graph editor is v2. |

### Layout & Panels

| Decision | Choice | Notes |
|----------|--------|-------|
| Primary view | Split pane (editor + graph), resizable | Editor on one side, graph placeholder on the other |
| Settings / backend config | Collapsible left sidebar | VS Code style |
| Story analysis panel | Collapsible right sidebar | Structured display: cards/sections for cast, timeline, world_rules, etc. Not raw JSON. |
| Theme | Dark default, light mode toggle | |

### Scope (v1 vs v2)

| Feature | Version | Notes |
|---------|---------|-------|
| LLM backends | v1: lmstudio, ollama, openai, llamacpp | Azure deferred |
| Persistence | v1: SQLite + markdown export | |
| Node graph rendering | v2 | v1 ships with data model only |
| Model warmup | v1 | Progress indicator on model load |
| Branching workflow | v1: data model. v2: visual graph | |

### Data Model

| Decision | Choice | Notes |
|----------|--------|-------|
| Atomic unit | Switchable: paragraph, arbitrary block, sentence | User can switch granularity. All three modes supported. |
| Branch semantics | Fork at any point + multiple options per node | Both modes: fork the story at a paragraph to create a new branch, AND have multiple "next" candidates at any node |
| Provenance tracking | Per character span | Every span of text tagged with source: `ai_generated`, `user_written`, `user_edited`, `initial_prompt`. Enables NovelAI-style color coding. |

## Reference Material

### Current App

- `02-worktrees/demo-marimo-app/app.py` (820 lines)
- Marimo notebook, 5 LLM backends, Pydantic structured output
- Flow: premise -> StoryStart -> story textarea + draft textarea -> generate (run_cycle: StoryAnalysis -> StoryContinue) -> approve/discard
- Schemas: `StoryStart` (premise + opening_paragraph), `StoryContinue` (next_paragraph), `StoryAnalysis` (logline, cast, world_rules, pov_tense_tone, timeline, current_situation, active_threads, continuity_landmines, ambiguities, next_paragraph_seeds)

### NovelAI Editor Reference

- Color-coded text by source (user input=blue, AI generated=white, user edits=pink, initial prompt=cream)
- Undo/redo history tree (not linear)
- Retry/branching at any point
- Inline generation at cursor
- Editor V2 with dynamic loading

### Screenshot Reference

- `00-supporting-files/images/README/` — current marimo UI screenshots
- Shows two-column grid: settings left, story + controls right
- Premise textarea, story textarea, draft textarea, analysis JSON panel

## Open Questions for Planning

1. Which rich text editor library for Svelte? (Tiptap, ProseMirror, CodeMirror, custom)
2. SQLite schema design — how to model the tree of paragraph nodes with span-level provenance
3. WebSocket vs SSE for streaming AI generation to the frontend
4. How to handle the switchable atomic unit (paragraph/block/sentence) in the data model — is it a view-layer concern or stored differently?
5. Graph rendering library for v2 (Svelte Flow, D3, Xyflow, custom canvas)

## Non-Goals (v1)

- Azure backend support
- Visual node graph rendering (data model only)
- Multi-user / collaboration
- Cloud deployment / auth
- Mobile-responsive layout
