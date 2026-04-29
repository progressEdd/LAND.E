---
plan: 04-01
phase: 04-story-deletion
status: complete
started: "2026-04-29T03:15:00.000Z"
completed: "2026-04-29T03:30:00.000Z"
---

# Summary: Plan 04-01 — Story Deletion with Card Flip UI & Batch Mode

## Objective
Add delete story capability to the dashboard with card-flip confirmation, batch delete mode, inline edit on card back, and backend orphan cleanup.

## What Was Built

### Backend
- **Orphan cleanup**: Added `DELETE FROM canonical_characters WHERE id NOT IN (SELECT canonical_id FROM character_aliases) AND id NOT IN (SELECT canonical_id FROM character_story_appearances)` to the `delete_story()` endpoint, cleaning up canonical characters left orphaned after story cascade delete.
- **PATCH endpoint**: New `PATCH /api/stories/{story_id}` endpoint accepting `UpdateStoryRequest` with optional `title` and `premise` fields. Returns full `StoryResponse` via `get_story()` reuse. Placed before DELETE route to avoid routing conflicts.

### Frontend
- **StoryCard rewrite**: Complete rewrite with CSS card-flip animation (0.4s ease-in-out, rotateY 180deg, backface-visibility hidden). Front face shows title, premise, character badges, date/paragraph count in footer, and hover-visible trash icon. Back face shows Delete/Edit/Select Multiple actions. Includes inline edit form with title input and premise textarea.
- **Batch mode**: Batch checkboxes on cards, batch toolbar with "Delete Selected (N)" and "Cancel Selection" buttons. Entry via "Select Multiple" button on card back, shift-click, or long-press (300ms). Escape exits batch mode.
- **Dashboard integration**: New state management (batchMode, selectedStoryIds), event handlers wired to StoryCard props, batch toolbar with slide-in animation.

## Key Decisions
- PATCH endpoint reuses `get_story()` for response to avoid duplicating node/span/mention loading logic
- Card flip uses CSS 3D transforms rather than a modal dialog for a more integrated feel
- Click-outside-to-unflip uses document mousedown listener attached via $effect
- `storyState.clearActiveStory()` called after every delete to ensure dashboard stays visible (never auto-opens next story)

## Files Modified
- `backend/app/routers/stories.py` — Orphan cleanup + PATCH endpoint
- `backend/app/models/schemas.py` — UpdateStoryRequest model
- `frontend/src/lib/api/rest.ts` — updateStory method
- `frontend/src/lib/components/StoryCard.svelte` — Full rewrite
- `frontend/src/lib/components/Dashboard.svelte` — Batch mode + event handlers

## Self-Check: PASSED
- All 5 tasks executed and committed atomically
- Backend: orphan cleanup query uses NOT IN subqueries on both aliases and appearances
- Backend: PATCH endpoint returns 400 for empty body, 404 for missing story
- Frontend: card-flip CSS with perspective, preserve-3d, backface-visibility
- Frontend: trash icon hidden by default, visible on hover
- Frontend: batch mode with checkboxes, toolbar, slide-in animation
- Frontend: Escape key exits batch mode and unflips cards
