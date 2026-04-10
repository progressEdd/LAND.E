-- Migration 003: Cross-story character identity tables
-- Adds global character identity layer: canonical characters, name aliases, and story appearances.
-- Enables linking the same character across multiple stories for a shared universe view.

-- Canonical characters: global identity for a character that may appear across multiple stories
-- Each canonical character has a user-confirmed name and accumulates profile data over time.
CREATE TABLE IF NOT EXISTS canonical_characters (
    id TEXT PRIMARY KEY,              -- UUID
    canonical_name TEXT NOT NULL,     -- User-confirmed canonical name (e.g. "Chloe Miller")
    description TEXT,                 -- Free-text character description (user-editable character bible entry)
    traits TEXT,                      -- JSON array of character trait strings (e.g. ["brave","curious"])
    arc_summary TEXT,                 -- Accumulated arc summary across stories
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Character aliases: maps LLM-generated character names (per story) to their canonical identity
-- A raw name like "Chloe Miller (teenage daughter)" gets normalized to "Chloe Miller" for matching.
CREATE TABLE IF NOT EXISTS character_aliases (
    id TEXT PRIMARY KEY,              -- UUID
    canonical_id TEXT NOT NULL REFERENCES canonical_characters(id) ON DELETE CASCADE,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    raw_name TEXT NOT NULL,           -- Original LLM-generated name (e.g. "Chloe Miller (teenage daughter)")
    normalized_name TEXT NOT NULL,    -- Normalized form (e.g. "Chloe Miller") used for auto-matching
    status TEXT NOT NULL DEFAULT 'suggested',  -- One of: 'suggested', 'confirmed', 'split', 'rejected'
    role_in_story TEXT,               -- Role context for this character in this specific story
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Prevent duplicate alias entries for the same raw name in the same story under the same canonical
    UNIQUE(canonical_id, story_id, raw_name)
);

-- Character story appearances: tracks which canonical characters appear in which stories
-- Provides per-story context (role, arc notes) for the character's cross-story profile.
CREATE TABLE IF NOT EXISTS character_story_appearances (
    id TEXT PRIMARY KEY,              -- UUID
    canonical_id TEXT NOT NULL REFERENCES canonical_characters(id) ON DELETE CASCADE,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    role TEXT,                        -- Role in this story
    context TEXT,                     -- How the character appears in this story
    arc_notes TEXT,                   -- Character arc notes specific to this story
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- One appearance record per canonical character per story
    UNIQUE(canonical_id, story_id)
);

-- Indexes for cross-story character queries
CREATE INDEX IF NOT EXISTS idx_char_aliases_canonical ON character_aliases(canonical_id);
CREATE INDEX IF NOT EXISTS idx_char_aliases_story ON character_aliases(story_id);
CREATE INDEX IF NOT EXISTS idx_char_aliases_normalized ON character_aliases(normalized_name);
CREATE INDEX IF NOT EXISTS idx_char_aliases_status ON character_aliases(status);
CREATE INDEX IF NOT EXISTS idx_char_appearances_canonical ON character_story_appearances(canonical_id);
CREATE INDEX IF NOT EXISTS idx_char_appearances_story ON character_story_appearances(story_id);
