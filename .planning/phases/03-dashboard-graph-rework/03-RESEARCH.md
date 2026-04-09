# Phase 03: Dashboard + Graph Rework - Research

**Researched:** 2026-04-09
**Status:** Complete

## Research Question

What do I need to know to PLAN this phase well?

---

## 1. Current Architecture (What Exists)

### Welcome State → Editor Toggle

The current app has a simple two-state system in `+page.svelte` (105 lines):

```svelte
{#if hasStory}
  <div class="editor-pane">...EditorToolbar, Editor, GenerationControls...</div>
{:else}
  <div class="welcome-state">...placeholder text...</div>
{/if}
```

`hasStory` is derived from `!!storyState.activeStoryId`. The `onMount` hook auto-selects the first story if one exists, meaning the welcome state is rarely seen.

**Key insight:** The dashboard needs to replace the `{:else}` branch entirely AND become the default view when no story is active. The user should land on the dashboard, not auto-select a story.

### Layout Shell

`+layout.svelte` (193 lines) renders a fixed structure:
- Left sidebar: `SettingsPanel` (LLM config + story management)
- Main content: `Splitpanes` with editor pane (60%) + `NodeGraph` pane (40%)
- Right sidebar: `AnalysisPanel`

**Key insight:** The dashboard view needs a DIFFERENT layout — full-width, no split panes, no sidebars. The dashboard graph (story-level) replaces the NodeGraph. Options:
1. Make `+layout.svelte` conditional — show simplified shell when on dashboard, full shell when editing
2. Move the split pane / sidebars into the editor-only view in `+page.svelte`
3. Use CSS to hide/show sections based on `activeStoryId`

Option 1 is cleanest — the layout already imports sidebars and splitpanes that are irrelevant to the dashboard.

### Story Store (`story.svelte.ts`)

Current state:
- `stories: Story[]` — summaries from `listStories()` (no nodes)
- `activeStoryId: string | null` — currently selected story
- `loadedStories: Record<string, Story>` — cache of fully loaded stories (with nodes)
- `createStory()` — creates and immediately sets as active
- `setActiveStory()` — loads full data if not cached
- `deleteStory()` — removes from list, auto-selects another or null

**Changes needed:**
- `createStory()` currently auto-selects the new story. For dashboard, it should create the story and keep the user on the dashboard (or auto-switch — D-08 says "instant switch to editor").
- Need a `clearActiveStory()` or `goHome()` method that sets `activeStoryId = null` and clears localStorage.
- `listStories()` already returns summary data (id, title, premise, created_at, updated_at). But it does NOT return character mentions or node counts — only the full story has that.

### NodeGraph Component (`NodeGraph.svelte`, 824 lines)

Current SVG layers (rendered in order):
1. Tree edges (paragraph → paragraph lines)
2. Seed edges (paragraph → seed dashed lines)
3. Paragraph nodes (circles with position numbers)
4. Character supernodes (colored circles with initials, positioned in a column to the right)
5. Seed nodes (dashed circles with numbers)

Layout algorithm:
- Uses `d3-hierarchy` → `d3tree()` for paragraph tree positions
- Characters positioned in a column at `treeRight + CHAR_COLUMN_X_OFFSET`
- Seeds positioned below their parent paragraph nodes
- Zoom/pan via transform on the root `<g>` element
- Tooltip on hover, seed click triggers generation

**Character data already available:**
- `TreeResponse.characters: CharacterSummary[]` — each has `name` and `node_ids`
- `node_ids` is the list of paragraph node IDs where the character is mentioned
- This is exactly the data needed for character→paragraph edges

**Key insight for character→paragraph edges:** The layout already computes paragraph positions in `paraMap`. Each character already has `nodeIds` from the API. Connecting them requires:
1. For each character, look up each `nodeId` in `paraMap` to get `(x, y)` coordinates
2. Draw lines from character supernode `(c.x, c.y)` to each paragraph `(p.x, p.y)`
3. Only show on hover (D-06)
4. Color-code by character color (already assigned via `getCharacterColor()`)
5. Different styling from tree edges (D-07)

### Backend API

**Existing endpoints:**
- `GET /api/stories` — Returns `[{id, title, premise, created_at, updated_at}]` — summaries only
- `GET /api/stories/{id}/tree` — Returns `TreeResponse` with `root`, `characters`, `active_path`
- `GET /api/stories/random-premise` — Returns `{"premise": "..."}`
- `POST /api/stories` — Creates story with root node

**For the dashboard story-level graph (D-10):** Need to know which characters appear in which stories. The current `GET /api/stories` only returns summaries. Options:
1. **New endpoint:** `GET /api/stories/graph` — Returns all stories with their characters aggregated
2. **Extend list endpoint:** Add optional `?include_characters=true` query param
3. **Client-side aggregation:** Load each story's tree individually and aggregate — too many requests

Option 1 is cleanest. A single endpoint that returns:
```json
{
  "stories": [
    {"id": "...", "title": "...", "premise": "...", "character_names": ["Alice", "Bob"]}
  ],
  "characters": [
    {"name": "Alice", "story_ids": ["story1", "story3"]},
    {"name": "Bob", "story_ids": ["story1", "story2"]}
  ]
}
```

This provides the bipartite graph data (stories ↔ characters) needed for the dashboard graph visualization.

---

## 2. Dashboard Design Analysis

### Card Data Requirements (D-02)

Rich cards need: title, premise preview, character count, last edited, character names.

**What the list endpoint already provides:** `id`, `title`, `premise`, `created_at`, `updated_at`
**What's missing:** character count, character names, node count

The new `/api/stories/graph` endpoint can include these. Alternatively, the story list endpoint can be extended with a summary fields. For node count, we'd need a `COUNT()` query.

### Layout Structure (D-01, D-03)

Hybrid layout with carousel-style featured area + grid:
- **Featured area:** Most recently edited story (or last active story) displayed prominently
- **Grid:** All stories below in a responsive grid (2-3 columns)
- **Create card:** An inline-create card that expands with title + premise fields + "I'm Feeling Lucky"

### Story Creation Flow (D-03)

Current creation flow:
1. User clicks "+ New Story" in `SettingsPanel`
2. Form expands inline in the sidebar
3. User fills title + premise, clicks "Create"
4. `storyState.createStory()` creates and auto-selects

Dashboard creation flow:
1. Empty-state card with "+" or "Create Story" button
2. Click expands to show title + premise fields
3. "I'm Feeling Lucky" fills random premise
4. "Create" creates the story (D-08: instant switch to editor) OR stays on dashboard

D-08 says "Click story card → instant switch to editor" and D-03 says inline form + lucky button. The create flow should:
- Show the inline form in the card
- On create: switch to editor with the new story active (same as current behavior)

### Empty State (D-11, D-12, D-13)

When `storyState.stories.length === 0`:
- Centered "Create Your First Story" button
- "I'm Feeling Lucky" button alongside
- No graph shown
- Same view returns if all stories are deleted

---

## 3. Character-to-Paragraph Edge Implementation

### Data Flow

The `TreeResponse.characters` array already contains:
```typescript
CharacterSummary { name: string, node_ids: string[] }
```

The layout already maps paragraphs by ID in `paraMap`. So the edge data is trivially computed:

```typescript
interface CharEdge {
  charName: string;
  charX: number; charY: number;
  paraX: number; paraY: number;
  paraId: string;
  color: string;
}
```

### Rendering Approach

Per D-05 (straight lines, color-coded) and D-06 (hover to reveal):

1. Add a new SVG layer between tree edges and paragraph nodes (or after character nodes)
2. Compute edges in the `layout` derived — iterate characters, look up each `nodeId` in `paraMap`
3. Track `hoveredCharacter: string | null` state
4. Show edges only when `hoveredCharacter === edge.charName`
5. Style: solid lines with the character's color, moderate opacity (0.4-0.6), stroke-width ~1.5

### Edge Positioning Considerations

Characters are positioned in a column to the RIGHT of the tree. Edges will cross the tree horizontally. With many paragraphs, this could get cluttered. Mitigations:
- D-06 already says hover-only, so only one character's edges are visible at a time
- Use lower opacity and thinner stroke than tree edges
- Consider drawing edges behind nodes (lower z-order) so nodes aren't obscured

### SVG Layer Ordering with Edges

Recommended layer order:
1. Tree edges (paragraph flow) — already exists
2. **Character→paragraph edges** — NEW, behind nodes
3. Seed edges — already exists
4. Paragraph nodes — already exists
5. Character supernodes — already exists
6. Seed nodes — already exists

This puts character edges behind all nodes so they don't obscure the tree structure.

---

## 4. Dashboard Story-Level Graph

### What It Shows (D-10)

- Stories as large nodes
- Characters as smaller nodes
- Edges connect characters to the stories they appear in
- This is a bipartite graph (stories ↔ characters)

### Implementation Options

**Option A: Fork NodeGraph pattern into new `DashboardGraph.svelte`**
- Reuse the SVG rendering approach (zoom, pan, tooltip)
- Different layout algorithm (not d3-tree — use force-directed or radial)
- Different data source (new endpoint)
- Pros: Clean separation, no risk of breaking existing graph
- Cons: Some code duplication (SVG boilerplate, zoom/pan)

**Option B: Extend NodeGraph with a `mode` prop**
- `mode="story-tree"` (current) vs `mode="story-overview"` (dashboard)
- Conditional rendering based on mode
- Pros: No duplication
- Cons: Component becomes massive (already 824 lines)

**Option C: Extract shared SVG primitives, two focused components**
- `GraphViewport.svelte` — zoom/pan container, SVG boilerplate
- `StoryTreeGraph.svelte` — current NodeGraph logic
- `DashboardGraph.svelte` — story-level graph using GraphViewport
- Pros: Clean, reusable
- Cons: More files, more refactoring

**Recommendation:** Option A is pragmatic for this phase. The dashboard graph is fundamentally different data and layout. Copy the SVG viewport pattern (zoom/pan/tooltip) but keep the layout and data logic separate. ~200-300 lines for DashboardGraph vs 824 for NodeGraph. If duplication becomes a concern in Phase 02 (cross-story graph), refactor to Option C then.

### Layout Algorithm for Dashboard Graph

The dashboard graph has stories and characters as nodes. For a small number of stories (likely 1-10), layout options:
- **Radial:** Stories in a circle, characters around them. Works for 2-8 stories.
- **Force-directed:** d3-force simulation. Good for any size, but needs d3-force dependency.
- **Manual grid:** Stories in a row, characters positioned between stories they connect to. Simple but rigid.

Force-directed (d3-force) is the standard choice for this kind of graph. It handles varying numbers of nodes gracefully and produces organic layouts. However, adding d3-force as a dependency needs consideration.

**Simpler alternative:** Since the existing code uses d3-hierarchy (already installed), check if d3-force is also available:
- `package.json` has `d3-hierarchy` — does it also have `d3-force`?

If not, a simple manual layout works for the likely small number of stories:
- Stories positioned in a horizontal row (evenly spaced)
- Characters positioned below/between stories they connect to
- Vertical spacing for readability

### Backend Data for Dashboard Graph

New endpoint needed: `GET /api/stories/overview`

Returns:
```python
class StoryOverviewStory(BaseModel):
    id: str
    title: str
    premise: str
    character_names: list[str]
    node_count: int

class StoryOverviewCharacter(BaseModel):
    name: str
    story_ids: list[str]

class StoryOverviewResponse(BaseModel):
    stories: list[StoryOverviewStory]
    characters: list[StoryOverviewCharacter]
```

SQL queries:
```sql
-- Stories with character names and node counts
SELECT s.id, s.title, s.premise,
       GROUP_CONCAT(DISTINCT cm.character_name) as character_names,
       COUNT(DISTINCT n.id) as node_count
FROM stories s
LEFT JOIN nodes n ON n.story_id = s.id
LEFT JOIN character_mentions cm ON cm.node_id IN (SELECT id FROM nodes WHERE story_id = s.id)
GROUP BY s.id
ORDER BY s.updated_at DESC;

-- Characters with story IDs
SELECT cm.character_name as name,
       GROUP_CONCAT(DISTINCT n.story_id) as story_ids
FROM character_mentions cm
JOIN nodes n ON cm.node_id = n.id
GROUP BY cm.character_name
ORDER BY cm.character_name;
```

---

## 5. Navigation Changes

### Home Icon in Toolbar (D-09)

`EditorToolbar.svelte` currently has formatting buttons only (Bold, Italic, etc.). Need to add:
- Home icon button (🏠 or SVG house icon) at the LEFT of the toolbar
- Clicking it calls `storyState.clearActiveStory()` (new method)
- This takes user back to dashboard

### Breadcrumb (D-09)

Add a breadcrumb bar above the editor:
- Dashboard view: no breadcrumb (or just "Home")
- Editor view: "Home > {Story Title}"
- "Home" is clickable → back to dashboard
- Story title is static text

The breadcrumb could be part of the top-bar in `+layout.svelte` or in a new component. Since the top-bar already has the app title, replacing it with a breadcrumb when a story is active makes sense:
- No story: "AI Story Writer" (current)
- Story active: "🏠 Home > {Story Title}"

### Dashboard → Editor Transition (D-08)

Instant switch — no animation delay. The current conditional rendering in `+page.svelte` already swaps instantly. The key change is:
1. Dashboard is the DEFAULT when no story is active
2. Remove auto-selection on mount (currently auto-selects first story)
3. Only select a story when user clicks a card

---

## 6. Layout Restructuring

### Current Structure

```
+layout.svelte (fixed shell)
├── Left Sidebar (SettingsPanel)
├── Main Content (Splitpanes)
│   ├── Editor Pane (+page.svelte content)
│   └── Graph Pane (NodeGraph)
└── Right Sidebar (AnalysisPanel)
```

### Needed Structure

```
+layout.svelte (conditional shell)
├── IF no active story (Dashboard):
│   ├── Top bar with app title + theme toggle
│   └── Dashboard (full-width)
│       ├── Featured story area
│       ├── Story grid + create card
│       └── Story-level graph (DashboardGraph)
└── IF active story (Editor):
    ├── Left Sidebar (SettingsPanel — LLM config only)
    ├── Main Content (Splitpanes)
    │   ├── Editor Pane (EditorToolbar with home icon, Editor, GenerationControls)
    │   └── Graph Pane (NodeGraph with character→paragraph edges)
    └── Right Sidebar (AnalysisPanel)
```

**Implementation approach:** The simplest way is to move the conditional into `+layout.svelte`. When `storyState.activeStoryId` is null, render the dashboard component full-width. When it's set, render the current split-pane layout.

Alternatively, keep `+layout.svelte` minimal (just the top bar and theme toggle) and put the conditional rendering in `+page.svelte`:
- No story: render `Dashboard.svelte`
- Story active: render the split-pane editor layout

This is cleaner because the layout doesn't need to know about dashboard vs editor. The page component handles it.

### SettingsPanel Changes

Currently, `SettingsPanel` has TWO sections:
1. **LLM Backend** config — stays in sidebar
2. **Stories** management (list + create + delete) — moves to dashboard

After this change:
- `SettingsPanel` only contains LLM config (backend, model, warmup)
- Story management is handled by the Dashboard component
- The left sidebar can be collapsed more aggressively since it only has LLM config

---

## 7. Dependency Analysis

### New NPM Dependencies

For the dashboard graph:
- `d3-force` — If we want force-directed layout. Check if already available as a transitive dep.
- Alternative: manual positioning for small graphs (no new dep)

For the dashboard UI:
- No new deps needed — Svelte + CSS custom properties are sufficient
- Grid layout via CSS Grid (no Tailwind classes needed)

### New Backend Dependencies

None. FastAPI + aiosqlite + Pydantic already handle everything.

### Files Modified

**Frontend (new):**
- `frontend/src/lib/components/Dashboard.svelte` — Dashboard home page
- `frontend/src/lib/components/DashboardGraph.svelte` — Story-level graph visualization
- `frontend/src/lib/components/StoryCard.svelte` — Individual story card component

**Frontend (modified):**
- `frontend/src/routes/+page.svelte` — Replace welcome state with dashboard
- `frontend/src/routes/+layout.svelte` — Conditional layout (dashboard vs editor)
- `frontend/src/lib/components/NodeGraph.svelte` — Add character→paragraph edge layer + hover state
- `frontend/src/lib/components/EditorToolbar.svelte` — Add home icon button
- `frontend/src/lib/components/SettingsPanel.svelte` — Remove story management section
- `frontend/src/lib/stores/story.svelte.ts` — Add `clearActiveStory()`, modify auto-selection behavior
- `frontend/src/lib/types/index.ts` — Add new type definitions (StoryOverview, etc.)

**Backend (modified):**
- `backend/app/routers/stories.py` — Add `GET /api/stories/overview` endpoint
- `backend/app/models/schemas.py` — Add `StoryOverview*` Pydantic models

**No database migrations needed** — all required data already exists in `character_mentions` and `nodes` tables.

---

## 8. Risk Assessment

### Low Risk
- Character→paragraph edges: Data is already served, rendering is straightforward SVG lines
- SettingsPanel refactor: Just removing the stories section
- Home icon / breadcrumb: Simple UI additions

### Medium Risk
- Layout restructuring: Changing `+layout.svelte` conditional logic could affect editor behavior. Test carefully.
- Dashboard graph: New visualization code, but self-contained and doesn't affect existing components
- Removing auto-story-selection on mount: Changes current user behavior. Make sure dashboard makes it obvious how to open a story.

### Edge Cases
- **No characters yet:** If a story has no character mentions (no generation has been run), the dashboard graph should still show story nodes without character connections
- **Many stories:** Grid should scroll; graph should handle 10+ stories without breaking
- **Story with only root node:** Newly created story has one node (the premise). Card should show "0 characters" and "1 paragraph"
- **Concurrent edits:** Dashboard should refresh story list after create/delete operations
- **Light theme:** All new components must use CSS custom properties for theming

---

## 9. Implementation Order Recommendation

Based on dependency analysis, recommended order:

1. **Backend: Stories overview endpoint** — `GET /api/stories/overview` with character aggregation
2. **Frontend: Story store updates** — `clearActiveStory()`, remove auto-selection
3. **Frontend: Dashboard component** — Cards, grid, empty state, create flow
4. **Frontend: Layout restructuring** — Conditional dashboard vs editor in `+page.svelte` / `+layout.svelte`
5. **Frontend: Navigation** — Home icon in toolbar, breadcrumb in top bar
6. **Frontend: SettingsPanel refactor** — Remove story management section
7. **Frontend: Character→paragraph edges** — Extend NodeGraph with hover edges
8. **Frontend: Dashboard graph** — Story-level graph component (if time permits in this phase)

This order ensures each step builds on the previous and can be tested independently.

---

## RESEARCH COMPLETE
