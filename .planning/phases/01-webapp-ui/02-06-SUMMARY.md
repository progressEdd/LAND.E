---
phase: 02-webapp-ui
plan: 06
subsystem: ui
tags: [svelte5, tiptap, provenance, analysis-panel, markdown-export, story-loading]

# Dependency graph
requires:
  - phase: 02-05
    provides: "WebSocket generation streaming, draft node lifecycle, provenance marks"
provides:
  - "AnalysisPanel displaying 10 structured StoryAnalysis cards in right sidebar"
  - "AnalysisCard reusable collapsible card component"
  - "Markdown export endpoint (GET /api/stories/{id}/export)"
  - "Story loading flow with provenance mark restoration"
  - "localStorage persistence of active story ID"
  - "Welcome state when no story selected"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Provenance span restoration from DB to Tiptap marks via loadContent()"
    - "Cached story loading with loadedStories map to avoid re-fetching"
    - "localStorage for cross-refresh state persistence"

key-files:
  created:
    - "02-worktrees/webapp-ui/frontend/src/lib/components/AnalysisPanel.svelte"
    - "02-worktrees/webapp-ui/frontend/src/lib/components/AnalysisCard.svelte"
    - "02-worktrees/webapp-ui/backend/app/services/export.py"
  modified:
    - "02-worktrees/webapp-ui/backend/app/routers/stories.py"
    - "02-worktrees/webapp-ui/backend/app/models/schemas.py"
    - "02-worktrees/webapp-ui/frontend/src/lib/stores/story.svelte.ts"
    - "02-worktrees/webapp-ui/frontend/src/lib/components/Editor.svelte"
    - "02-worktrees/webapp-ui/frontend/src/routes/+page.svelte"
    - "02-worktrees/webapp-ui/frontend/src/routes/+layout.svelte"
    - "02-worktrees/webapp-ui/frontend/src/lib/types/index.ts"
    - "02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts"

key-decisions:
  - "Added ProvenanceSpanResponse to backend and included spans in get_story endpoint for content restoration"
  - "Used loadedStories cache map in story store to avoid redundant API calls when switching stories"
  - "Async setActiveStory() auto-loads full story data if not cached"

patterns-established:
  - "Story content loading pattern: fetch story with nodes+spans → build Tiptap doc with provenance marks → set content"
  - "localStorage persistence pattern for activeStoryId with $effect watcher"

# Metrics
duration: 4min
completed: 2026-02-14
---

# Phase 02 Plan 06: Analysis Panel, Export & Story Loading Summary

**AnalysisPanel with 10 structured cards, markdown export endpoint, and story loading with provenance mark restoration across page refreshes**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-14T04:04:45Z
- **Completed:** 2026-02-14T04:08:42Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- Right sidebar now shows 10 structured analysis cards (logline, cast, world rules, POV, timeline, situation, threads, landmines, ambiguities, seeds) with collapsible AnalysisCard components
- Markdown export endpoint walks active_path nodes and produces downloadable .md file with title, premise, content, and export footer
- Story loading restores editor content with correct provenance colors (cream/white/blue/pink) by reading spans from database
- Active story persists across page refresh via localStorage; welcome state shown when no story selected

## Task Commits

Each task was committed atomically:

1. **Task 1: Build analysis panel and markdown export endpoint** - `0f71983` (feat)
2. **Task 2: Story loading flow and app polish** - `922a4f8` (feat)

## Files Created/Modified
- `frontend/src/lib/components/AnalysisPanel.svelte` - 10-card structured display of StoryAnalysis, export button
- `frontend/src/lib/components/AnalysisCard.svelte` - Reusable collapsible card with warning variant (amber)
- `backend/app/services/export.py` - export_story_markdown() walking active_path to produce .md
- `backend/app/routers/stories.py` - GET /export endpoint, updated get_story to include provenance spans
- `backend/app/models/schemas.py` - Added ProvenanceSpanResponse, provenance_spans field on NodeResponse
- `frontend/src/lib/stores/story.svelte.ts` - loadStory(), getActivePathNodes(), lastAnalysis, loadedStories cache
- `frontend/src/lib/components/Editor.svelte` - loadContent() with provenance mark restoration, $effect for story changes
- `frontend/src/routes/+page.svelte` - Story loading flow, localStorage persistence, welcome state
- `frontend/src/routes/+layout.svelte` - Replaced placeholder with AnalysisPanel component
- `frontend/src/lib/types/index.ts` - Added ProvenanceSpan interface to StoryNode
- `frontend/src/lib/stores/generation.svelte.ts` - Use refreshActiveStory() on draft accept

## Decisions Made
- Added ProvenanceSpanResponse to backend schemas and included provenance spans in the get_story endpoint — required for restoring provenance colors when loading stories (was missing from original API)
- Used a loadedStories cache map (Record<string, Story>) in story store to avoid re-fetching stories when switching between them
- Made setActiveStory() async to auto-load full story data when selecting a story that hasn't been loaded yet

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added provenance spans to get_story API response**
- **Found during:** Task 2 (story loading flow)
- **Issue:** The get_story endpoint returned nodes but not their provenance spans — making it impossible to restore provenance colors when loading a story
- **Fix:** Added ProvenanceSpanResponse schema, added provenance_spans field to NodeResponse, updated get_story to fetch and attach spans per node
- **Files modified:** backend/app/models/schemas.py, backend/app/routers/stories.py, frontend/src/lib/types/index.ts
- **Verification:** Backend import check passes, frontend npm run check passes with 0 errors
- **Committed in:** 922a4f8 (Task 2 commit)

**2. [Rule 2 - Missing Critical] Changed loadStories() to refreshActiveStory() on draft accept**
- **Found during:** Task 2 (story loading flow)
- **Issue:** On draft accept, generation store called loadStories() which only fetches summaries without nodes — needed full story reload to update active_path and nodes
- **Fix:** Added refreshActiveStory() method to story store, updated generation store to use it
- **Files modified:** frontend/src/lib/stores/story.svelte.ts, frontend/src/lib/stores/generation.svelte.ts
- **Verification:** npm run check passes
- **Committed in:** 922a4f8 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 missing critical functionality)
**Impact on plan:** Both auto-fixes essential for story loading to work correctly. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- **Phase 02 (Webapp UI) is now complete** — all 6 plans executed
- The webapp delivers the full end-to-end flow: create story → generate AI continuations → accept/reject drafts → view structured analysis → switch stories → export markdown
- Ready for UAT verification

---
*Phase: 02-webapp-ui*
*Completed: 2026-02-14*

## Self-Check: PASSED

All files exist, all commits verified.
