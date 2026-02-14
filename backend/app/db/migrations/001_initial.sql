-- Stories: top-level container
CREATE TABLE IF NOT EXISTS stories (
    id TEXT PRIMARY KEY,          -- UUID
    title TEXT NOT NULL,
    premise TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    active_path TEXT              -- JSON array of node IDs representing current reading path
);

-- Nodes: each paragraph/block/sentence in the story tree
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,           -- UUID
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    parent_id TEXT REFERENCES nodes(id) ON DELETE SET NULL,  -- NULL for root node
    position INTEGER NOT NULL DEFAULT 0,     -- Order among siblings (for multiple candidates)
    content TEXT NOT NULL,          -- The actual text content
    node_type TEXT NOT NULL DEFAULT 'paragraph',  -- 'paragraph' | 'block' | 'sentence'
    source TEXT NOT NULL DEFAULT 'ai_generated',  -- Primary source for the whole node
    is_draft INTEGER NOT NULL DEFAULT 0,          -- 1 if this is an unaccepted draft
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Tree integrity
    UNIQUE(story_id, parent_id, position)  -- No duplicate positions among siblings
);

-- Provenance spans: character-level source tracking within a node
CREATE TABLE IF NOT EXISTS provenance_spans (
    id TEXT PRIMARY KEY,           -- UUID
    node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    start_offset INTEGER NOT NULL, -- Character offset within node.content
    end_offset INTEGER NOT NULL,   -- Character offset (exclusive)
    source TEXT NOT NULL,           -- 'ai_generated' | 'user_written' | 'user_edited' | 'initial_prompt'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    CHECK(start_offset >= 0),
    CHECK(end_offset > start_offset)
);

-- Index for tree traversal
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_story ON nodes(story_id);
CREATE INDEX IF NOT EXISTS idx_provenance_node ON provenance_spans(node_id);
