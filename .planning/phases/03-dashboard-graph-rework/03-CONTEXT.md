# Phase 03: Dashboard + Graph Rework - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Two deliverables: (1) Replace the welcome placeholder with a story dashboard home page featuring story cards, inline story creation, and a story-level graph showing stories as nodes connected to shared characters. (2) Rework the in-story node graph to draw character-to-paragraph edges with color-coded straight lines on hover.

Cross-story character identity and shared-universe features are Phase 02 — not in scope. This phase renders what already exists in the `character_mentions` table.

</domain>

<decisions>
## Implementation Decisions

### Dashboard Layout
- **D-01:** Hybrid layout — carousel-style featured/active story at top + grid of all stories below. Everything visible, not hidden behind tabs.
- **D-02:** Rich cards — title, premise preview (2-3 lines), character count, last edited, character names.
- **D-03:** Inline form for new story (card expands in-place with title + premise fields), plus "I'm Feeling Lucky" button alongside it.
- **D-04:** Dashboard replaces the welcome state entirely. Two distinct views: dashboard (no story open) → editor (story selected). "Back" or home icon returns to dashboard.

### Character-to-Paragraph Edges (In-Story Graph)
- **D-05:** Character→paragraph edges are straight lines, color-coded per character. Each character gets a distinct color for easy tracing.
- **D-06:** Edges appear on hover over a character supernode. Clean by default, details on demand.
- **D-07:** Character edges and tree edges coexist, layered together. Different styling to distinguish them (agent decides exact visual treatment — e.g., dashed vs solid, opacity levels).

### Navigation
- **D-08:** Click story card → instant switch to editor. No animation delay.
- **D-09:** Home icon + breadcrumb ("Home > Story Title") in toolbar to return to dashboard. Both mechanisms available.

### Graph Views (Dashboard vs Editor)
- **D-10:** Dashboard shows a story-level graph — each story as a node, character nodes connected to stories they appear in. High-level overview map. Editor shows the paragraph-level tree for the active story (current behavior, extended with character→paragraph edges from D-05).

### Empty State
- **D-11:** Empty state: centered "Create Your First Story" button + "I'm Feeling Lucky" button. Action-oriented.
- **D-12:** Empty state returns if all stories are deleted. Same create + lucky buttons.
- **D-13:** No graph shown in empty state. Graph area hidden until at least one story exists.

### the agent's Discretion
- Character color palette for edges (pick a distinct set that works in both dark and light themes)
- Exact card dimensions, spacing, and grid breakpoints
- Tree edge vs character edge visual distinction (dashed, opacity, stroke width)
- Breadcrumb placement and styling details
- Dashboard graph layout algorithm (force-directed, radial, etc.)
- Transition timing for inline form expand/collapse

</decisions>

<specifics>
## Specific Ideas

- Dashboard graph is the "zoomed out" view — stories as big nodes, characters as smaller nodes connected to the stories they appear in. Editor graph is the "zoomed in" view — paragraph tree with character edges.
- "I'm Feeling Lucky" should work from both the dashboard empty state and the inline create form — same random premise pool that already exists in the backend.
- Story cards should feel scannable — title prominent, premise gives context, character names hint at the cast.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Graph Implementation
- `02-worktrees/webapp-ui/frontend/src/lib/components/NodeGraph.svelte` — Current SVG tree visualizer (824 lines). Character supernodes, d3-hierarchy layout, seed nodes, tooltips, zoom/pan. Must be extended, not replaced.
- `02-worktrees/webapp-ui/frontend/src/lib/stores/graph.svelte.ts` — Graph state store.
- `02-worktrees/webapp-ui/backend/app/routers/stories.py` — `get_story_tree()` endpoint returns `TreeResponse` with `characters: list[CharacterSummary]` containing `node_ids` per character.

### Existing Dashboard / Welcome State
- `02-worktrees/webapp-ui/frontend/src/routes/+page.svelte` — Current welcome state (105 lines). Has `hasStory` conditional that shows welcome or editor. This is what gets replaced.
- `02-worktrees/webapp-ui/frontend/src/routes/+layout.svelte` — App shell (193 lines). Split panes, sidebars, theme toggle.
- `02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte` — Currently handles story creation and deletion (518 lines). Dashboard will take over story creation UX.

### Story Management
- `02-worktrees/webapp-ui/frontend/src/lib/stores/story.svelte.ts` — Story store with `loadStories()`, `setActiveStory()`, `loadedStories` cache, `createStory()`.
- `02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts` — WebSocket state, handles "I'm Feeling Lucky" flow.
- `02-worktrees/webapp-ui/backend/app/routers/stories.py` — `random_premise` endpoint and `create_story` endpoint.

### Data Model (character→paragraph linkage)
- `02-worktrees/webapp-ui/backend/app/models/database.py` — `character_mentions` table schema (node_id, character_name, role).
- `02-worktrees/webapp-ui/backend/app/models/schemas.py` — `CharacterSummary` (name, node_ids), `CharacterMentionResponse`, `TreeResponse`, `StoryResponse`.
- `02-worktrees/webapp-ui/backend/app/db/migrations/002_graph_support.sql` — character_mentions and node_analyses tables.

### Planning Context
- `.planning/codebase/ARCHITECTURE.md` — Full architecture docs updated 2026-04-09.
- `.planning/codebase/STRUCTURE.md` — Directory structure and file locations.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `NodeGraph.svelte`: All the SVG rendering, d3-hierarchy layout, zoom/pan, and node interaction code. Dashboard graph can fork or share this pattern.
- `story.svelte.ts` store: Already has `loadStories()`, `setActiveStory()`, story list state. Dashboard consumes this data.
- `random_premise` endpoint: Backend already returns random premises. "I'm Feeling Lucky" on dashboard calls the same endpoint.
- `CharacterSummary` with `node_ids`: Backend already aggregates which paragraph nodes each character appears in. The data for character→paragraph edges is already served by the tree endpoint.

### Established Patterns
- Svelte 5 runes class pattern for stores (singletons exported as `const`)
- CSS custom properties for theming (`--panel-bg`, `--text-primary`, etc.)
- `svelte-splitpanes` for resizable layout
- Tiptap custom marks with inline style attributes
- `fetchJSON` wrapper in `rest.ts` for API calls

### Integration Points
- `+page.svelte` is where dashboard vs editor conditional lives — this is the primary file to restructure
- `+layout.svelte` controls the shell (sidebars, splitpanes) — dashboard may need a different shell layout (full-width, no sidebars)
- `SettingsPanel.svelte` currently owns story creation — dashboard takes this over, SettingsPanel keeps LLM config
- `EditorToolbar.svelte` needs home icon + breadcrumb added
- `story.svelte.ts` needs a `clearActiveStory()` or `goHome()` method to return to dashboard
- Backend may need a new endpoint for story-level graph data (stories + shared characters across stories) if the existing list endpoint doesn't provide enough

</code_context>

<deferred>
## Deferred Ideas

- Cross-story character identity (linking "Jane" in Story A to "Jane" in Story B as the same character) — Phase 02
- Force-directed graph with shared universe visualization — Phase 02
- Story import from markdown — future phase
- Story templates / story series grouping — future phase

</deferred>

---

*Phase: 03-dashboard-graph-rework*
*Context gathered: 2026-04-09*
