-- Migration 002: Graph support tables for node graph visualizer
-- Adds character-to-node mapping and per-node analysis persistence

-- Character mentions: links character names to specific story nodes
CREATE TABLE IF NOT EXISTS character_mentions (
    id TEXT PRIMARY KEY,              -- UUID
    node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    character_name TEXT NOT NULL,     -- Normalized name extracted from StoryAnalysis.cast
    role TEXT,                        -- Optional role descriptor (e.g., "protagonist seeking revenge")
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- One mention per character per node
    UNIQUE(node_id, character_name)
);

-- Node analyses: persists StoryAnalysis JSON per node so it survives page refresh
CREATE TABLE IF NOT EXISTS node_analyses (
    id TEXT PRIMARY KEY,              -- UUID
    node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    analysis_json TEXT NOT NULL,      -- Full StoryAnalysis serialized as JSON
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- One analysis per node (latest wins)
    UNIQUE(node_id)
);

-- Indexes for graph queries
CREATE INDEX IF NOT EXISTS idx_char_mentions_node ON character_mentions(node_id);
CREATE INDEX IF NOT EXISTS idx_char_mentions_name ON character_mentions(character_name);
CREATE INDEX IF NOT EXISTS idx_node_analyses_node ON node_analyses(node_id);
