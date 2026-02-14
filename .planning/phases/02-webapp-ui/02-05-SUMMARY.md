---
phase: 02-webapp-ui
plan: 05
subsystem: api
tags: [websocket, fastapi, svelte5, tiptap, provenance, streaming, draft-flow]

# Dependency graph
requires:
  - phase: 02-webapp-ui/01
    provides: FastAPI backend with SQLite schema, LLM service layer (run_cycle, create_llm_client)
  - phase: 02-webapp-ui/03
    provides: Tiptap editor with custom Provenance mark extension (4 source colors)
  - phase: 02-webapp-ui/04
    provides: REST API routers, LLM config module-level state, typed frontend API client
provides:
  - WebSocket endpoint at /ws/generate for bidirectional generation messaging
  - Draft node lifecycle: create (is_draft=1) → stream tokens → accept (is_draft=0) or reject (delete)
  - Token-by-token streaming with 10ms delay for visual streaming effect
  - Frontend WebSocket client with auto-reconnect (exponential backoff, 5 attempts)
  - GenerationState store tracking status, draft content, analysis, connection state
  - GenerationControls component with Generate/Cancel/Accept/Reject buttons
  - Editor integration: streamed tokens inserted with ai_generated provenance mark
  - User-typed text automatically gets user_written provenance via handleTextInput
  - WebSocket connection status indicator (green/yellow/red dot)
affects: [02-webapp-ui/06]

# Tech tracking
tech-stack:
  added: []
  patterns: [fastapi-websocket-endpoint, ws-message-loop, svelte5-effect-streaming, tiptap-insertContent-with-marks, handleTextInput-provenance]

key-files:
  created:
    - 02-worktrees/webapp-ui/backend/app/routers/ws.py
    - 02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts
    - 02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts
    - 02-worktrees/webapp-ui/frontend/src/lib/components/GenerationControls.svelte
  modified:
    - 02-worktrees/webapp-ui/backend/app/main.py
    - 02-worktrees/webapp-ui/frontend/src/lib/components/Editor.svelte
    - 02-worktrees/webapp-ui/frontend/src/routes/+page.svelte
    - 02-worktrees/webapp-ui/frontend/src/lib/types/index.ts

key-decisions:
  - "run_cycle() returns full result then streams char-by-char with 10ms delay — visual streaming with structured output API"
  - "Model name sent in generate message from frontend — uses settingsState.model already selected by user"
  - "User-typed text provenance applied via handleTextInput ProseMirror prop — intercepts input and wraps with user_written mark"

patterns-established:
  - "WebSocket message loop pattern: type-based dispatch with generate/cancel/accept/reject"
  - "GenerationState class centralizes all generation lifecycle (connect, send, handle messages)"
  - "Editor $effect() watches generationState.draftContent for token-by-token insertion"

# Metrics
duration: 3min
completed: 2026-02-14
---

# Phase 02 Plan 05: WebSocket Generation Streaming Summary

**WebSocket-based AI generation pipeline with token-by-token streaming into Tiptap editor, draft node lifecycle (create/accept/reject), and 4-color provenance marking**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-14T03:55:21Z
- **Completed:** 2026-02-14T03:59:16Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- End-to-end generation flow: Generate → tokens stream into editor with ai_generated (white) provenance → Accept persists / Reject removes
- WebSocket endpoint handles 4 message types with draft node SQLite lifecycle (create as is_draft=1, accept flips to 0, reject deletes)
- Frontend WebSocket client with exponential backoff reconnection (1s, 2s, 4s, 8s, 16s, max 5 attempts)
- GenerationControls button bar with connection status indicator and contextual button display

## Task Commits

Each task was committed atomically:

1. **Task 1: Build WebSocket generation endpoint and client** - `04e4723` (feat)
2. **Task 2: Integrate generation flow into editor with provenance marks** - `be5b015` (feat)

## Files Created/Modified
- `backend/app/routers/ws.py` - WebSocket endpoint at /ws/generate with generate/cancel/accept/reject message handling
- `backend/app/main.py` - Updated to include WebSocket router
- `frontend/src/lib/api/ws.ts` - WebSocket client class with auto-reconnect and typed messages
- `frontend/src/lib/stores/generation.svelte.ts` - GenerationState class with status tracking, message dispatch, connection management
- `frontend/src/lib/components/GenerationControls.svelte` - Generate/Cancel/Accept/Reject button bar with connection indicator
- `frontend/src/lib/components/Editor.svelte` - Draft text insertion via $effect(), user_written provenance via handleTextInput, draft removal on reject
- `frontend/src/routes/+page.svelte` - WebSocket lifecycle (connect on mount, disconnect on destroy), GenerationControls added
- `frontend/src/lib/types/index.ts` - Fixed StoryAnalysis type to match backend (string[] fields not string)

## Decisions Made
- **run_cycle() then stream:** The structured output API (run_cycle) returns the full result at once. To create a streaming visual effect, we stream the result character-by-character with 10ms delays. This gives NovelAI-style token streaming while preserving the structured output guarantees.
- **Model in generate message:** The model name is sent from the frontend in the generate WebSocket message rather than reading from LLM config endpoint — avoids an extra API call and uses the model already selected by the user.
- **handleTextInput for provenance:** User-typed text is intercepted via ProseMirror's handleTextInput prop and re-inserted with user_written provenance mark. This ensures all user input is automatically color-coded blue.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed StoryAnalysis TypeScript type to match backend**
- **Found during:** Task 1 (creating WebSocket client types)
- **Issue:** Frontend StoryAnalysis interface had all `string` fields but backend Pydantic model has `list[str]` for cast, world_rules, timeline, active_threads, continuity_landmines, ambiguities, next_paragraph_seeds
- **Fix:** Changed those fields to `string[]` in types/index.ts
- **Files modified:** frontend/src/lib/types/index.ts
- **Committed in:** 04e4723 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Type mismatch would have caused runtime errors when displaying analysis data. Essential fix.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- WebSocket generation pipeline complete, ready for Plan 06 (Analysis panel displays StoryAnalysis from generation)
- GenerationState.lastAnalysis holds the latest StoryAnalysis for Plan 06 to render
- Story loading from SQLite ready for Plan 06 (restore story content with provenance on page refresh)
- Markdown export in Plan 06 can walk active_path and concatenate node contents

## Self-Check: PASSED

- All 8 key files verified on disk
- Both task commits verified (04e4723, be5b015)
- svelte-check: 0 errors, 0 warnings
- Backend WebSocket router imports successfully

---
*Phase: 02-webapp-ui*
*Completed: 2026-02-14*
