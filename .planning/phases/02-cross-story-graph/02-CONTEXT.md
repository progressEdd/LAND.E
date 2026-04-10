# Phase 02: Cross-Story Knowledge Graph - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Global character identity across stories, shared universe visualization, and cross-story character linking. The system will identify when characters appearing in different stories are the same character, visualize the shared universe on the existing dashboard graph, and maintain rich character profiles that span stories.

Creating new stories, in-story graph visualization, and dashboard layout are already built (Phase 01 + 03). This phase adds the cross-story layer on top.

</domain>

<decisions>
## Implementation Decisions

### Character Matching Strategy
- **D-01:** Hybrid approach — auto-suggest matches by normalized name, user confirms or splits.
- **D-02:** Character names in the database are LLM-generated descriptive strings like "Chloe Miller (teenage daughter)" — normalization logic needs to extract the base name for matching while preserving the full descriptive string as context.
- **D-03:** User can explicitly split an auto-matched pair ("these are actually different characters") and manually link characters the system didn't auto-match.

### Graph Visualization
- **D-04:** Enhance the existing `DashboardGraph.svelte` — no new dedicated view. Linking and splitting characters happens directly on the dashboard graph.
- **D-05:** Graph shows linked characters as unified nodes with visual indication of cross-story presence. Unlinked characters remain per-story.

### Universe / Grouping Model
- **D-06:** No explicit "universe" or "series" table. Stories cluster visually on the graph based on shared characters. If two groups of stories share no characters, they naturally sit apart as separate clusters.

### Character Profile Depth
- **D-07:** Rich character sheet — a global character record that accumulates data across stories: canonical name, description, traits, arc summary, and per-story appearances with the role/context as it appears in each story.
- **D-08:** Character profile grows with each story — not just static metadata but a living "character bible" that the user can view and edit.

### the agent's Discretion
- Name normalization algorithm (how to extract "Chloe Miller" from "Chloe Miller (teenage daughter)")
- Exact UI for confirm/split actions on the graph (click, drag, context menu, panel)
- Character sheet layout and presentation details
- How auto-suggestions are presented (inline badges, side panel, notification)
- Color-coding or visual treatment for linked vs unlinked character nodes
- Whether the character sheet is editable by the user or auto-populated only

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Graph Implementation
- `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte` — Current d3-force dashboard graph (512 lines). Story + character nodes, color palette, hover states, force layout. This is the primary file to extend.
- `02-worktrees/webapp-ui/frontend/src/lib/components/Dashboard.svelte` — Dashboard page container (359 lines). Renders story cards and DashboardGraph.
- `02-worktrees/webapp-ui/frontend/src/lib/components/NodeGraph.svelte` — In-story SVG tree visualizer (881 lines). NOT the target for this phase, but reference for graph patterns.

### Data Model (character data already collected)
- `02-worktrees/webapp-ui/backend/app/models/database.py` — `character_mentions` table: `id`, `node_id`, `character_name`, `role`, `created_at`. Note: `role` is currently NULL; descriptive info is baked into `character_name` by the LLM.
- `02-worktrees/webapp-ui/backend/app/models/schemas.py` — `CharacterSummary` (name, node_ids), `StoryOverviewCharacter` (name, story_ids), `StoryOverviewResponse` (stories + characters).
- `02-worktrees/webapp-ui/backend/app/db/migrations/002_graph_support.sql` — character_mentions and node_analyses tables.

### Story Data
- `02-worktrees/webapp-ui/backend/app/db/migrations/001_initial.sql` — Stories, nodes, provenance_spans tables.
- `02-worktrees/webapp-ui/backend/app/routers/stories.py` — `stories_overview()` endpoint (line 205): already aggregates character→story mappings by name. Returns `StoryOverviewResponse` with stories and characters.
- `02-worktrees/webapp-ui/backend/app/services/story.py` — Generation pipeline, character extraction from LLM analysis.

### Frontend State
- `02-worktrees/webapp-ui/frontend/src/lib/stores/story.svelte.ts` — Story store with `loadStories()`, `setActiveStory()`, `createStory()`.
- `02-worktrees/webapp-ui/frontend/src/lib/types/index.ts` — TypeScript interfaces matching backend schemas, including `StoryOverviewCharacter`, `StoryOverviewResponse`.

### Planning Context
- `.planning/codebase/ARCHITECTURE.md` — Full architecture docs.
- `.planning/codebase/STRUCTURE.md` — Directory structure and file locations.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DashboardGraph.svelte`: Full d3-force implementation with story/character nodes, link rendering, color palette, hover states. This is the file being extended — not replaced.
- `stories_overview()` endpoint: Already returns `StoryOverviewCharacter` with `story_ids` per character name. The cross-story aggregation by name already works at the data level.
- `StoryOverviewResponse` types: Backend and frontend types already support characters with multiple story associations.

### Established Patterns
- Character names are LLM-generated descriptive strings — not clean proper nouns (e.g., "The Weathervane (an inanimate object with unusual agency)")
- `role` field in `character_mentions` is unused (NULL) — role info is embedded in the name string
- d3-force with synchronous 120 ticks for static layout (no animation)
- Svelte 5 runes class pattern for stores
- CSS custom properties for theming
- `fetchJSON` wrapper for API calls

### Integration Points
- `DashboardGraph.svelte` — primary file to extend with linking UI and linked character rendering
- `Dashboard.svelte` — may need character detail panel or sheet overlay
- `stories_overview()` endpoint — needs to return richer data for linked characters (or new endpoints needed)
- Database needs new tables/migrations for global character records (canonical character identity, character sheets)
- `character_mentions` table data stays per-story; new layer maps local mentions to global characters

</code_context>

<specifics>
## Specific Ideas

- Auto-clustering should feel organic — stories that share characters naturally group together on the force graph, separate story worlds drift apart. No explicit "universe" management.
- Character matching should surface suggestions proactively but let the user have the final say. The system should be helpful, not presumptuous.
- Rich character profiles are essentially a "character bible" — something a writer would actually want to reference when continuing a series or returning to a shared world.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-cross-story-graph*
*Context gathered: 2026-04-10*
