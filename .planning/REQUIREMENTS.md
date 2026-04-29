# Requirements: LAND.E v1.1 — UI Fixes & Story Management

**Defined:** 2026-04-28
**Core Value:** Fix broken connection indicator and add story deletion capability — polish and completeness for the existing webapp.

## v1.1 Requirements

### Story Deletion

- [x] **DELE-01**: User can delete a story from the dashboard via a trash icon button with a confirmation dialog
- [x] **DELE-02**: Deleting a story cascades to remove all related records (nodes, provenance_spans, character_mentions, node_analyses, character_aliases, character_story_appearances)

### Connection Fix

- [x] **CONN-01**: Clicking "I'm Feeling Lucky" does not cause the WebSocket connection indicator to show "disconnected"
- [x] **CONN-02**: WebSocket connection state remains accurate after any REST API call

## Future Requirements

(none identified)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Graph layout switcher (yfiles-style) | Current d3 layouts sufficient for needs |
| Automated test suite | Planned for future milestone |
| Error recovery for failed generations | Deferred |
| Story import from markdown | Deferred |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DELE-01 | Phase 04: Story Deletion | ✓ Verified |
| DELE-02 | Phase 04: Story Deletion | ✓ Verified |
| CONN-01 | Phase 05: Connection Fix | ✓ Verified |
| CONN-02 | Phase 05: Connection Fix | ✓ Verified |

**Coverage:**
- v1.1 requirements: 4 total
- Mapped to phases: 4 ✓
- Unmapped: 0

---
*Requirements defined: 2026-04-28*
