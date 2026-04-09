---
created: "2026-04-09T22:13:04.127Z"
issue: Character nodes in DashboardGraph don't show full name on hover
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
---

## Root Cause

The `DashboardGraph.svelte` character nodes only rendered the initial letter inside the circle permanently — no hover state existed to display the full character name. The in-story `NodeGraph.svelte` already had tooltip-based name display, but the dashboard graph component was built without it.

## Fix

Added a conditional `{#if hoveredNode === n.id}` text element below the character circle in `DashboardGraph.svelte` that renders the full character name when hovered. Name is truncated to 14 characters with ellipsis for long names.

**File modified:** `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte`
- Added hover name label (SVG `<text>`) positioned at `y + 30` below the circle
- Added `.char-hover-name` CSS class with theme-aware color and pointer-events: none

## Verification

1. Open the app → dashboard shows story universe graph
2. Hover over a character circle → full name appears below the circle
3. Move mouse away → name disappears, only initial remains
4. Long names are truncated with `…`
