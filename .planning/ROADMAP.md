# Roadmap: LAND.E

## Overview

**v1.0 (Complete):** Project infrastructure — git worktree template, branch creation workflow, root README index, and the full webapp UI (FastAPI + SvelteKit SPA with Tiptap editor, provenance tracking, WebSocket streaming, node graph, SQLite persistence).

**v1.1 (Current):** UI polish — delete story button with cascade cleanup, fix premise generation breaking WebSocket connection status.

## Phases

**Phase Numbering:**
- Phases 00-03: v1.0 (complete)
- Phases 04+: v1.1 (current milestone)

- [x] **Phase 00: Infrastructure** - Template prep, branch creation, root README index
- [x] **Phase 01: Webapp UI** - Purpose-built story writer webapp replacing the marimo notebook
- [x] **Phase 02: Cross-Story Knowledge Graph** - Shared characters across stories, force-directed graph visualization
- [x] **Phase 03: Dashboard + Graph Rework** - Story dashboard home page, in-story character-to-paragraph graph edges
- [x] **Phase 04: Story Deletion** - Delete story from dashboard with cascade cleanup
- [ ] **Phase 05: Connection Fix** - Fix premise generation breaking WebSocket connection indicator

## Phase Details

### Phase 04: Story Deletion
**Goal**: Users can delete stories from the dashboard with full cascade cleanup
**Status**: Ready
**Folder**: `.planning/phases/04-story-deletion/`
**Depends on**: Phase 01 (Webapp UI), Phase 03 (Dashboard)
**Branch**: `webapp-ui` (existing)
**Worktree**: `02-worktrees/webapp-ui/`
**Requirements**: DELE-01, DELE-02
**Success Criteria**:
  1. Trash icon appears on story cards in the dashboard
  2. Clicking trash shows a confirmation dialog before deleting
  3. DELETE `/api/stories/{story_id}` removes the story and all cascade-related records (nodes → spans/mentions/analyses, aliases, appearances)
  4. After deletion, the story list refreshes and the deleted story is gone
**Plans:** 1 plan

### Phase 05: Connection Fix
**Goal**: "I'm Feeling Lucky" no longer breaks the WebSocket connection indicator
**Status**: Ready
**Folder**: `.planning/phases/05-connection-fix/`
**Depends on**: Phase 01 (Webapp UI)
**Branch**: `webapp-ui` (existing)
**Worktree**: `02-worktrees/webapp-ui/`
**Requirements**: CONN-01, CONN-02
**Success Criteria**:
  1. Clicking "I'm Feeling Lucky" keeps the connection indicator green/connected
  2. WebSocket connection state remains accurate after any REST API call
  3. The fix does not introduce new disconnection scenarios
**Plans:** 1 plan

## Progress

| Phase | Folder | Plans Complete | Status | Completed |
|-------|--------|----------------|--------|-----------|
| 00. Infrastructure | `00-infrastructure` | 1+ | Complete | 2026-02-13 |
| 01. Webapp UI | `01-webapp-ui` | 16/16 | Complete | 2026-02-14 |
| 02. Cross-Story Graph | `02-cross-story-graph` | 6/6 | Complete | 2026-04-10 |
| 03. Dashboard + Graph Rework | `03-dashboard-graph-rework` | 6/6 | Complete | 2026-04-09 |
| 04. Story Deletion | `04-story-deletion` | 1/1 | Complete | 2026-04-29 |
| 05. Connection Fix | `05-connection-fix` | 0/1 | Ready | — |
