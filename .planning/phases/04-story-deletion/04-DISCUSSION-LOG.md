# Phase 04: Story Deletion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-28
**Phase:** 04-story-deletion
**Areas discussed:** Trash Icon Placement, Confirmation Dialog (Card Flip), Orphan Cleanup, Post-Delete UX, Batch Delete, Card Flip Options (Edit)

---

## Trash Icon Placement

| Option | Description | Selected |
| ------ | ----------- | -------- |
| Top-right corner, visible on hover | Trash icon fades in on card hover. stopPropagation prevents card open. | ✓ |
| Top-right corner, always visible | Trash icon always showing. More discoverable but noisy. | |
| Footer area, inline with metadata | Next to paragraph count. Always visible but less prominent. | |

**User's choice:** Top-right hover trash icon, with date badge moved from header to footer next to paragraph count.
**Notes:** Card header becomes title-only. Date relocates to footer alongside "X paragraphs". Screenshot of current layout saved to `00-supporting-files/images/story-card-delete-layout.png`.

---

## Confirmation Dialog (Card Flip)

| Option | Description | Selected |
| ------ | ----------- | -------- |
| Custom modal overlay | Centered modal with backdrop blur. Polished but new pattern. | |
| Browser native confirm() | Quick, consistent with existing character deletion. Looks jarring in dark theme. | |
| Card flip animation | Card rotates Y-axis to reveal back face with confirmation. Maintains grid layout. | ✓ |

**User's choice:** Card flip — card rotates to show back face with Delete/Cancel options. Maintains exact card size. Cancel and clicking outside both flip back.
**Notes:** Back face becomes an action menu with Delete, Select Multiple, and Edit options (expanded during discussion).

---

## Orphan Cleanup

| Option | Description | Selected |
| ------ | ----------- | -------- |
| Yes, auto-clean | Delete canonical characters with zero appearances after story delete. Clean database. | ✓ |
| No, leave them | Preserve user-curated character profiles even if orphaned. | |
| Auto-clean only if unedited | Middle ground — delete only unedited orphans. More complex. | |

**User's choice:** Auto-clean. Delete canonical characters that have zero `character_story_appearances` and zero `character_aliases` after story deletion.

---

## Post-Delete UX

| Option | Description | Selected |
| ------ | ----------- | -------- |
| Return to dashboard | Always land on dashboard after delete. Predictable. | ✓ |
| Auto-open next story | Immediately switch to next story. Faster but surprising. | |
| Hybrid (dashboard if last, auto-open otherwise) | Context-dependent behavior. More complex, less predictable. | |

**User's choice:** Always return to dashboard. If last story deleted, show empty state (Phase 03 D-12).

---

## Batch Delete Mode

| Option | Description | Selected |
| ------ | ----------- | -------- |
| Edit-style toggle | Toolbar "Edit" button activates batch mode. Checkboxes appear. Familiar iOS/Android pattern. | |
| Long-press / shift-click only | No visible toggle. Power-user friendly but undiscoverable. | |
| Individual checkboxes always visible | Checkboxes on every card at all times. Always accessible but noisy. | |
| All three combined | Card flip "Select Multiple" + long-press + shift-click. Checkboxes appear in batch mode only. | ✓ |

**User's choice:** All three entry points. Card flip back face has "Select Multiple" button, long-press activates batch mode, shift-click activates batch mode. In batch mode: checkboxes on cards, highlight on selected, "Delete Selected (N)" in toolbar, Escape to exit.

---

## Card Flip Options (Edit + Delete + Batch)

**Added during discussion:** Card flip back face expanded from just "Delete/Cancel" to three actions:
- **Delete** — destructive delete with confirmation
- **Select Multiple** — enters batch mode
- **Edit** — allows editing story title and premise inline on the card back face

| Aspect | Decision |
| ------ | -------- |
| Edit fields | Title (single-line, pre-filled) + Premise (multi-line, pre-filled) on card back face |
| Save mechanism | Existing update endpoint (or new one if needed) |
| Layout | Stacked fields with Save/Cancel buttons, maintaining card dimensions |

**User's notes:** Edit was suggested as a natural extension of the card flip — since the back face is already revealed, it makes sense to offer editing alongside deletion.

---

## the agent's Discretion

- Card flip animation timing and easing
- Checkbox positioning and styling
- Batch mode toolbar button styling
- Whether batch delete uses N individual API calls or a single batch endpoint
- Whether story title/premise update needs a new backend endpoint or if one already exists
- Edit form layout on card back face (field arrangement)
- Highlight/border accent color for selected cards in batch mode

## Deferred Ideas

- Story export before delete (safety net) — future phase
- Undo delete with a grace period — future phase
