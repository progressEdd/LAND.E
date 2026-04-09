---
created: "2026-04-09T22:53:00.000Z"
issue: Story Universe graph too small — wastes whitespace on dashboard
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
---

## Root Cause

Graph viewport had no explicit height, and the SVG inside was fixed at `height: 300px`. With a 1200px-wide dashboard area, the graph appeared tiny with massive whitespace below.

## Fix

- Set `.graph-viewport` to `height: 500px` (from implicit ~300px)
- Changed `.graph-svg` from `height: 300px` to `height: 100%; min-height: 400px` so it fills the viewport

**File modified:** `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte`

## Verification

1. Dashboard shows Story Universe graph taking up significantly more vertical space
2. Graph still zooms/pans correctly
3. No layout overflow
