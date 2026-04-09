# Roadmap: LAND.E

## Overview

**v1 (Complete):** Project infrastructure — git worktree template, branch creation workflow, root README index, and the full webapp UI (FastAPI + SvelteKit SPA with Tiptap editor, provenance tracking, WebSocket streaming, node graph, SQLite persistence).

**v2 (Planned):** Dashboard home page, graph rework with character-to-paragraph edges, and cross-story knowledge graph with shared characters.

## Phases

**Phase Numbering:**
- Phase 00: Foundation work (infrastructure, tooling) — already complete
- Phases 01+: Feature work in execution order
- Decimal phases (1.1, 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 00: Infrastructure** - Template prep, branch creation, root README index
- [x] **Phase 01: Webapp UI** - Purpose-built story writer webapp replacing the marimo notebook
- [ ] **Phase 02: Cross-Story Knowledge Graph** - Shared characters across stories, force-directed graph visualization
- [x] **Phase 03: Dashboard + Graph Rework** - Story dashboard home page, in-story character-to-paragraph graph edges

## Phase Details

### Phase 00: Infrastructure
**Goal**: Repository scaffolding, git worktree template system, and root README index
**Status**: Complete (2026-02-13)
**Folder**: `.planning/phases/00-infrastructure/`

Sub-phases (all complete):
- 00a. Template Preparation — README template with `$placeholder` variables on `00-experiments`
- 00b. Branch Creation Flow — New-project workflow: branch, worktree, file population, env setup
- 00c. Root README Index — Master branch README lists active experiments

Plans:
- [x] 01-01-PLAN.md — Create README template with $placeholder variables on 00-experiments
- [x] Branch creation flow (direct execution)
- [x] Root README update (direct execution)

### Phase 01: Webapp UI
**Goal**: A working story writer webapp with AI generation, inline provenance tracking, structured analysis, and persistence — replacing the marimo notebook
**Status**: Complete (2026-02-14)
**Folder**: `.planning/phases/01-webapp-ui/`
**Depends on**: Nothing (independent milestone)
**Branch**: `webapp-ui` (forked from `00-experiments`)
**Worktree**: `02-worktrees/webapp-ui/`
**Success Criteria** (what must be TRUE):
  1. FastAPI backend starts with SQLite database (stories, nodes, provenance_spans tables)
  2. SvelteKit frontend renders with collapsible sidebars, split pane layout, dark/light theme
  3. Tiptap editor supports rich text formatting and 4-color provenance marking (AI=white, user=blue, edits=pink, prompt=cream)
  4. REST API handles stories CRUD, nodes CRUD, LLM backend config, model listing, and warmup
  5. WebSocket streams AI-generated text token-by-token into the editor with provenance marks
  6. User can accept or reject AI drafts; accepted drafts persist, rejected drafts are removed
  7. Analysis panel shows structured StoryAnalysis cards (logline, cast, timeline, etc.) after generation
  8. Stories persist in SQLite and restore with provenance on page refresh
  9. Markdown export produces a downloadable .md file of the active story path
  10. 4 LLM backends supported: lmstudio, ollama, openai, llamacpp
**Plans:** 16 plans (16 complete)

Plans:
- [x] 02-01-PLAN.md — Backend scaffold: FastAPI, SQLite schema, LLM service, story pipeline
- [x] 02-02-PLAN.md — Frontend scaffold: SvelteKit SPA, Tailwind, layout shell, sidebars, theme
- [x] 02-03-PLAN.md — Tiptap editor with custom provenance mark extension and toolbar
- [x] 02-04-PLAN.md — REST API endpoints, frontend API client, settings panel
- [x] 02-05-PLAN.md — WebSocket generation streaming, inline draft flow in editor
- [x] 02-06-PLAN.md — Analysis panel, markdown export, story loading, app polish
- [x] 02-07-PLAN.md — "I'm Feeling Lucky" random premise generator
- [x] 02-08-PLAN.md — Bug fixes: accept truncation, missing space, generating animation, title population, delete button
- [x] 02-09-PLAN.md — Node graph backend: character_mentions table, analysis persistence, tree API, branch switching endpoint
- [x] 02-10-PLAN.md — Frontend graph visualizer: interactive SVG tree, character badges, branch switching UX, active path highlighting
- [x] 02-11-PLAN.md — Bug fixes: light mode provenance visibility, graph visualization rework, node position labels
- [x] 02-12-PLAN.md — Graph hover tooltips and zoom/pan navigation
- [x] 02-13-PLAN.md — Bug fixes: light-mode story highlight, dark-mode provenance visibility, graph label cleanup, edge opacity
- [x] 02-14-PLAN.md — Character initials labels, remove cross-edges from paragraph nodes
- [x] 02-15-PLAN.md — Single-letter character labels, clickable seed nodes with seed-guided generation
- [x] 02-16-PLAN.md — Graph polish: enlarged nodes, theme-aware seed colors, per-node seed persistence, SVG layering fix

### Phase 02: Cross-Story Knowledge Graph
**Goal**: Global character identity across stories, shared universe visualization, cross-story character linking
**Status**: Planned (future)
**Folder**: `.planning/phases/02-cross-story-graph/` (to be created)
**Depends on**: Phase 01 (Webapp UI), Phase 03 (Dashboard + Graph Rework — in-story graph edges first)
**Open questions:**
  - How to identify "same character" across stories? Manual linking? LLM matching?
  - Does the home page become the cross-story graph, or is it a separate view?
  - Need a "universe" concept to group stories?
**Plans:** TBD

### Phase 03: Dashboard + Graph Rework
**Goal**: Replace the welcome placeholder with a story dashboard home page, and rework the node graph visualizer to draw edges from character nodes to the paragraphs where they appear.
**Status**: In Progress
**Folder**: `.planning/phases/03-dashboard-graph-rework/`
**Depends on**: Phase 01 (Webapp UI must be functional)
**Branch**: `webapp-ui` (existing)
**Worktree**: `02-worktrees/webapp-ui/`
**Success Criteria** (what must be TRUE):
  1. Home page shows a dashboard with story cards instead of a text welcome message
  2. Users can create new stories directly from the dashboard without opening the settings panel
  3. Node graph visualizer draws edges from character supernodes to the paragraph nodes where they are mentioned
  4. Graph edges are visually clear and don't clutter the tree layout
  5. Both features work in dark and light themes
**Plans:** TBD after context gathering

## Progress

**Execution Order:**
Phases execute: 00 → 01 → 03 → 02 (Phase 03 before 02 because in-story edges are prerequisite for cross-story graph)

| Phase | Folder | Plans Complete | Status | Completed |
|-------|--------|----------------|--------|-----------|
| 00. Infrastructure | `00-infrastructure` | 1+ | Complete | 2026-02-13 |
| 01. Webapp UI | `01-webapp-ui` | 16/16 | Complete | 2026-02-14 |
| 02. Cross-Story Graph | `02-cross-story-graph` | 0/? | Planned | — |
| 03. Dashboard + Graph Rework | `03-dashboard-graph-rework` | 0/? | Complete | — |
