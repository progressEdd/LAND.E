---
created: "2026-04-09T22:35:01.719Z"
issue: 5 dashboard UI issues — hover clip, missing tooltips, broken click navigation, character focus request, story label truncation
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
deferred: character-focus-highlight
---

## Issues

1. Character hover text still cut off after previous fix
2. No descriptive tooltips on "New Story" / "I'm Feeling Lucky" buttons
3. Clicking story nodes in DashboardGraph doesn't navigate to story
4. Future feature request: clicking character highlights connected stories
5. Story premise/title truncated too aggressively in graph node view

## Root Cause

1. **Hover text clipped**: SVG viewBox was 600×300. Character nodes near the bottom have `y + 30` hover labels exceeding the 300px boundary.

2. **Missing tooltips**: Buttons had no `title` attributes at all.

3. **Click navigation broken** (regression from previous fix): The `handlePointerDown` added in the pan/zoom fix captured ALL left clicks (`e.button === 0`) for panning and called `e.preventDefault()`. This prevented `onclick` handlers on `<g>` nodes from ever firing. No click-vs-drag distinction existed.

4. **Character focus**: Future feature — noted for Phase 02 (Cross-Story Graph) planning.

5. **Story label truncation**: Story rect was only 80px wide, label truncated to 12 chars. Too aggressive for story titles.

## Fix

**Files modified:**
- `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte`
- `02-worktrees/webapp-ui/frontend/src/lib/components/Dashboard.svelte`

**DashboardGraph changes:**
- Added `didDrag` state to distinguish clicks from drags (>3px threshold)
- Removed `e.preventDefault()` from pointer down — only suppress click if drag occurred
- Moved `handleNodeClick` to check `didDrag` flag before navigating
- Expanded SVG viewBox from `600×300` to `600×400` for hover label room
- Widened story rect from 80px to 100px, increased truncation to 14 chars
- Added full-title hover label for story nodes with names >14 chars

**Dashboard changes:**
- Added `title` attributes to all "New Story" buttons: "Start writing a new story with a title and premise"
- Added `title` attributes to all "I'm Feeling Lucky" buttons: "Generate a random story premise automatically"

## Deferred

- **Character focus/highlight**: Clicking a character node to grey out unrelated stories. This is a meaningful interaction feature that should be planned properly, possibly as part of Phase 02 (Cross-Story Graph) where character identity across stories is the core feature.

## Verification

1. Click a story node in the Story Universe graph → switches to editor view
2. Drag to pan → graph moves, no navigation occurs
3. Hover character node near bottom → full name visible, not clipped
4. Hover "+ New Story" button → tooltip appears with description
5. Hover "I'm Feeling Lucky" button → tooltip appears with description
6. Story nodes show up to 14 chars, full title on hover for longer names
