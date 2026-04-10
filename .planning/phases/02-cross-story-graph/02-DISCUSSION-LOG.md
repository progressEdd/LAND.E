# Phase 02: Cross-Story Knowledge Graph - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 02-cross-story-graph
**Areas discussed:** Character matching strategy, Graph visualization, Universe/grouping model, Character profile depth

---

## Character Matching Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Automatic name matching | Same name = same character. Simple but risky with descriptive LLM names. | |
| Manual user linking | User explicitly links characters. Precise but labor-intensive. | |
| Hybrid: auto-suggest + confirm | System normalizes names, suggests matches, user confirms or splits. | ✓ |
| LLM-assisted matching | Send character contexts to LLM for judgment. Nondeterministic. | |

**User's choice:** Hybrid — auto-suggest by normalized name, user confirms or splits.
**Notes:** Key insight from codebase exploration — character names are LLM-generated descriptive strings like "Chloe Miller (teenage daughter)", not clean proper nouns. Normalization needs to extract base name while preserving full descriptive string as context.

---

## Graph Visualization

| Option | Description | Selected |
|--------|-------------|----------|
| Enhance existing dashboard graph | Add linking/splitting controls directly on DashboardGraph.svelte. Consistent UI. | ✓ |
| Dedicated cross-story view | New full-page view for universe exploration. Dashboard stays overview-only. | |
| Both (progressive) | Dashboard shows overview + indicators, detail view for managing links. | |

**User's choice:** Enhance the existing dashboard graph.
**Notes:** Keep everything in one place — linking/splitting happens right on the dashboard.

---

## Universe / Grouping Model

| Option | Description | Selected |
|--------|-------------|----------|
| No universe — just character links | Stories stay flat, only cross-story structure is shared characters. | |
| Explicit universe/series grouping | User creates universe, adds stories. Characters scoped to universe. | |
| Auto-cluster by shared characters | Graph visually clusters stories sharing characters. Implicit universes. | ✓ |

**User's choice:** Auto-cluster by shared characters — no explicit universe table.
**Notes:** No management overhead. The force-directed layout naturally groups related stories.

---

## Character Profile Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal: name + linked stories | Canonical name and which stories they appear in. | |
| Moderate: name + description + role-per-story | Canonical name, description, plus role as it appears in each linked story. | |
| Rich: full character sheet | Name, description, traits, arc summary, all appearances with context. Living character bible. | ✓ |

**User's choice:** Rich character sheet — full profile that grows with each story.
**Notes:** Essentially a "character bible" — something a writer would reference when continuing a series.

---

## the agent's Discretion

- Name normalization algorithm (extracting base name from descriptive LLM strings)
- UI for confirm/split actions (click, drag, context menu, panel)
- Character sheet layout and presentation
- Auto-suggestion presentation format
- Visual treatment for linked vs unlinked nodes
- Whether character sheets are user-editable or auto-populated only

## Deferred Ideas

None — discussion stayed within phase scope.
