---
created: "2026-04-11T04:30:00Z"
issue: Character nodes overlap premise/story boxes in DashboardGraph
type: logic_error
phase: completed (all phases done)
status: resolved
---

## Screenshot

![](../../00-supporting-files/images/2026-04-11-dashboard-graph-char-overlap/20260411043000.png)

See: `2026-04-11-dashboard-graph-char-overlap/20260411043000.png` — character circles sitting on top of story/premise cards

## Root Cause

The `forceCollide` radii in the d3-force simulation were far too small relative to the actual rendered node sizes:

1. **Story nodes** are rendered as 180×80 `foreignObject` elements (diagonal ≈99px), but `forceCollide` radius was only `50` — barely half the diagonal, so character circles could overlap the card
2. **Linked character nodes** have outer ring `r=34` but collision radius was only `30` — the ring itself extended past the collision boundary
3. **Canonical character link distance** was hardcoded at `50`, forcefully pulling character nodes right on top of the story boxes regardless of collision

## Fix

Changes in `DashboardGraph.svelte` only:

1. **`forceCollide` radii increased**: story `50→95`, linked_character `30→40`, unlinked_character `22→28`
2. **`forceCollide` strength** set to `0.9` for stronger separation enforcement
3. **Canonical character link distance**: from hardcoded `50` to `baseLinkDistance * 0.8` (scales with graph size: 80 for small, 96 for large)
4. **Cluster distances unchanged**: `baseLinkDistance`, `chargeStrength`, `forceCenter` all kept the same

## Files Modified

- `frontend/src/lib/components/DashboardGraph.svelte` — collision radii, collision strength, canonical link distance

## Verification

1. Reload the Dashboard — character circles should be clearly separated from story/premise cards
2. Zoom and pan should work as before
3. Cluster-to-cluster distances should be the same as before
