---
created: "2026-04-09T22:13:04.127Z"
issue: Character nodes in Dashboard Graph don't show full name on hover
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
---

## Root Cause

DashboardGraph character nodes only render the initial letter inside the circle. No hover state exists to display the full character name. Compare with NodeGraph.svelte which already has tooltip-based name display via `showCharTooltip()`. The `hoveredNode` state was used for visual highlighting only — no text label was wired to it.

## Fix

Added a conditional `{#if hoveredNode === n.id}` SVG `<text>` element below the character circle in `DashboardGraph.svelte`. Renders the full character name when hovered. Name is truncated to 14 characters with ellipsis for long names.

**File modified:** `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte`
- Added hover name label (SVG `<text>`) positioned at `y + 30` below the circle
- Added `.char-hover-name` CSS class with theme-aware color and pointer-events: none

## Verification

1. Open the app → dashboard shows story universe graph
2. Hover over a character circle → full name appears below the circle
3. Move mouse away → name disappears, only initial remains
4. Long names are truncated with `…`
