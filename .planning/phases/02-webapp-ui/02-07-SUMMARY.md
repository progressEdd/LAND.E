---
phase: 02-webapp-ui
plan: 07
subsystem: ui
tags: [random-premise, settings-panel, rest-api, ux]

# Dependency graph
requires:
  - phase: 02-webapp-ui/04
    provides: REST API client, SettingsPanel with new story form
provides:
  - GET /api/stories/random-premise endpoint returning a random premise from a curated pool of 25
  - "I'm Feeling Lucky" button in the new story form that fills the premise textarea
  - randomPremise() method on the frontend API client
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: [random-selection-endpoint, dashed-border-button-style]

key-files:
  created: []
  modified:
    - 02-worktrees/webapp-ui/backend/app/routers/stories.py
    - 02-worktrees/webapp-ui/frontend/src/lib/api/rest.ts
    - 02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte

key-decisions:
  - "Used a hardcoded premise pool on the backend rather than LLM-generated premises — instant response, no model dependency, deterministic"
  - "Button uses dashed border style to visually distinguish it from primary actions"

patterns-established:
  - "Random content endpoint pattern: stateless GET returning a random selection from a curated pool"

# Metrics
duration: 2min
completed: 2026-02-14
---

# Phase 02 Plan 07: Random Premise Generator Summary

**"I'm Feeling Lucky" button in the new story form that fills the premise textarea with a random story premise from a curated pool of 25 premises**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-14
- **Completed:** 2026-02-14
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments
- Backend endpoint GET /api/stories/random-premise returns a random premise from a pool of 25 curated story premises spanning sci-fi, mystery, horror, literary fiction, and magical realism
- Frontend API client method randomPremise() wraps the endpoint
- "I'm Feeling Lucky" button appears in the new story form between the premise textarea and the Create/Cancel buttons, with dashed border styling and loading state

## Task Commits

1. **Task 1: Add random premise endpoint and frontend button** — (feat)

## Files Modified
- `backend/app/routers/stories.py` — Added PREMISES list (25 entries) and GET /random-premise endpoint before story_id routes
- `frontend/src/lib/api/rest.ts` — Added randomPremise() method to ApiClient
- `frontend/src/lib/components/SettingsPanel.svelte` — Added feelingLucky() function, isLoadingPremise state, "I'm Feeling Lucky" button with .btn-lucky styling

## Decisions Made
- **Hardcoded pool over LLM generation:** Random premises come from a curated list rather than calling the LLM. This gives instant response without requiring a running model, and the premises are higher quality since they're hand-crafted.
- **Dashed border button:** The lucky button uses a dashed border to visually separate it from the primary Create action, signaling it's an optional helper rather than a required step.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered
None

## Self-Check: PASSED

- All 3 modified files verified
- Endpoint placed before /{story_id} routes to avoid path param collision
- Button has loading state and error handling

---
*Phase: 02-webapp-ui*
*Completed: 2026-02-14*
