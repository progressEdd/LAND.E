---
created: 2026-04-10T23:16:54Z
title: Redesign graph visualizer with yfiles-style layout switcher
area: ui
files:
  - 02-worktrees/webapp-ui/frontend/src/lib/components/DashboardGraph.svelte
  - /home/bedhedd/Documents/development_projects/progressEdd_projects/glma/02-worktrees/linux_kernel/.venv/lib/python3.13/site-packages/yfiles_jupyter_graphs/widget.py
  - /home/bedhedd/Documents/development_projects/progressEdd_projects/glma/02-worktrees/linux_kernel/.venv/lib/python3.13/site-packages/yfiles_jupyter_graphs/layout/configurations.py
---

## Problem

The current `DashboardGraph.svelte` uses a hardcoded d3-force organic layout with manual zoom/pan. The user wants a more polished graph visualization similar to yfiles_jupyter_graphs' GraphWidget, which provides:

1. **Layout switcher toolbar** — buttons to switch between layout algorithms (organic, circular, hierarchic, tree, radial, orthogonal). The yfiles widget exposes methods like `organic_layout()`, `circular_layout()`, `hierarchic_layout()`, `tree_layout()`, `radial_layout()`, `orthogonal_layout()`.
2. **Node styling by type** — yfiles supports `node_styles` with `{color, shape}` per node type (e.g. rectangles for stories, ellipses for characters, different colors for linked vs unlinked). Current implementation uses circles for everything.
3. **Shapes** — yfiles supports: `'ellipse'`, `'hexagon'`, `'hexagon2'`, `'octagon'`, `'pill'`, `'rectangle'`, `'round-rectangle'`, `'triangle'`. Current graph only uses circles.

Current state: Single force-directed layout in SVG with zoom/pan controls (+ / - / 1:1 buttons). No way to switch views.

## Solution

Enhance `DashboardGraph.svelte`:

1. **Add layout toolbar** — row of icon buttons above the graph (or overlaid like current zoom controls):
   - 🌿 Organic (current d3-force, default)
   - ⭕ Circular — arrange nodes on a circle (stories on outer ring, characters on inner, or vice versa)
   - 📊 Hierarchic — stories as roots, characters branching down
   - 🌳 Tree — similar to hierarchic but strict tree layout
   - 🎯 Radial — stories at center, characters radiating outward

2. **Implement layouts using d3-force primitives** (no new deps):
   - Organic: current `forceSimulation` (already done)
   - Circular: compute angular positions, no simulation needed
   - Hierarchic: d3 tree or manual layering (stories = layer 0, characters = layer 1)
   - Radial: d3 cluster/radial or manual polar coordinates

3. **Add node shapes by type** (SVG):
   - Stories: `round-rectangle` (current `foreignObject` card, keep as-is)
   - Linked characters: filled circle with double-ring (current, keep)
   - Unlinked characters: `pill` shape or hexagon to visually distinguish from linked

4. **Smooth transitions** — animate node positions when switching layouts using Svelte transitions or manual tweening (interpolate from old positions to new positions over ~300ms)

### Reference: yfiles layout algorithms
From `/home/bedhedd/Documents/development_projects/progressEdd_projects/glma/02-worktrees/linux_kernel/.venv/lib/python3.13/site-packages/yfiles_jupyter_graphs/layout/configurations.py`:
- `OrganicLayoutConfiguration` — force-directed
- `CircularLayoutConfiguration` — circular arrangement
- `HierarchicLayoutConfiguration` — layered top-to-bottom
- `TreeLayoutConfiguration` — strict tree
- `RadialLayoutConfiguration` — radial outward from center
- `OrthogonalLayoutConfiguration` — grid-aligned edges
- `InteractiveOrganicLayoutConfiguration` — animated/interactive force

### Implementation notes
- d3-force already imported; can reuse `forceSimulation` for organic
- For non-force layouts, compute positions analytically then set directly
- Consider extracting layout logic into `frontend/src/lib/layouts/` for clean separation
- Current node data structure (`GraphNode` with `type`, `label`, `canonical_id`, `story_count`, `color`) is already sufficient for type-based styling
