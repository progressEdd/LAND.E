# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-13)

**Core value:** Every experiment/feature branch is self-documenting from creation — branching, worktree setup, README population, and project naming happen automatically so you can start building immediately.
**Current focus:** Phase 4 (Webapp UI) — Plan 02-11 COMPLETE (Bug Fixes: provenance visibility, graph rework, node labels). All plans complete.

## Current Position

Phase: 4 of 4 (Webapp UI) — Plan 02-11 COMPLETE
Plan: 11 in current phase — COMPLETE
Status: Bug fixes applied — provenance marks use background tints for theme compatibility, graph reworked to bipartite circle design, node labels fixed to show tree depth.
Last activity: 2026-02-14 — Completed 02-11-PLAN.md (Bug Fixes)

Progress: [██████████] 100% (11/11 plans in Phase 4)

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: 2.0 min
- Total execution time: 0.3 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Template Preparation | 1/1 | 1 min | 1 min |
| 2. Branch Creation Flow | 1/1 | 2 min | 2 min |
| 3. Root README Index | 1/1 | 1 min | 1 min |
| 4. Webapp UI | 8/9 | 18 min | 2.3 min |

**Recent Trend:**
- Last 5 plans: 02-02-webapp (3 min), 02-03-webapp (2 min), 02-04-webapp (3 min), 02-05-webapp (3 min), 02-06-webapp (4 min)
- Trend: stable

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: 3 phases derived — Template Prep, Branch Creation Flow, Root README Index. Research suggested a 4th phase (Lifecycle Management) but no v1 requirements map to it — deferred to v2.
- [02-01-webapp]: Used FastAPI lifespan context manager instead of deprecated on_event('startup')
- [02-01-webapp]: Preserved schema docstrings exactly from marimo app — they serve as LLM system prompts
- [02-01-webapp]: Used asyncio.to_thread() to wrap synchronous OpenAI SDK calls for async FastAPI
- [02-02-webapp]: Svelte 5 runes class pattern for state management (ThemeState, SettingsState singletons)
- [02-02-webapp]: CSS custom properties for theming instead of Tailwind dark: prefix — enables runtime theme switching
- [02-02-webapp]: Updated root .gitignore to negate lib/ exclusion for frontend/src/lib/

- [02-03-webapp]: Used TypeScript getter properties instead of $derived() for EditorState — cleaner with Tiptap Editor type
- [02-03-webapp]: Provenance mark renders via inline style attribute — survives copy/paste between applications

- [02-04-webapp]: LLM config stored as module-level variable (single-user app) — no DB persistence needed
- [02-04-webapp]: Used $effect() for initial story list load on SettingsPanel mount
- [02-04-webapp]: Svelte 5 event handler: onclick with e.stopPropagation() instead of |stopPropagation modifier

- [02-05-webapp]: run_cycle() returns full result then streams char-by-char with 10ms delay — visual streaming with structured output API
- [02-05-webapp]: Model name sent in generate WebSocket message from frontend — avoids extra API call
- [02-05-webapp]: User-typed text provenance via handleTextInput ProseMirror prop — intercepts and wraps with user_written mark

- [02-06-webapp]: Added ProvenanceSpanResponse to backend and included spans in get_story endpoint for content restoration
- [02-06-webapp]: Used loadedStories cache map in story store to avoid redundant API calls when switching stories
- [02-06-webapp]: Async setActiveStory() auto-loads full story data if not cached

### Pending Todos

None.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-14
Stopped at: Completed 02-11-PLAN.md (Bug Fixes: provenance visibility, graph rework, node labels). All Phase 4 plans complete.
Resume file: None — all planned work complete
