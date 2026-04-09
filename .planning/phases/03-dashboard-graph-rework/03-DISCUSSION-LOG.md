# Phase 03: Dashboard + Graph Rework - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-09
**Phase:** 03-dashboard-graph-rework
**Areas discussed:** Dashboard Layout, Character-to-Paragraph Edges, Navigation, Graph Views, Empty State

---

## Dashboard Layout

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Grid of cards | 2-3 columns, title + premise + date + node count. Like Notion/Linear. | |
| Single column list | One story per row, compact. Like Google Docs home. | |
| Card carousel | Featured story large at top, recent below. Emphasizes "continue writing". | ✓ (hybrid with grid) |

**User's choice:** Hybrid — carousel-style featured/active story at top + grid of all stories below.

### Card content

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Minimal | Title + date + node count only | |
| Rich | Title + premise preview + character count + last edited + character names | ✓ |
| You decide | Agent picks what fits | |

**User's choice:** Rich cards.

### Story creation flow

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Inline form | Card expands in-place with title + premise fields | ✓ |
| Modal dialog | Overlay modal with form | |
| Feeling Lucky default | Immediately generates random premise and opens editor | |

**User's choice:** Inline form + "I'm Feeling Lucky" button alongside.

### Dashboard location

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Replaces welcome state | Dashboard IS the home page, editor is separate view | ✓ |
| Always-visible tab | Dashboard as sidebar tab alongside editor | |
| Left sidebar takeover | Story list moves into dedicated panel | |

**User's choice:** Replaces welcome state. Two distinct views.

---

## Character-to-Paragraph Edges

### Edge rendering

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Curved bezier lines | Arc from character to paragraphs. Elegant. | |
| Straight lines + color coding | Each character gets distinct color. Easy to trace. | ✓ |
| Highlighted node borders | Click character → bold borders on their paragraphs. Less noise. | |

**User's choice:** Straight lines with color coding per character.

### Clutter handling

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Show all edges always | Full picture, can get dense. | |
| Hover to reveal | Edges appear on hover over character supernode. | ✓ |
| Toggle per character | Click to toggle edges on/off per character. | |

**User's choice:** Hover to reveal.

### Coexistence with tree edges

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Layered together | Both visible, different styling (dashed vs solid) | ✓ |
| Separate mode | Toggle between tree view and character map view | |
| You decide | Agent picks what's readable | |

**User's choice:** Layered together with different styling.

---

## Navigation

### Story card click

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Instant switch | Click → dashboard out, editor in. Fast. | ✓ |
| Slide transition | Animated slide between views. | |
| You decide | Whatever feels natural. | |

**User's choice:** Instant switch.

### Return to dashboard

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Home icon in toolbar | House button returns to dashboard. | |
| Breadcrumb | "Home > Story Title" at top. | |
| Both | Home icon + breadcrumb. Multiple ways back. | ✓ |

**User's choice:** Both home icon and breadcrumb.

### Graph across views

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Graph only in editor | Current behavior. Dashboard has no graph. | |
| Mini graph on dashboard | Small preview graph for featured story. | |
| Reverse: dashboard = all nodes, editor = story nodes | Dashboard shows story-level graph (stories + shared characters), editor shows paragraph tree. | ✓ |

**User's choice:** Reversed — dashboard shows story-level graph (stories as nodes, characters connected to stories), editor shows paragraph-level tree. NOT showing all paragraph nodes on dashboard — that's Phase 02.

---

## Empty State

### No stories view

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| Big create + lucky | Centered buttons, action-oriented. | ✓ |
| Guided welcome | Welcome message + expanded inline form. | |
| You decide | Make it clear what to do. | |

**User's choice:** Big "Create Your First Story" + "I'm Feeling Lucky" buttons.

### Empty state recurrence

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| One-time only | Once a story exists, never seen again. | |
| Returns on delete-all | If all stories deleted, empty state comes back. | ✓ |

**User's choice:** Returns if all stories deleted. Same create + lucky buttons.

### Empty graph

| Option | Description | Selected |
| ---------- | ---------------------------------- | -------- |
| No graph | Graph area hidden until stories exist. | ✓ |
| Empty graph with hint | Visible but empty graph with placeholder text. | |

**User's choice:** No graph in empty state.

---

## the agent's Discretion

- Character color palette for edges (distinct colors in both themes)
- Card dimensions, spacing, grid breakpoints
- Tree edge vs character edge visual distinction (dashed/opacity/stroke width)
- Breadcrumb placement and styling
- Dashboard graph layout algorithm
- Inline form expand/collapse transition timing

## Deferred Ideas

- Cross-story character identity (same character across stories) — Phase 02
- Force-directed shared universe graph — Phase 02
- Story import from markdown — future phase
- Story templates / series grouping — future phase
