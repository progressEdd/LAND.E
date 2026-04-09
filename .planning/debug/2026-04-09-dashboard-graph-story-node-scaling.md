---
created: "2026-04-09T22:44:22.183Z"
issue: Story node premise/title truncated in DashboardGraph — nodes should scale to fit text
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
---

## Root Cause

Story nodes used fixed SVG `<rect>` (100×36px) with `<text>` truncated at 14 characters. SVG rectangles cannot auto-size to content, so longer titles were always cut off.

## Fix

Replaced SVG `<rect>` + `<text>` with `<foreignObject>` embedding an HTML `<div>`. HTML naturally auto-sizes to content. The story node card now shows up to 22 characters with word-break for overflow.

Additional adjustments:
- Widened viewBox from 600×400 to 800×400 for larger nodes
- Increased force simulation collision radius from 40 to 60
- Increased link distance from 80 to 100
- Increased charge strength from -200 to -250
- Full title available via HTML `title` attribute (native browser tooltip on hover)

**File modified:** `02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte`

## Verification

1. Story nodes in the graph show full titles (up to 22 chars)
2. Nodes have proper spacing (no overlapping)
3. Hover shows browser tooltip with full title
4. Click still navigates to story editor
5. Pan/zoom still works
