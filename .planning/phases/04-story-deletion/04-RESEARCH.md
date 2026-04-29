# Phase 04: Story Deletion — Research

**Date:** 2026-04-28
**Status:** Complete

## Research Question
What do I need to know to PLAN the story deletion phase well?

---

## 1. Cascade Delete Chain (Backend)

### Current State
The `DELETE /api/stories/{story_id}` endpoint in `stories.py` (line ~340) does a simple `DELETE FROM stories WHERE id = ?`. SQLite `PRAGMA foreign_keys=ON` is active (set in `database.py` lines 28/41), so all `ON DELETE CASCADE` constraints fire automatically.

### Cascade Chain (verified from migrations)
```
stories(id) DELETE
  ├→ nodes(story_id) CASCADE                    [001_initial.sql]
  │   ├→ provenance_spans(node_id) CASCADE      [001_initial.sql]
  │   ├→ character_mentions(node_id) CASCADE    [002_graph_support.sql]
  │   └→ node_analyses(node_id) CASCADE         [002_graph_support.sql]
  ├→ character_aliases(story_id) CASCADE         [003_cross_story_characters.sql]
  └→ character_story_appearances(story_id) CASCADE [003_cross_story_characters.sql]
```

### Gap: Orphaned Canonical Characters
`canonical_characters` has no FK to `stories` — they are standalone global entities. After deleting a story and its cascade, canonical characters that only appeared in that story will have:
- Zero `character_aliases` rows (deleted via cascade from story)
- Zero `character_story_appearances` rows (deleted via cascade from story)

**Need to add:** Post-delete query to find and remove orphaned canonical characters:
```sql
DELETE FROM canonical_characters
WHERE id NOT IN (SELECT canonical_id FROM character_aliases)
  AND id NOT IN (SELECT canonical_id FROM character_story_appearances)
```

This is safe because `canonical_characters` cascades to `character_aliases` and `character_story_appearances` on delete — but those are already empty for orphans, so it's a clean delete.

### Implementation Approach
Add the orphan cleanup query to the existing `delete_story()` endpoint in `stories.py`, right after `DELETE FROM stories` and before `commit()`. No new endpoint needed.

---

## 2. Missing Story Update Endpoint

### Finding
CONTEXT.md decision D-08 mentions "Edit mode on the card back shows editable title and premise fields... Saves via existing `PATCH /api/stories/{story_id}` or equivalent update endpoint."

**There is no PATCH endpoint for updating story title/premise.** The only PATCH endpoints are:
- `PATCH /{story_id}/nodes/{node_id}` — updates node content
- `PATCH /{story_id}/active-path` — switches active branch

**For the Edit feature (D-07, D-08), a new endpoint is needed:**
```python
@router.patch("/{story_id}", response_model=StoryResponse)
async def update_story(story_id: str, req: UpdateStoryRequest):
    # Update title and/or premise
```

This is a prerequisite for the card-back edit feature.

---

## 3. Card Flip Pattern (CSS)

### Technical Approach
CSS 3D transform card flip is a well-established pattern. The implementation needs:

```html
<div class="card-flip-container">
  <div class="card-inner">
    <div class="card-front"><!-- existing card content --></div>
    <div class="card-back"><!-- delete/edit/batch options --></div>
  </div>
</div>
```

```css
.card-flip-container {
  perspective: 1000px;
}
.card-inner {
  transition: transform 0.4s ease;
  transform-style: preserve-3d;
}
.card-inner.flipped {
  transform: rotateY(180deg);
}
.card-front, .card-back {
  backface-visibility: hidden;
  position: absolute;
  inset: 0;
}
.card-back {
  transform: rotateY(180deg);
}
```

### Key Considerations
- **Grid dimensions must not shift:** The card maintains its exact `min-height: 140px` from `.story-card`. Both front and back faces need to fill the container.
- **The card is currently `onclick={handleOpen}` on the outer div:** Need `stopPropagation()` on the trash icon and all card-back interactive elements.
- **Svelte 5 reactivity:** Use a `let isFlipped = $state(false)` per card. The trash icon click sets `isFlipped = true`.
- **Click outside to unflip:** Can use a `Svelte.use:clickOutside` action or an `$effect` that listens for clicks outside the card-back. Alternatively, add a transparent overlay behind the flipped card.

### Accessibility
- The card flip is a visual pattern, not a semantic one. The back face should have proper `role="dialog"` and focus management.
- Escape key should flip back (already noted in D-10 for batch mode — applies to card flip too).

---

## 4. Batch Delete Mode

### Entry Points (from CONTEXT D-09)
1. Card flip back face "Select Multiple" button
2. Long-press on a card (mousedown timer)
3. Shift-click on a card

### State Management
Batch mode is dashboard-level state, not per-card state. It should live in `Dashboard.svelte`:
```typescript
let batchMode = $state(false);
let selectedStoryIds = $state<Set<string>>(new Set());
```

Pass these as props to `StoryCard`:
```typescript
<StoryCard {story} {batchMode} {selectedStoryIds} onselect={...} onflip={...} />
```

### Exit Triggers (D-10)
- Cancel button in toolbar
- Escape key
- After batch delete completes

### Batch Delete Implementation
Two options:
1. **Loop individual DELETE calls** — simpler, reuses existing endpoint, handles partial failures gracefully
2. **New batch DELETE endpoint** — more efficient, single transaction

**Recommendation:** Loop individual calls. With 2-5 stories typical, the overhead is negligible. Partial failure UX is cleaner (show which failed vs which succeeded). No new backend code needed.

---

## 5. StoryCard Component Refactoring

### Current Structure
`StoryCard.svelte` is a flat card with: header (title + date) → premise → footer (characters + node count).

### Needed Changes
1. **Wrap content in flip container** — The entire existing card becomes `.card-front`
2. **Add `.card-back` face** — Contains Delete/Edit/Select Multiple buttons
3. **Add trash icon to card-front header** — Visible on hover, triggers flip
4. **Move date to footer** — Per D-02, date moves from header to footer
5. **Add batch mode checkbox** — Conditional rendering when `batchMode` prop is true
6. **Add edit form** — On card-back, when "Edit" is clicked, show title/premise edit fields

### Component Props Evolution
```typescript
// Before
let { story }: { story: StoryOverviewStory } = $props();

// After
let {
  story,
  batchMode = false,
  selected = false,
  onselect,
  ondelete,
  onedit
}: {
  story: StoryOverviewStory;
  batchMode?: boolean;
  selected?: boolean;
  onselect?: (id: string, multi: boolean) => void;
  ondelete?: (id: string) => void;
  onedit?: (id: string, title: string, premise: string) => void;
} = $props();
```

### Event Flow
1. **Trash icon click** → `stopPropagation()` → flip card
2. **Card back "Delete" click** → call `ondelete(story.id)` → Dashboard calls `storyState.deleteStory()`
3. **Card back "Edit" click** → toggle edit form on card back
4. **Card back "Select Multiple" click** → bubble up to Dashboard → activate batch mode
5. **Batch mode checkbox click** → `stopPropagation()` → toggle selection
6. **Card front click (no batch mode)** → `handleOpen()` (existing behavior)
7. **Card front click (batch mode)** → toggle selection instead of opening

---

## 6. Dashboard Component Changes

### State Additions
```typescript
let batchMode = $state(false);
let selectedStoryIds = $state<Set<string>>(new Set());
```

### New Functions
```typescript
function enterBatchMode() { batchMode = true; }
function exitBatchMode() { batchMode = false; selectedStoryIds.clear(); }
function toggleStorySelection(id: string) { ... }
async function deleteSelectedStories() { ... }
async function handleStoryDelete(id: string) { ... }
async function handleStoryEdit(id: string, title: string, premise: string) { ... }
```

### Toolbar Additions
When `batchMode` is true, show a toolbar bar:
- "Delete Selected (N)" button (destructive red)
- "Cancel" button

### Post-Delete Behavior (D-06)
After deleting (single or batch), always return to dashboard. The existing `storyState.deleteStory()` auto-selects the first remaining story — this needs to change. Instead:
```typescript
// In handleStoryDelete:
await storyState.deleteStory(id);
await loadOverview(); // Refresh grid
// Ensure we're on dashboard (activeStoryId should be null)
```

The store's `deleteStory()` currently does:
```typescript
if (this.activeStoryId === id) {
    this.activeStoryId = this.stories.length > 0 ? this.stories[0].id : null;
}
```
This auto-opens the next story. For Phase 04, the Dashboard should handle this by calling `storyState.clearActiveStory()` after deletion to ensure dashboard view.

---

## 7. Store Changes

### `storyState.deleteStory()` — No Changes Needed
The existing method works fine. The Dashboard will handle post-delete routing (clearing active story to return to dashboard).

### Potential New Method: `deleteMultipleStories()`
```typescript
async deleteMultipleStories(ids: string[]): Promise<void> {
    for (const id of ids) {
        await this.deleteStory(id);
    }
}
```
Or just loop `deleteStory()` from the Dashboard. Either approach works.

---

## 8. Backend: New Story Update Endpoint

### Required for D-08 (Edit on card back)
```python
class UpdateStoryRequest(BaseModel):
    title: Optional[str] = None
    premise: Optional[str] = None

@router.patch("/{story_id}", response_model=StoryResponse)
async def update_story(story_id: str, req: UpdateStoryRequest):
    async with get_db() as db:
        # Verify story exists
        # UPDATE stories SET title=?, premise=?, updated_at=datetime('now') WHERE id=?
        # Return updated story
```

The frontend API client also needs a matching `updateStory()` method.

---

## 9. Visual Reference Check

The current card layout (from `StoryCard.svelte`):
- **Header:** Title (left) + Date "Today"/"Yesterday" (right)
- **Body:** Premise text (3-line clamp)
- **Footer:** Character badges (left) + "X paragraphs" (right)

After changes:
- **Header:** Title only (date moves to footer)
- **Header hover:** Trash icon appears top-right
- **Body:** Premise text (unchanged)
- **Footer:** Character badges (left) + Date · Paragraphs (right)
- **Back face:** "Delete [title]?" + Delete button + Cancel + Select Multiple + Edit

---

## 10. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Orphan canonical characters cluttering DB | Medium | Post-delete cleanup query in backend |
| Card flip animation jank with grid layout | Low | Use `position: absolute` for back face, preserve card dimensions |
| Batch delete partial failure leaves inconsistent UI | Medium | Loop individual deletes, refresh overview after each, show errors inline |
| Long-press conflicting with mobile scroll | Low | Use 300ms threshold, cancel on mousemove/touchmove |
| Missing PATCH story endpoint blocks D-08 | High | Add endpoint in same plan as card flip UI |
| Escape key handler conflicts between card flip and batch mode | Low | Card flip handler only fires when card is flipped AND not in batch mode edit |

---

## 11. Implementation Order Recommendation

Based on dependency analysis:

**Wave 1 — Backend + Core Delete:**
1. Add orphan canonical character cleanup to `delete_story()` endpoint
2. Add `PATCH /api/stories/{story_id}` update endpoint + frontend API method
3. Add trash icon to StoryCard, card flip, single delete flow

**Wave 2 — Enhanced UX:**
1. Batch mode (Dashboard state + StoryCard checkbox + toolbar)
2. Card-back edit form (title + premise editing)
3. Date move to footer, polish animations

---

## RESEARCH COMPLETE

Key findings:
1. **Backend cascade is complete** — foreign keys handle everything except orphan canonical characters
2. **Missing PATCH story endpoint** — must be created for card-back edit feature
3. **Card flip is a new CSS pattern** — no existing overlay/modal patterns in the app to reference
4. **Batch mode is Dashboard-level state** — StoryCard receives props, bubbles events up
5. **Post-delete routing** — must clear `activeStoryId` to stay on dashboard (store currently auto-opens next story)
6. **Store needs no breaking changes** — `deleteStory()` works as-is, Dashboard handles routing
