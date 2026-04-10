# Phase 02: Cross-Story Knowledge Graph — Research

**Researched:** 2026-04-10
**Status:** Complete

## Research Question

**What do I need to know to PLAN this phase well?**

This phase adds a cross-story character identity layer on top of the existing story dashboard graph. The system must: (1) identify when characters in different stories are the same person, (2) let users confirm/split these matches, (3) render linked characters as unified nodes on the graph, and (4) accumulate a rich character profile spanning all stories.

---

## 1. Current Data Architecture

### What Already Exists

**character_mentions table** (per-node, per-story):
- `id` (UUID PK), `node_id` (FK→nodes), `character_name` (TEXT), `role` (TEXT, currently NULL), `created_at`
- Unique constraint: `(node_id, character_name)`
- Character names are LLM-generated descriptive strings like `"Chloe Miller (teenage daughter)"`, `"The Weathervane (an inanimate object with unusual agency)"`
- The `role` field is unused — role info is embedded in the name string

**stories_overview() endpoint** already aggregates characters across stories:
```python
# Returns StoryOverviewCharacter(name="Chloe Miller", story_ids=["uuid1", "uuid2"])
# Groups by exact character_name match
```

**DashboardGraph.svelte** renders:
- Story nodes as `foreignObject` cards (180×80px)
- Character nodes as colored circles (r=20) with first-letter labels
- d3-force with synchronous 120 ticks, forceLink/forceManyBody/forceCenter/forceCollide
- Links: character→story edges (char:Name → story-uuid)
- Zoom/pan with pointer capture, wheel zoom, reset button

### Key Gap

Currently, character identity is **per-story by exact name string**. Two stories that both have `"Chloe Miller (teenage daughter)"` are already linked by the existing `stories_overview()` grouping. But `"Chloe Miller"` in one story and `"Chloe Miller (protagonist)"` in another would NOT match — these are treated as different characters.

## 2. Character Identity Problem

### Challenge

LLM-generated character names are **non-deterministic descriptive strings**. The same fictional person might appear as:
- `"Chloe Miller (teenage daughter)"` in story A
- `"Chloe Miller"` in story B
- `"Chloe (the daughter)"` in story C
- `"C. Miller"` in story D

### Recommended Approach: Normalized Name Matching + User Confirmation

**Step 1 — Normalization function:**
Extract the "canonical name" from the LLM-generated string:
- Strip parenthetical suffixes: `"Chloe Miller (teenage daughter)"` → `"Chloe Miller"`
- Strip articles: `"The Weathervane (an inanimate object)"` → `"Weathervane"`
- Collapse whitespace, trim
- This gives a normalized key for fuzzy grouping

**Step 2 — Auto-suggest groups:**
Group characters whose normalized names match (exact match on normalized form). Present as suggestions to the user.

**Step 3 — User confirms or splits:**
- User sees: "Chloe Miller appears in 3 stories — link them?" → Confirm
- User sees: "The Narrator appears in 2 stories — but they're different characters" → Split
- User can also manually link characters the system didn't auto-match

### Name Normalization Algorithm

```python
import re

def normalize_character_name(raw_name: str) -> str:
    """Extract canonical name from LLM-generated descriptive string."""
    # Remove parenthetical descriptions
    name = re.sub(r'\s*\([^)]*\)', '', raw_name).strip()
    # Remove leading articles
    name = re.sub(r'^(The|A|An)\s+', '', name, flags=re.IGNORECASE).strip()
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name)
    return name
```

This handles ~80% of cases. Edge cases ("Chloe" vs "Chloe Miller") need manual resolution.

## 3. Database Schema Design

### New Tables Needed

**canonical_characters** — Global character identity:
```sql
CREATE TABLE IF NOT EXISTS canonical_characters (
    id TEXT PRIMARY KEY,                          -- UUID
    canonical_name TEXT NOT NULL,                 -- User-confirmed canonical name
    description TEXT,                             -- Optional: accumulated character description
    traits TEXT,                                  -- JSON array of traits
    arc_summary TEXT,                             -- Accumulated arc summary
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**character_aliases** — Links LLM-generated mentions to canonical characters:
```sql
CREATE TABLE IF NOT EXISTS character_aliases (
    id TEXT PRIMARY KEY,                          -- UUID
    canonical_id TEXT NOT NULL REFERENCES canonical_characters(id) ON DELETE CASCADE,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    raw_name TEXT NOT NULL,                       -- Original LLM-generated name
    normalized_name TEXT NOT NULL,                -- Normalized form used for matching
    status TEXT NOT NULL DEFAULT 'suggested',     -- 'suggested' | 'confirmed' | 'split'
    role_in_story TEXT,                           -- Role context specific to this story
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    UNIQUE(canonical_id, story_id, raw_name)
);
```

**character_story_appearances** — Rich per-story appearance data:
```sql
CREATE TABLE IF NOT EXISTS character_story_appearances (
    id TEXT PRIMARY KEY,                          -- UUID
    canonical_id TEXT NOT NULL REFERENCES canonical_characters(id) ON DELETE CASCADE,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    role TEXT,                                    -- Role in this story
    context TEXT,                                 -- How the character appears in this story
    arc_notes TEXT,                               -- Character arc in this story
    created_at TEXT NOT NOT NULL DEFAULT (datetime('now')),
    
    UNIQUE(canonical_id, story_id)
);
```

### Migration Strategy

New migration file: `003_cross_story_characters.sql`
- Creates 3 new tables
- Does NOT modify existing `character_mentions` table (backward compatible)
- Existing `character_mentions` data stays as-is; the new layer sits on top

### Data Flow

```
character_mentions (per-node, per-story — unchanged)
        ↓ aggregation
stories_overview() → groups by exact name → StoryOverviewCharacter
        ↓ NEW: normalization + matching
character_aliases → maps raw names → canonical_characters
        ↓
Dashboard graph shows canonical characters as unified nodes
```

## 4. API Design

### New Endpoints Needed

**GET /api/characters/candidates** — Auto-suggested matches:
- Normalizes all character names across stories
- Groups by normalized name where multiple stories match
- Returns list of candidate groups with raw names + story IDs
- Response: `{ candidates: [{ normalized_name, mentions: [{ raw_name, story_id, story_title }] }] }`

**POST /api/characters/link** — Confirm a match group:
- Takes a list of raw_name + story_id pairs to link into one canonical character
- Creates canonical_characters record + character_aliases records with status='confirmed'
- Returns the new canonical character

**POST /api/characters/split** — Split a false match:
- Takes a canonical_id and list of raw_name + story_id pairs to separate
- Creates a new canonical_characters record for the split group
- Moves specified aliases to the new canonical

**GET /api/characters/{id}** — Get canonical character with full profile:
- Returns canonical name, traits, description, arc_summary
- Includes per-story appearances with role/context
- Includes list of all raw names across stories

**PATCH /api/characters/{id}** — Edit character profile:
- Update canonical_name, description, traits, arc_summary
- User-editable character bible

**GET /api/characters** — List all canonical characters:
- For overview / graph data
- Returns minimal data: id, canonical_name, story_count, story_ids

**DELETE /api/characters/{id}** — Remove canonical character:
- Removes canonical record and all aliases
- Does NOT touch original character_mentions

### Modified Endpoints

**GET /api/stories/overview** — Enhanced with canonical data:
- Add optional `?linked=true` query param
- When true, returns canonical character data instead of raw names
- StoryOverviewCharacter gains optional `canonical_id` field

## 5. Graph Visualization Changes

### Current Rendering (DashboardGraph.svelte)

- Story nodes: foreignObject cards (180×80)
- Character nodes: colored circles (r=20) with first-letter label
- Links: thin dashed lines (opacity 0.3)
- Layout: d3-force, 120 ticks synchronous
- Interactions: click story→open, hover character→show name

### Needed Changes

**Linked character rendering:**
- Characters with `canonical_id` (confirmed links) render as **unified nodes** connected to multiple stories
- Visual distinction: larger node, double-ring border, or glow effect
- Show story count badge (e.g., "3" indicator for appearing in 3 stories)

**Unlinked character rendering:**
- Characters without canonical link remain per-story circles (current behavior)
- No visual change needed

**Match suggestion UI on graph:**
- Candidate groups highlighted with dashed connecting lines
- Click to open confirm/split dialog
- Could be: modal, side panel, or inline badge

**Character detail panel:**
- Click a linked character → slide-out panel with character profile
- Shows: canonical name, description, traits, per-story appearances
- Editable fields for user to enrich the character bible

### d3-force Considerations

- Adding unified character nodes with connections to multiple stories will **naturally cluster** stories that share characters — this matches D-06 (no explicit universe table)
- Stories without shared characters will drift apart — also desired behavior
- May need to adjust `forceLink` distance for cross-story edges vs intra-story edges
- Consider increasing `forceManyBody` strength for larger graphs

### Force Parameters

Current: linkDistance=100, charge=-250, collide=60

Recommended for cross-story:
- Story-character links: distance=80 (tighter)
- Cross-story character links: keep at 100 (breathing room)
- Charge: increase to -300 for better separation with more nodes
- Collide: increase to 70 for larger unified character nodes

## 6. Frontend Component Architecture

### New Components

**CharacterMatchPanel.svelte** — Match suggestion + confirmation UI:
- Lists candidate groups: "These characters might be the same person"
- For each group: confirm (link) or split buttons
- Shows raw names + story titles for context

**CharacterProfilePanel.svelte** — Character bible view/edit:
- Slides in from right (or modal)
- Fields: canonical name, description, traits, arc summary
- Per-story appearance list with roles
- Editable text areas

### Modified Components

**DashboardGraph.svelte** — Enhanced node types:
- New node type: `'linked_character'` (distinct from `'character'`)
- Larger radius, multi-ring or glow for linked characters
- Click handler: linked_character → open CharacterProfilePanel
- Candidate suggestions rendered as dashed connecting lines

**Dashboard.svelte** — Panel integration:
- Host CharacterMatchPanel when suggestions available
- Host CharacterProfilePanel when character selected
- Add "Characters" tab or section alongside story cards

### State Management

New store or extend existing:
```typescript
interface CharacterState {
    canonicalCharacters: CanonicalCharacter[];
    candidates: CharacterCandidate[];
    selectedCharacter: CanonicalCharacter | null;
    showMatchPanel: boolean;
    showProfilePanel: boolean;
}
```

## 7. Character Profile Accumulation Strategy

### How Profiles Grow

**Option A — Manual only (Recommended for v1):**
- User creates canonical character by linking
- User manually fills in description, traits, arc notes
- System provides raw material (character names, story contexts) but doesn't auto-populate

**Option B — LLM-assisted:**
- When characters are linked, call LLM to merge/summarize their descriptions
- Generate initial character profile from cast data across stories
- More impressive but adds complexity and latency

**Recommendation:** Start with Option A (manual). The LLM-assisted version can be a future enhancement. The linking/splitting UX and graph visualization are the core value.

### Profile Data Sources

From existing data, per canonical character:
- All raw names → aliases list
- All story_ids → story appearance list
- Character mentions → which nodes they appear in (for context)

New data the user adds:
- Canonical name (editable)
- Free-text description
- Traits (tag list or free text)
- Per-story arc notes

## 8. Technical Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Name normalization misses valid matches | User must manually link | Provide manual link UI |
| Name normalization creates false matches | User splits | Default to "suggested" status, require confirmation |
| Graph clutter with many characters | Visual noise | Limit displayed characters, add filtering |
| Large number of candidate suggestions | Overwhelming | Batch suggestions, priority ranking |
| SQLite performance with cross-story queries | Slow overview endpoint | Index on normalized_name, canonical_id |
| d3-force instability with many nodes | Layout breaks | Adaptive force parameters, zoom/pan |

## 9. Existing Patterns to Follow

From CONTEXT.md canonical_refs:

1. **Database**: New migration file `003_cross_story_characters.sql` — follow pattern of 001/002
2. **Pydantic schemas**: Add new models to `schemas.py` — follow existing naming (CanonicalCharacter, CharacterAlias, etc.)
3. **API router**: Either extend `stories.py` or create new `characters.py` router — recommend new router for clean separation
4. **Frontend types**: Add to `types/index.ts` — follow existing interface patterns
5. **API client**: Add methods to `rest.ts` ApiClient class
6. **Svelte components**: Follow existing patterns (onMount, $state, CSS custom properties for theming)
7. **Stores**: Svelte 5 runes class pattern if new store needed

## 10. Implementation Waves Recommendation

Based on dependencies:

**Wave 1 — Data Foundation (parallel):**
- Migration 003 + database helper functions
- Pydantic schemas + TypeScript types

**Wave 2 — Character Identity API:**
- New characters router with CRUD endpoints
- Name normalization logic
- Candidate suggestion endpoint
- Enhanced overview endpoint

**Wave 3 — Frontend Integration:**
- API client methods
- CharacterMatchPanel component
- CharacterProfilePanel component
- DashboardGraph enhancements (linked character rendering)

**Wave 4 — UX Polish:**
- Match suggestion flow (suggest → confirm/split)
- Character profile editing
- Graph clustering visualization tuning
- Edge cases (unlink, re-link, delete)

---

## RESEARCH COMPLETE

Key findings:
1. The existing `stories_overview()` already does cross-story character aggregation by exact name — this is the foundation to build on
2. A new `canonical_characters` + `character_aliases` layer sits cleanly above `character_mentions` without modifying existing tables
3. Name normalization with user confirmation is the right approach for handling LLM-generated descriptive names
4. The dashboard graph's d3-force will naturally cluster shared-character stories — no explicit universe table needed
5. Recommend 4 implementation waves: data → API → frontend → polish
6. Character profile should start manual-only; LLM-assisted profiles are a future enhancement
7. New `characters.py` router keeps the codebase clean; extend `stories_overview()` for linked data
