---
created: 2026-04-28T20:28:18-05:00
title: Add delete story button
area: ui
files:
  - frontend/src/lib/components/Dashboard.svelte
  - frontend/src/lib/stores/story.svelte.ts
  - backend/routers/stories.py
---

## Problem

There is no way to delete a story from the UI. Currently the only way to remove stories is by manually running SQL against `backend/data/stories.db`. The database has cascade-related data in `nodes`, `provenance_spans`, `character_mentions`, `node_analyses`, `character_aliases`, and `character_story_appearances` tables that all need cleanup on delete.

## Solution

- Add a DELETE `/api/stories/{story_id}` endpoint in the backend router that removes the story and all related records (nodes → spans/mentions/analyses, aliases, appearances)
- Add a delete button (trash icon) to story cards in `Dashboard.svelte` with a confirmation dialog
- Add `deleteStory()` action to `story.svelte.ts` store
- Wire the frontend to call the delete endpoint and refresh the story list
