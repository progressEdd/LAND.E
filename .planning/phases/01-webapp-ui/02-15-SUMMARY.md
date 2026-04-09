# Plan 02-15 Summary: Single-Letter Character Labels, Clickable Seed Nodes

## What Was Done

Fixed character label overflow in the graph by switching to single first letter, and added interactive seed nodes that let users click to trigger seed-guided AI generation directly from the graph.

### Before (issues addressed)

![Character labels overflow with concatenated initials, seeds are plain text in sidebar](../../../00-supporting-files/images/02-CONTEXT/20260214015225.png)

### Changes

**NodeGraph.svelte — Single-letter character labels:**
- Replaced `initials(name)` (which concatenated first chars of all words) with `initial(name)` — returns only `name.trim().charAt(0).toUpperCase()`
- "Detective Miles Corbin" now renders as "D" instead of "DMCASBSD"

**NodeGraph.svelte — Clickable seed nodes:**
- Added `PositionedSeed` interface and `seeds` array to `GraphLayout`
- Added layout constants: `SEED_RADIUS=10`, `SEED_SPACING_X=40`, `SEED_OFFSET_Y=44`
- Seeds are positioned by fanning out horizontally below the last active paragraph node when `generationState.lastAnalysis` has seeds and status is `idle`
- Added `handleSeedClick(seed)` — triggers `generationState.startGeneration(storyId, lastNodeId, seed.text)`
- Added `showSeedTooltip(e, seed)` — shows "Seed N" title with full seed text in body
- Rendered as dashed amber circles (#fbbf24) with numbered labels (1, 2, 3...) connected by dashed amber lines to the parent node
- Seeds disappear automatically when generation starts (status leaves `idle`)

**generation.svelte.ts — Seed parameter:**
- `startGeneration()` now accepts optional `seed?: string` parameter
- Passes `seed` through in the WS `generate` message when provided

**ws.ts — WS message type:**
- Added optional `seed?: string` field to the `generate` client message type

**story.py — Seed-guided generation:**
- Added `seed: str | None = None` parameter to `run_cycle()`
- When seed is provided, appends `"\n\nDirectional seed (follow this beat):\n{seed}"` to the continuation prompt

**ws.py — WS handler:**
- Passes `msg.get("seed")` through to `run_cycle()` in the generate handler

### Commits

- **webapp-ui branch:** `a315640` — feat(02-15): single-letter character labels, clickable seed nodes in graph with seed-guided generation

### Decisions

- Used single first letter instead of scaling text to fit — simpler, cleaner, and the hover tooltip already shows the full name
- Seeds render only in `idle` state (after generation completes, before next starts) — they naturally disappear when clicked because `startGeneration` sets status to `generating`
- Amber (#fbbf24) dashed styling differentiates seeds from paragraph nodes (solid indigo) and draft nodes (dashed amber fill) — seeds have dashed outline only, no fill
- Seed hint is appended to the continuation prompt rather than replacing analysis seeds — the LLM still sees the full analysis context and is gently steered toward the chosen beat
