---
created: "2026-04-09T22:40:35.292Z"
issue: Clicking story nodes in DashboardGraph still doesn't navigate after previous didDrag fix
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
---

## Root Cause

The previous fix added `didDrag` tracking but kept `setPointerCapture(e.pointerId)` in `handlePointerDown`, firing it on EVERY left click. `setPointerCapture` redirects all subsequent pointer events (including `click`) to the capturing element (the viewport div), which suppresses the `onclick` handler on child SVG `<g>` nodes. The `didDrag` flag in `handleNodeClick` was never reached because the `click` event never fired on the `<g>` element.

## Fix

Deferred `setPointerCapture` from `handlePointerDown` to `handlePointerMove` — it now only captures the pointer after the user has dragged >3px (confirming intent to pan). For simple clicks (<3px movement), pointer capture is never acquired, so `click` events propagate normally to SVG child nodes.

**File modified:** `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte`

## Verification

1. Click a story node in Story Universe graph → switches to editor view
2. Click+drag to pan → graph moves, no navigation
3. Zoom controls still work
4. Character node hover still works
