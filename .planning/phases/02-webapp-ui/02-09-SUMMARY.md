# Plan 02-09 Summary: Node Graph Backend

## What Was Done

Added backend data model and API support for the node graph visualizer feature, laying the foundation for the frontend graph component (02-10).

### Changes

**Migration 002 — `backend/app/db/migrations/002_graph_support.sql`:**
- `character_mentions` table: links character names to specific nodes with role field, UNIQUE(node_id, character_name)
- `node_analyses` table: persists full StoryAnalysis JSON per node, UNIQUE(node_id)
- Three indexes for efficient graph queries

**Database — `backend/app/models/database.py`:**
- Updated `init_db()` to auto-discover and run all migration files (`*.sql`) in sorted order, replacing the hardcoded `001_initial.sql` reference

**Pydantic Models — `backend/app/models/schemas.py`:**
- Added `CharacterMentionResponse`, `CharacterSummary`, `TreeNodeResponse` (recursive), `TreeResponse`, `SwitchPathRequest`
- Extended `NodeResponse` with optional `character_mentions` and `analysis` fields

**Character Extraction — `backend/app/services/story.py`:**
- Added `extract_characters(cast)` that parses StoryAnalysis.cast entries ("Name — role") into deduplicated (name, role) tuples
- Handles em dash, regular dash, and entries without dash

**Generation Pipeline — `backend/app/routers/ws.py`:**
- After streaming completes, persists analysis JSON to `node_analyses` table
- Extracts characters from analysis.cast and inserts into `character_mentions`
- Both cascade-delete on reject, persist on accept

**Story API — `backend/app/routers/stories.py`:**
- `GET /api/stories/{id}` now includes character_mentions and analysis per node
- `GET /api/stories/{id}/tree` — new endpoint returning recursive tree structure with character supernodes
- `PATCH /api/stories/{id}/active-path` — new endpoint for branch switching (walks up tree from target to root)

**Frontend Types — `frontend/src/lib/types/index.ts`:**
- Added `CharacterMention`, `CharacterSummary`, `TreeNode`, `TreeResponse`, `SwitchPathRequest`
- Extended `StoryNode` with `character_mentions` and `analysis` fields

**REST Client — `frontend/src/lib/api/rest.ts`:**
- Added `getStoryTree(storyId)` and `switchActivePath(storyId, targetNodeId)` methods

### Commits

- **webapp-ui branch:** `8dc182a` — feat(02-09): add graph backend

### Decisions

- Used `INSERT OR REPLACE` for node_analyses (one analysis per node, latest wins)
- Used `INSERT OR IGNORE` for character_mentions (idempotent per node+character pair)
- Character extraction handles both em dash (` — `) and regular dash (` - `) separators
- Migration runner updated to glob pattern (`*.sql`) for future-proofing
- Tree endpoint builds full recursive structure server-side rather than returning flat list for client-side construction
- Branch switching walks up via parent_id with cycle detection

### Next Steps

- **02-10:** Frontend graph visualizer — replace GraphPlaceholder.svelte with interactive graph, character supernodes, branch switching UX, active path highlighting
