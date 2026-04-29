---
phase: 04
slug: story-deletion
status: approved
shadcn_initialized: false
preset: none
created: 2026-04-28
---

# Phase 04 - UI Design Contract

> Visual and interaction contract for Story Deletion phase. Pre-populated from CONTEXT.md decisions and existing design tokens.

---

## Design System

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Tool              | none (SvelteKit — shadcn not applicable)            |
| Preset            | not applicable                                      |
| Component library | none (custom Svelte 5 components)                   |
| Icon library      | none — inline SVG for new icons (trash, edit, check)|
| Font              | system stack (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif) |

---

## Spacing Scale

Existing scale from project CSS. All values are multiples of 4.

| Token | Value | Usage                              |
| ----- | ----- | ---------------------------------- |
| xs    | 4px   | Icon gaps, inline padding, borders |
| sm    | 8px   | Compact element spacing, card gaps |
| md    | 16px  | Default element spacing, card padding |
| lg    | 24px  | Section padding, dashboard margins |
| xl    | 32px  | Layout gaps, dashboard outer padding |
| 2xl   | 48px  | Major section breaks               |
| 3xl   | 64px  | Page-level spacing                 |

Exceptions: none

---

## Typography

Constrained from existing 9 font sizes down to 4 for this phase's new elements:

| Role    | Size | Weight   | Line Height | Usage                                    |
| ------- | ---- | -------- | ----------- | ---------------------------------------- |
| Body    | 13px | 400      | 1.5         | Card premise, card-back body text        |
| Label   | 11px | 400      | 1.3         | Badges, metadata, date, node count       |
| Heading | 15px | 600      | 1.3         | Card title, card-back heading            |
| Display | 20px | 700      | 1.2         | Dashboard title                          |

Note: Existing components use sizes outside this scale (e.g. 14px toolbar, 9px graph labels). This contract covers **new Phase 04 elements only**. Existing components remain unchanged.

---

## Color

From existing CSS custom properties in `+layout.svelte`:

| Role            | Dark Value                      | Light Value                     | Usage                                              |
| --------------- | ------------------------------- | ------------------------------- | -------------------------------------------------- |
| Dominant (60%)  | `var(--panel-bg)` #030712       | #ffffff                         | Background, card-back face                          |
| Secondary (30%) | `var(--sidebar-bg)` #111827     | #f9fafb                         | Cards (front face), sidebar, toolbar bar            |
| Accent (10%)    | #6366f1 / #a5b4fc               | #4f46e5 / #6366f1               | Card hover border, primary CTA, selected highlight  |
| Destructive     | #ef4444                         | #dc2626                         | Delete button text/background, batch delete button  |

Accent reserved for: card hover border, primary CTA ("Create Story", "New Story"), selected card highlight border in batch mode, active nav item.

Destructive reserved for: "Delete" button on card-back face, "Delete Selected (N)" button in batch toolbar.

---

## Copywriting Contract

| Element                      | Copy                                                        |
| ---------------------------- | ----------------------------------------------------------- |
| Primary CTA (create)         | "Create Story" / "Create Your First Story"                  |
| Empty state heading          | "Welcome to LAND.E"                                         |
| Empty state body             | "Create your first story to get started."                   |
| Error state                  | "Failed to delete story. Please try again."                 |
| Destructive confirmation     | Story delete: Card flip — "Delete [title]?" with Delete/Cancel buttons |
| Batch delete confirmation    | "Delete Selected (N)" button in toolbar                     |
| Card-back actions            | "Delete" / "Edit" / "Select Multiple"                       |
| Edit save                    | "Save Changes" / "Cancel"                                   |
| Batch mode toolbar           | "Delete Selected (N)" / "Cancel Selection"                  |

---

## Visual Hierarchy

### Focal Point
**Story card grid** — the primary visual anchor. Cards draw the eye via title text and character badges.

### Card Flip Interaction

**Front face (default):**
1. Title (15px semibold) — primary visual anchor
2. Premise (13px, 3-line clamp) — secondary
3. Character badges + metadata (11px) — tertiary
4. Trash icon (top-right, hover only) — action layer

**Back face (flipped):**
1. "Delete [title]?" heading (15px semibold) — focal point
2. Three action buttons stacked vertically — action layer
3. Edit form (when active) replaces action buttons

### Batch Mode
1. Checkboxes appear on all cards (top-left, always visible)
2. Selected cards get accent border highlight (#6366f1, 2px)
3. Toolbar bar slides in above grid with "Delete Selected (N)" + "Cancel Selection"

---

## Component Inventory

### New Components
| Component | Type | Notes |
|-----------|------|-------|
| Card flip wrapper | CSS pattern | 3D transform, `perspective: 1000px`, `transform-style: preserve-3d` |
| Trash icon | Inline SVG | 16×16, stroke-based, `var(--text-faint)` color, hover → `var(--text-muted)` |
| Batch checkbox | Inline SVG | 16×16, stroke-based, unchecked/checked states |
| Edit icon | Inline SVG | 16×16, stroke-based, pencil glyph |
| Batch toolbar | HTML bar | Fixed above grid, contains destructive + cancel buttons |

### Modified Components
| Component | Changes |
|-----------|---------|
| `StoryCard.svelte` | Card flip wrapper, trash icon (hover), date moved to footer, batch checkbox, card-back face with 3 actions |
| `Dashboard.svelte` | Batch mode state, batch toolbar, event handlers from StoryCard |
| `story.svelte.ts` | No structural changes (Dashboard handles post-delete routing) |
| `stories.py` (backend) | Orphan canonical character cleanup in `delete_story()`, new `PATCH /api/stories/{story_id}` endpoint |

---

## Interaction States

### Card Front Face
| State | Visual |
|-------|--------|
| Default | `var(--sidebar-bg)` bg, `var(--border-color)` border, no trash icon visible |
| Hover | `#6366f1` border, `var(--hover-bg)` bg, trash icon fades in top-right |
| Active (pressed) | Subtle scale(0.98) for tactile feel |
| Batch selected | `#6366f1` 2px border, slight bg tint `rgba(99, 102, 241, 0.08)` |
| Batch unselected | Default appearance with checkbox visible |

### Card Back Face
| State | Visual |
|-------|--------|
| Flipped (default) | Shows 3 action buttons: Delete (destructive), Edit, Select Multiple |
| Flipped (edit) | Shows title input + premise textarea + Save/Cancel |
| Cancel | Click outside, press Escape, or "Cancel" flips back to front |

### Trash Icon
| State | Visual |
|-------|--------|
| Hidden | `opacity: 0` on card front when not hovered |
| Visible | `opacity: 1` on card hover, smooth 150ms fade |
| Hover | Color shifts from `var(--text-faint)` to destructive `#ef4444` |

### Batch Toolbar
| State | Visual |
|-------|--------|
| Hidden | `display: none` when `batchMode === false` |
| Visible | Slides in below dashboard header, full width of grid, `var(--sidebar-bg)` bg, `var(--border-color)` bottom border |
| Delete Selected hover | Destructive bg `#ef4444`, white text |
| Cancel hover | Default button hover pattern |

---

## Animation Specifications

| Animation | Duration | Easing | Details |
|-----------|----------|--------|---------|
| Card flip | 400ms | `ease-in-out` | `rotateY(180deg)`, `perspective: 1000px` on parent |
| Trash icon fade-in | 150ms | `ease` | `opacity: 0 → 1` on card hover |
| Batch toolbar slide | 200ms | `ease-out` | `translateY(-8px → 0)` + `opacity` |
| Card delete removal | 250ms | `ease-in` | `opacity: 1 → 0` + `scale(1 → 0.95)` then reflow |

---

## Accessibility

| Element | Requirement |
|---------|-------------|
| Trash icon button | `aria-label="Delete story"`, `role="button"`, keyboard focusable |
| Card flip | `aria-live="polite"` on card-back, announce "Delete options visible" |
| Batch checkbox | `aria-label="Select [title]"`, `role="checkbox"`, `aria-checked` |
| Delete confirmation | Focus trapped on card-back while flipped, Escape to dismiss |
| Batch toolbar | Focus moves to toolbar when batch mode activates |
| Destructive buttons | `aria-label` includes "destructive" context, e.g. "Delete story permanently" |

---

## Layout Specifications

### Card Front (modified)
```
┌────────────────────────────────────────┐
│ [Title]                    [🗑] (hover) │  ← header: title only, trash on hover
│                                        │
│ Premise text clamped to 3 lines...     │  ← premise
│                                        │
│ [badge] [badge] [+N]  Today · 5 para.  │  ← footer: chars + date + count
└────────────────────────────────────────┘
```

### Card Back (flipped)
```
┌────────────────────────────────────────┐
│                                        │
│     Delete "Story Title"?              │  ← heading
│                                        │
│     [🗑 Delete]                        │  ← destructive button
│     [✏ Edit]                           │  ← secondary button
│     [☑ Select Multiple]                │  ← secondary button
│                                        │
└────────────────────────────────────────┘
```

### Card Back — Edit Mode
```
┌────────────────────────────────────────┐
│                                        │
│  Title: [________________]             │
│  Premise:                              │
│  [________________________]            │
│  [________________________]            │
│                                        │
│  [Save Changes]  [Cancel]              │
└────────────────────────────────────────┘
```

### Batch Toolbar (above grid)
```
┌──────────────────────────────────────────────────────────┐
│  🗑 Delete Selected (3)              Cancel Selection     │
└──────────────────────────────────────────────────────────┘
```

### Card Front — Batch Mode
```
┌────────────────────────────────────────┐
│ [☐]                                    │  ← checkbox top-left
│ [Title]                                │  ← header: title only
│ Premise text clamped to 3 lines...     │
│ [badge] [badge] [+N]  Today · 5 para.  │
└────────────────────────────────────────┘
```

---

## Registry Safety

| Registry        | Blocks Used | Safety Gate   |
| --------------- | ----------- | ------------- |
| none (no shadcn)| n/a         | not applicable |

No third-party component registries. All new UI elements are custom SVG icons and CSS.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS (no registries)

**Approval:** approved 2026-04-28
