# Plan 02-12 Summary: Graph Hover Tooltips and Zoom/Pan Navigation

## What Was Done

Added custom hover tooltips and zoom/pan navigation to the node graph visualizer, making it interactive and navigable for large story trees.

![Graph before enhancements](../../../00-supporting-files/images/02-CONTEXT/20260214012112.png)

### Changes

**NodeGraph.svelte — Hover Tooltips:**
- Replaced native SVG `<title>` elements with custom HTML tooltip divs positioned at the cursor
- Paragraph node tooltips show: title ("Paragraph N"), content preview (up to 200 chars), and list of character names mentioned
- Character supernode tooltips show: colored dot + full character name, and paragraph appearance count
- Tooltips appear instantly on `mouseenter`, disappear on `mouseleave`
- Styled with dark background, border, shadow, 280px max width, pre-wrap for content text

**NodeGraph.svelte — Zoom/Pan:**
- Replaced scroll-based overflow container with an SVG transform group (`<g transform="translate(...) scale(...)">`)
- Mouse wheel zooms 0.3x to 3x, anchored to cursor position (point under cursor stays fixed)
- Left-click drag on empty viewport area pans the graph; middle mouse button also pans
- Viewport cursor changes to `grab` (idle) / `grabbing` (dragging)
- Zoom controls in bottom-right corner: + / - buttons, 1:1 reset button, percentage readout
- Zoom/pan resets automatically when tree data changes (new story loaded)

### Commits

- **webapp-ui branch:** `db0bcef` — feat(02-12): add hover tooltips and zoom/pan to node graph

### Decisions

- Custom HTML tooltips over SVG foreignObject — HTML divs positioned absolutely in the viewport container are simpler to style and don't have SVG text wrapping limitations
- Cursor-anchored zoom — zooming keeps the point under the cursor fixed, matching the behavior of design tools (Figma, etc.)
- Left-click pan on empty area only (not on nodes) — prevents conflict with click-to-switch-branch interaction on paragraph nodes
- Transform group approach instead of viewBox manipulation — simpler state management, avoids viewBox recalculation on every zoom/pan

### Next Steps

- Keyboard shortcuts for zoom (Ctrl+/Ctrl-)
- Minimap for navigation in very large trees
- Double-click a paragraph node to scroll the editor to that paragraph's content
