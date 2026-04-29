# Phase 04: Story Deletion - Context

**Gathered:** 2026-04-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a delete story button on dashboard story cards with cascade cleanup. Trash icon on cards triggers a card-flip confirmation, batch mode allows selecting and deleting multiple stories at once. Backend cascade already works via foreign keys but needs orphaned canonical character cleanup. Frontend needs the UI trigger — the full state management layer (store method, API client) already exists.

</domain>

<decisions>
## Implementation Decisions

### Trash Icon Placement
- **D-01:** Trash icon top-right corner of the card, visible on hover only. `onclick` with `stopPropagation()` to prevent card open.
- **D-02:** Move the date from top-right header down to the footer, aligned with the paragraph count. Card header becomes title only — cleaner, makes room for the trash icon hover area.

### Confirmation Dialog (Card Flip)
- **D-03:** Confirmation is a CSS card-flip animation — card rotates (Y-axis) to reveal the back face with "Delete [title]?" message, "Delete" (destructive red) button, and "Cancel" button. Card maintains its exact grid dimensions (no layout shift).
- **D-04:** "Cancel" button and clicking outside the card both flip back to the normal front face. The back face presents a small action menu: Delete, Select Multiple, Edit.

### Orphan Cleanup
- **D-05:** Backend auto-deletes canonical characters that become orphaned after a story deletion — i.e., canonical characters with zero `character_story_appearances` and zero `character_aliases` remaining. Keeps the database clean of stale records.

### Post-Delete UX
- **D-06:** After deleting, always return to the dashboard (never auto-open the next story). If the last story was deleted, show the empty state (per Phase 03 D-12: centered "Create Your First Story" + "I'm Feeling Lucky" buttons).

### Card Flip Options (Edit + Delete + Batch)
- **D-07:** Card flip back face has three options: (1) "Delete" — triggers the destructive delete flow, (2) "Select Multiple" — activates batch selection mode, (3) "Edit" — allows editing the story title and premise inline on the back face.
- **D-08:** Edit mode on the card back shows editable title and premise fields (pre-filled with current values), with a "Save" and "Cancel" button. Saves via existing `PATCH /api/stories/{story_id}` or equivalent update endpoint.

### Batch Delete Mode
- **D-09:** Three entry points to activate batch mode: (1) Card flip back face "Select Multiple" button (D-07), (2) Long-press on a card, (3) Shift-click on a card.
- **D-10:** In batch mode, all cards show checkboxes. Selected cards get a highlight/border accent. A "Delete Selected (N)" button appears in the dashboard toolbar. "Cancel" button or pressing Escape exits batch mode and unchecks everything.
- **D-11:** Batch delete confirmation — one confirmation for all selected stories (agent decides exact presentation: could be a card flip on first selected card, or a toolbar-area confirmation). Backend implementation: loop existing DELETE endpoint or add a batch endpoint (agent's discretion).

### the agent's Discretion
- Exact card flip animation timing and easing
- Checkbox positioning and styling within cards
- Batch mode toolbar button styling
- Whether batch delete uses N individual API calls or a single batch endpoint
- Whether story title/premise update needs a new backend endpoint or if one already exists (check routers)
- Edit form layout on card back face (stacked fields, single-line title + multi-line premise)
- Highlight/border accent color for selected cards in batch mode
- "Select Multiple" button styling on the card back face

</decisions>

<specifics>
## Specific Ideas

- Card flip animation should feel smooth and quick — the card stays in place, content swaps via rotation. Reference: standard CSS `transform: rotateY(180deg)` with `perspective` on the parent.
- Batch mode entry via the card flip back face is the discoverable path — the "Select Multiple" text appears alongside "Delete" and "Edit" so users see all card actions naturally. Long-press and shift-click are power-user shortcuts for batch mode only.
- Date badge moves from card header to footer — sits next to the "X paragraphs" count. Footer becomes: `[character badges] ... [date] · [X paragraphs]`

### Visual Reference
- `00-supporting-files/images/story-card-delete-layout.png` — Screenshot of current story card layout showing title, date ("Yesterday"), premise, character badges, and paragraph count. This is the starting point for the redesign.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Story Card (UI target)
- `02-worktrees/webapp-ui/frontend/src/lib/components/StoryCard.svelte` — Current card component. Entire card is `onclick={handleOpen}`. Date is in `.card-header` next to title. This is where trash icon, card flip, and checkbox changes go.
- `02-worktrees/webapp-ui/frontend/src/lib/components/Dashboard.svelte` — Dashboard parent. Contains grid of StoryCards, toolbar area, empty state, create form. Batch mode toolbar button goes here.

### Backend Delete (cascade verification)
- `02-worktrees/webapp-ui/backend/app/routers/stories.py` — `delete_story()` endpoint (line ~310). Currently only deletes the story row. Foreign key CASCADE handles nodes, spans, mentions, analyses, aliases, appearances. Need to add orphan canonical character cleanup after the story delete.
- `02-worktrees/webapp-ui/backend/app/db/migrations/001_initial.sql` — Stories and nodes tables with `ON DELETE CASCADE` foreign keys.
- `02-worktrees/webapp-ui/backend/app/db/migrations/003_cross_story_characters.sql` — `canonical_characters`, `character_aliases`, `character_story_appearances` tables. Aliases and appearances have `ON DELETE CASCADE` referencing stories. Canonical characters are standalone — no cascade.

### Frontend State (already built)
- `02-worktrees/webapp-ui/frontend/src/lib/stores/story.svelte.ts` — `deleteStory()` method already handles: filtering story list, clearing cache, auto-selecting next story. May need adjustment for "always return to dashboard" behavior.
- `02-worktrees/webapp-ui/frontend/src/lib/api/rest.ts` — `deleteStory()` API client method already exists (DELETE request, handles 204).

### Existing Delete Pattern (for consistency)
- `02-worktrees/webapp-ui/frontend/src/lib/components/CharacterProfilePanel.svelte` — Uses browser native `confirm()` for character deletion. Story deletion uses the card-flip pattern instead — more polished, but native confirm is the existing app convention for destructive actions.

### Planning Context
- `.planning/codebase/ARCHITECTURE.md` — Full architecture docs.
- `.planning/codebase/CONVENTIONS.md` — Svelte 5 runes, CSS custom properties, component patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `storyState.deleteStory()`: Fully functional — filters list, clears cache, handles active story edge case. Just needs UI to trigger it.
- `api.deleteStory()`: API client method already handles the DELETE request and 204 response.
- `Dashboard.svelte`: Has `loadOverview()` for refreshing story list after mutations. Has empty state rendering already.
- CSS custom properties (`--panel-bg`, `--border-color`, `--hover-bg`, etc.): Consistent theming tokens available for card flip and batch mode styling.

### Established Patterns
- Svelte 5 runes (`$state`, `$props`, `$effect`) for all component state
- CSS custom properties for theming (dark/light mode)
- `stopPropagation()` needed for interactive elements inside clickable containers
- No existing modal/overlay pattern in the app — card flip is a new pattern

### Integration Points
- `StoryCard.svelte`: Primary file to modify — add trash icon, card flip markup, batch mode checkbox
- `Dashboard.svelte`: Add batch mode state, toolbar button, "Delete Selected" action
- `story.svelte.ts` store: May need a `deleteMultipleStories()` method for batch mode, or loop `deleteStory()`
- `stories.py` backend: Add orphan cleanup logic to `delete_story()` endpoint — after cascade, query for canonical characters with zero appearances and zero aliases, delete them

### Important Note on Foreign Keys
The SQLite schema has `PRAGMA foreign_keys=ON` set in `get_db()`. All cascade constraints are active:
- `stories(id)` DELETE → cascades to `nodes`, `character_aliases`, `character_story_appearances`
- `nodes(id)` DELETE → cascades to `provenance_spans`, `character_mentions`, `node_analyses`
- `canonical_characters(id)` DELETE → cascades to `character_aliases`, `character_story_appearances`

So deleting a story row automatically cleans up nodes, spans, mentions, analyses, aliases, and appearances. The only gap is orphaned `canonical_characters` with no remaining linked records.

</code_context>

<deferred>
## Deferred Ideas

- Story export before delete (safety net) — future phase consideration
- Undo delete with a grace period — future phase consideration

</deferred>

---

*Phase: 04-story-deletion*
*Context gathered: 2026-04-28*
