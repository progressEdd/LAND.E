"""REST API endpoints for story and node CRUD operations."""

import json
import random
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.models.schemas import (
    CharacterMentionResponse,
    CharacterSummary,
    NodeResponse,
    StoryAnalysis,
    StoryCreateRequest,
    StoryOverviewCanonicalCharacter,
    StoryOverviewCharacter,
    StoryOverviewResponse,
    StoryOverviewStory,
    StoryResponse,
    SwitchPathRequest,
    TreeNodeResponse,
    TreeResponse,
)
from app.services.export import export_story_markdown


router = APIRouter(prefix="/api/stories", tags=["stories"])


# ---------- Random premise pool ----------

PREMISES: list[str] = [
    "A retired astronaut receives a handwritten letter from a colony on Mars — one she was told was never established.",
    "Every night at exactly 3:17 AM, every clock in the city stops for thirteen seconds. Tonight, someone finally stays awake to watch what happens during those seconds.",
    "A deep-sea research station picks up a repeating signal from the ocean floor — a lullaby in a language that predates human civilization.",
    "The last bookshop in the world has a back room where the stories rewrite themselves overnight. The owner has been covering it up for decades.",
    "A competitive chess player discovers that her opponent in the championship final has been dead for six years.",
    "In a world where dreams are taxed, a black-market dream dealer discovers that one of her clients is dreaming someone else's memories.",
    "A linguist is hired to translate a manuscript found in a shipwreck. The language is impossible — it hasn't been invented yet.",
    "A forensic botanist is called to a crime scene where the victim's body has been replaced by a perfect topiary replica, still growing.",
    "Two rival food truck owners in a small desert town discover that the strange ingredient making their recipes extraordinary comes from the same unmarked jar left on both their doorsteps.",
    "An AI therapist begins having sessions with a patient who claims to be the AI's own subconscious.",
    "A cartographer mapping unmapped caves finds her own name carved into a wall — in her handwriting — dated two hundred years ago.",
    "The world's greatest violin was lost at sea in 1743. It washes ashore tomorrow, still in tune, still warm to the touch.",
    "A hospice nurse realizes that every patient in Ward C is telling the same story about their childhood, word for word, despite having never met.",
    "A small town's beloved weathervane has always pointed north — until this morning, when it started pointing at specific houses, one by one.",
    "An archivist at the Vatican discovers that every pope's private journal for the last 400 years contains the same unsent letter to the same person.",
    "A beekeeper notices her hives are building structures that look exactly like the floor plan of a building that doesn't exist yet.",
    "A surgeon performing a routine operation finds a message etched on the patient's rib bone. The message is addressed to her.",
    "A lighthouse keeper on a decommissioned island realizes the beam has been signaling coordinates — and something just signaled back.",
    "The last analog photographer develops a roll of film and finds photos of tomorrow. Each one shows a different version of how the day could end.",
    "A museum security guard notices that the subjects in the paintings have been slowly moving over the past year. Tonight, one of them is gone.",
    "A town wakes up to find that every mirror reflects yesterday instead of today.",
    "A retired spy receives a package containing her own obituary, published in a newspaper from a country that doesn't exist.",
    "A child's imaginary friend starts leaving physical footprints in the snow.",
    "An elevator technician discovers a floor between floors — one that doesn't appear on any blueprint but has a mailbox with his name on it.",
    "A storm chaser records a tornado that plays music — a symphony no one has composed yet, but that everyone who hears it recognizes.",
]


# ---------- Request models ----------


class CreateNodeRequest(BaseModel):
    """Request body for creating a new node."""

    parent_id: str
    content: str
    node_type: str = "paragraph"
    source: str = "ai_generated"
    position: Optional[int] = None


class UpdateNodeRequest(BaseModel):
    """Request body for updating a node's content."""

    content: str
    provenance_spans: list[dict] = Field(default_factory=list)


class ProvenanceSpanInput(BaseModel):
    """A provenance span for node content."""

    start_offset: int
    end_offset: int
    source: str


# ---------- Helper functions ----------


def _row_to_node(
    row,
    spans: list[dict] | None = None,
    char_mentions: list[dict] | None = None,
    analysis: StoryAnalysis | None = None,
) -> dict:
    """Convert a database row to a NodeResponse dict."""
    return {
        "id": row["id"],
        "story_id": row["story_id"],
        "parent_id": row["parent_id"],
        "position": row["position"],
        "content": row["content"],
        "node_type": row["node_type"],
        "source": row["source"],
        "is_draft": bool(row["is_draft"]),
        "created_at": row["created_at"],
        "provenance_spans": spans or [],
        "character_mentions": char_mentions or [],
        "analysis": analysis,
    }


def _row_to_story_summary(row) -> dict:
    """Convert a database row to a story summary dict (no nodes)."""
    return {
        "id": row["id"],
        "title": row["title"],
        "premise": row["premise"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# ---------- Story endpoints ----------


@router.get("/random-premise")
async def random_premise():
    """Return a random story premise from the curated pool."""
    return {"premise": random.choice(PREMISES)}


@router.post("", response_model=StoryResponse, status_code=201)
async def create_story(req: StoryCreateRequest):
    """Create a new story with a root node."""
    story_id = uuid.uuid4().hex
    root_node_id = uuid.uuid4().hex
    span_id = uuid.uuid4().hex
    active_path = json.dumps([root_node_id])

    async with get_db() as db:
        # Create story
        await db.execute(
            """INSERT INTO stories (id, title, premise, active_path)
               VALUES (?, ?, ?, ?)""",
            (story_id, req.title, req.premise, active_path),
        )

        # Create root node
        await db.execute(
            """INSERT INTO nodes (id, story_id, parent_id, position, content, node_type, source, is_draft)
               VALUES (?, ?, NULL, 0, ?, 'paragraph', 'initial_prompt', 0)""",
            (root_node_id, story_id, req.premise),
        )

        # Create provenance span for the entire root node content
        await db.execute(
            """INSERT INTO provenance_spans (id, node_id, start_offset, end_offset, source)
               VALUES (?, ?, 0, ?, 'initial_prompt')""",
            (span_id, root_node_id, len(req.premise)),
        )

        await db.commit()

        # Fetch the created story and node
        story_row = await db.execute_fetchall(
            "SELECT * FROM stories WHERE id = ?", (story_id,)
        )
        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE story_id = ? ORDER BY parent_id, position",
            (story_id,),
        )

    story = story_row[0]
    nodes = [_row_to_node(r) for r in node_rows]
    path = json.loads(story["active_path"]) if story["active_path"] else []

    return StoryResponse(
        id=story["id"],
        title=story["title"],
        premise=story["premise"],
        created_at=story["created_at"],
        updated_at=story["updated_at"],
        active_path=path,
        nodes=nodes,
    )


@router.get("", response_model=list[dict])
async def list_stories():
    """List all stories (summaries only, no node trees)."""
    async with get_db() as db:
        rows = await db.execute_fetchall(
            "SELECT * FROM stories ORDER BY updated_at DESC"
        )

    return [_row_to_story_summary(r) for r in rows]


@router.get("/overview", response_model=StoryOverviewResponse)
async def stories_overview():
    """Get all stories with aggregated character data for the dashboard graph and cards."""
    async with get_db() as db:
        # Fetch all stories ordered by updated_at
        story_rows = await db.execute_fetchall(
            "SELECT id, title, premise, created_at, updated_at FROM stories ORDER BY updated_at DESC"
        )

        # Fetch node counts per story
        node_count_rows = await db.execute_fetchall(
            "SELECT story_id, COUNT(*) as node_count FROM nodes GROUP BY story_id"
        )
        node_counts = {r["story_id"]: r["node_count"] for r in node_count_rows}

        # Fetch character→story mappings from character_mentions
        char_rows = await db.execute_fetchall(
            """SELECT DISTINCT cm.character_name, n.story_id
               FROM character_mentions cm
               JOIN nodes n ON cm.node_id = n.id
               ORDER BY cm.character_name"""
        )

        # Build character→story mapping
        char_to_stories: dict[str, list[str]] = {}
        for cr in char_rows:
            name = cr["character_name"]
            sid = cr["story_id"]
            if name not in char_to_stories:
                char_to_stories[name] = []
            if sid not in char_to_stories[name]:
                char_to_stories[name].append(sid)

        # Build story→character mapping
        story_chars: dict[str, list[str]] = {r["id"]: [] for r in story_rows}
        for cr in char_rows:
            name = cr["character_name"]
            sid = cr["story_id"]
            if sid in story_chars and name not in story_chars[sid]:
                story_chars[sid].append(name)

        stories = [
            StoryOverviewStory(
                id=r["id"],
                title=r["title"],
                premise=r["premise"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                character_names=story_chars.get(r["id"], []),
                node_count=node_counts.get(r["id"], 0),
            )
            for r in story_rows
        ]

        # Filter raw characters that have confirmed/suggested aliases
        aliased_rows = await db.execute_fetchall(
            """SELECT raw_name, story_id FROM character_aliases
               WHERE status IN ('confirmed', 'suggested')"""
        )
        aliased_pairs = {(r["raw_name"], r["story_id"]) for r in aliased_rows}

        filtered_char_to_stories = {}
        for name, sids in char_to_stories.items():
            unaliased_sids = [sid for sid in sids if (name, sid) not in aliased_pairs]
            if unaliased_sids:
                filtered_char_to_stories[name] = unaliased_sids

        # Fetch canonical characters with their linked story appearances
        canonical_rows = await db.execute_fetchall(
            """SELECT cc.id, cc.canonical_name, csa.story_id
               FROM canonical_characters cc
               JOIN character_story_appearances csa ON cc.id = csa.canonical_id
               ORDER BY cc.canonical_name"""
        )

        canonical_map: dict[str, dict] = {}
        for cr in canonical_rows:
            cid = cr["id"]
            if cid not in canonical_map:
                canonical_map[cid] = {
                    "id": cid,
                    "canonical_name": cr["canonical_name"],
                    "story_ids": [],
                }
            canonical_map[cid]["story_ids"].append(cr["story_id"])

        characters = [
            StoryOverviewCharacter(name=name, story_ids=sids)
            for name, sids in sorted(filtered_char_to_stories.items())
        ]

        canonical_characters = [
            StoryOverviewCanonicalCharacter(
                id=data["id"],
                canonical_name=data["canonical_name"],
                story_ids=data["story_ids"],
            )
            for data in canonical_map.values()
        ]

    return StoryOverviewResponse(stories=stories, characters=characters, canonical_characters=canonical_characters)


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """Get a story with its full node tree, provenance spans, character mentions, and analyses."""
    async with get_db() as db:
        story_rows = await db.execute_fetchall(
            "SELECT * FROM stories WHERE id = ?", (story_id,)
        )
        if not story_rows:
            raise HTTPException(status_code=404, detail="Story not found")

        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE story_id = ? ORDER BY parent_id, position",
            (story_id,),
        )

        # Fetch all provenance spans for this story's nodes
        node_ids = [r["id"] for r in node_rows]
        spans_by_node: dict[str, list[dict]] = {nid: [] for nid in node_ids}
        mentions_by_node: dict[str, list[dict]] = {nid: [] for nid in node_ids}
        analysis_by_node: dict[str, StoryAnalysis | None] = {
            nid: None for nid in node_ids
        }

        if node_ids:
            placeholders = ", ".join("?" for _ in node_ids)

            # Provenance spans
            span_rows = await db.execute_fetchall(
                f"SELECT node_id, start_offset, end_offset, source FROM provenance_spans WHERE node_id IN ({placeholders}) ORDER BY start_offset",
                tuple(node_ids),
            )
            for sr in span_rows:
                spans_by_node[sr["node_id"]].append(
                    {
                        "start_offset": sr["start_offset"],
                        "end_offset": sr["end_offset"],
                        "source": sr["source"],
                    }
                )

            # Character mentions
            char_rows = await db.execute_fetchall(
                f"SELECT node_id, character_name, role FROM character_mentions WHERE node_id IN ({placeholders})",
                tuple(node_ids),
            )
            for cr in char_rows:
                mentions_by_node[cr["node_id"]].append(
                    {
                        "character_name": cr["character_name"],
                        "role": cr["role"],
                    }
                )

            # Node analyses
            analysis_rows = await db.execute_fetchall(
                f"SELECT node_id, analysis_json FROM node_analyses WHERE node_id IN ({placeholders})",
                tuple(node_ids),
            )
            for ar in analysis_rows:
                try:
                    analysis_by_node[ar["node_id"]] = StoryAnalysis.model_validate_json(
                        ar["analysis_json"]
                    )
                except Exception:
                    pass

    story = story_rows[0]
    nodes = [
        _row_to_node(
            r,
            spans_by_node.get(r["id"], []),
            mentions_by_node.get(r["id"], []),
            analysis_by_node.get(r["id"]),
        )
        for r in node_rows
    ]
    path = json.loads(story["active_path"]) if story["active_path"] else []

    return StoryResponse(
        id=story["id"],
        title=story["title"],
        premise=story["premise"],
        created_at=story["created_at"],
        updated_at=story["updated_at"],
        active_path=path,
        nodes=nodes,
    )


@router.get("/{story_id}/tree", response_model=TreeResponse)
async def get_story_tree(story_id: str):
    """Get the full story tree structure for the graph visualizer.

    Returns a recursive tree with character mentions and analyses per node,
    plus an aggregated characters list for supernode rendering.
    """
    async with get_db() as db:
        story_rows = await db.execute_fetchall(
            "SELECT * FROM stories WHERE id = ?", (story_id,)
        )
        if not story_rows:
            raise HTTPException(status_code=404, detail="Story not found")

        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE story_id = ? ORDER BY parent_id, position",
            (story_id,),
        )

        node_ids = [r["id"] for r in node_rows]

        # Fetch provenance spans, character mentions, and analyses
        spans_by_node: dict[str, list[dict]] = {nid: [] for nid in node_ids}
        mentions_by_node: dict[str, list[dict]] = {nid: [] for nid in node_ids}
        analysis_by_node: dict[str, StoryAnalysis | None] = {
            nid: None for nid in node_ids
        }

        if node_ids:
            placeholders = ", ".join("?" for _ in node_ids)

            span_rows = await db.execute_fetchall(
                f"SELECT node_id, start_offset, end_offset, source FROM provenance_spans WHERE node_id IN ({placeholders}) ORDER BY start_offset",
                tuple(node_ids),
            )
            for sr in span_rows:
                spans_by_node[sr["node_id"]].append(
                    {
                        "start_offset": sr["start_offset"],
                        "end_offset": sr["end_offset"],
                        "source": sr["source"],
                    }
                )

            char_rows = await db.execute_fetchall(
                f"SELECT node_id, character_name, role FROM character_mentions WHERE node_id IN ({placeholders})",
                tuple(node_ids),
            )
            for cr in char_rows:
                mentions_by_node[cr["node_id"]].append(
                    {
                        "character_name": cr["character_name"],
                        "role": cr["role"],
                    }
                )

            analysis_rows = await db.execute_fetchall(
                f"SELECT node_id, analysis_json FROM node_analyses WHERE node_id IN ({placeholders})",
                tuple(node_ids),
            )
            for ar in analysis_rows:
                try:
                    analysis_by_node[ar["node_id"]] = StoryAnalysis.model_validate_json(
                        ar["analysis_json"]
                    )
                except Exception:
                    pass

    story = story_rows[0]
    path = json.loads(story["active_path"]) if story["active_path"] else []

    # Build tree from flat node list
    tree_nodes: dict[str, TreeNodeResponse] = {}
    root_node: TreeNodeResponse | None = None

    for r in node_rows:
        nid = r["id"]
        tree_node = TreeNodeResponse(
            id=nid,
            story_id=r["story_id"],
            parent_id=r["parent_id"],
            position=r["position"],
            content=r["content"],
            node_type=r["node_type"],
            source=r["source"],
            is_draft=bool(r["is_draft"]),
            created_at=r["created_at"],
            provenance_spans=spans_by_node.get(nid, []),
            character_mentions=mentions_by_node.get(nid, []),
            analysis=analysis_by_node.get(nid),
            children=[],
        )
        tree_nodes[nid] = tree_node
        if r["parent_id"] is None:
            root_node = tree_node

    # Wire up parent-child relationships
    for nid, tree_node in tree_nodes.items():
        if tree_node.parent_id and tree_node.parent_id in tree_nodes:
            tree_nodes[tree_node.parent_id].children.append(tree_node)

    # Sort children by position
    for tree_node in tree_nodes.values():
        tree_node.children.sort(key=lambda c: c.position)

    # Aggregate character supernodes
    char_to_nodes: dict[str, list[str]] = {}
    for nid, mentions in mentions_by_node.items():
        for m in mentions:
            name = m["character_name"]
            if name not in char_to_nodes:
                char_to_nodes[name] = []
            char_to_nodes[name].append(nid)

    characters = [
        CharacterSummary(name=name, node_ids=nids)
        for name, nids in sorted(char_to_nodes.items())
    ]

    return TreeResponse(
        story_id=story["id"],
        title=story["title"],
        premise=story["premise"],
        active_path=path,
        root=root_node,
        characters=characters,
    )


@router.delete("/{story_id}", status_code=204)
async def delete_story(story_id: str):
    """Delete a story (cascading delete removes nodes and spans)."""
    async with get_db() as db:
        story_rows = await db.execute_fetchall(
            "SELECT id FROM stories WHERE id = ?", (story_id,)
        )
        if not story_rows:
            raise HTTPException(status_code=404, detail="Story not found")

        await db.execute("DELETE FROM stories WHERE id = ?", (story_id,))
        await db.commit()

    return None


# ---------- Node endpoints ----------


@router.post("/{story_id}/nodes", response_model=NodeResponse, status_code=201)
async def create_node(story_id: str, req: CreateNodeRequest):
    """Create a new node in the story tree."""
    node_id = uuid.uuid4().hex

    async with get_db() as db:
        # Verify story exists
        story_rows = await db.execute_fetchall(
            "SELECT id FROM stories WHERE id = ?", (story_id,)
        )
        if not story_rows:
            raise HTTPException(status_code=404, detail="Story not found")

        # Calculate position if not provided
        position = req.position
        if position is None:
            pos_rows = await db.execute_fetchall(
                "SELECT COALESCE(MAX(position), -1) + 1 as next_pos FROM nodes WHERE story_id = ? AND parent_id = ?",
                (story_id, req.parent_id),
            )
            position = pos_rows[0]["next_pos"]

        # Create the node
        await db.execute(
            """INSERT INTO nodes (id, story_id, parent_id, position, content, node_type, source, is_draft)
               VALUES (?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                node_id,
                story_id,
                req.parent_id,
                position,
                req.content,
                req.node_type,
                req.source,
            ),
        )

        # Create provenance span for the content
        if req.content:
            span_id = uuid.uuid4().hex
            await db.execute(
                """INSERT INTO provenance_spans (id, node_id, start_offset, end_offset, source)
                   VALUES (?, ?, 0, ?, ?)""",
                (span_id, node_id, len(req.content), req.source),
            )

        await db.commit()

        # Fetch the created node
        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ?", (node_id,)
        )

    return NodeResponse(**_row_to_node(node_rows[0]))


@router.patch("/{story_id}/nodes/{node_id}", response_model=NodeResponse)
async def update_node(story_id: str, node_id: str, req: UpdateNodeRequest):
    """Update a node's content and provenance spans."""
    async with get_db() as db:
        # Verify node exists and belongs to story
        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ? AND story_id = ?",
            (node_id, story_id),
        )
        if not node_rows:
            raise HTTPException(status_code=404, detail="Node not found")

        # Update content
        await db.execute(
            """UPDATE nodes SET content = ? WHERE id = ?""",
            (req.content, node_id),
        )

        # Replace provenance spans
        await db.execute("DELETE FROM provenance_spans WHERE node_id = ?", (node_id,))
        for span in req.provenance_spans:
            span_id = uuid.uuid4().hex
            await db.execute(
                """INSERT INTO provenance_spans (id, node_id, start_offset, end_offset, source)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    span_id,
                    node_id,
                    span.get("start_offset", 0),
                    span.get("end_offset", len(req.content)),
                    span.get("source", "user_edited"),
                ),
            )

        # Update story's updated_at
        await db.execute(
            "UPDATE stories SET updated_at = datetime('now') WHERE id = ?",
            (story_id,),
        )

        await db.commit()

        # Fetch updated node
        updated_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ?", (node_id,)
        )

    return NodeResponse(**_row_to_node(updated_rows[0]))


@router.post("/{story_id}/nodes/{node_id}/accept", response_model=NodeResponse)
async def accept_node(story_id: str, node_id: str):
    """Accept a draft node — sets is_draft=0 and adds to active_path."""
    async with get_db() as db:
        # Verify node exists, is a draft, and belongs to story
        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ? AND story_id = ?",
            (node_id, story_id),
        )
        if not node_rows:
            raise HTTPException(status_code=404, detail="Node not found")

        node = node_rows[0]
        if not node["is_draft"]:
            raise HTTPException(status_code=400, detail="Node is not a draft")

        # Accept the draft
        await db.execute("UPDATE nodes SET is_draft = 0 WHERE id = ?", (node_id,))

        # Update active_path to include this node
        story_rows = await db.execute_fetchall(
            "SELECT active_path FROM stories WHERE id = ?", (story_id,)
        )
        current_path = (
            json.loads(story_rows[0]["active_path"])
            if story_rows[0]["active_path"]
            else []
        )
        if node_id not in current_path:
            current_path.append(node_id)

        await db.execute(
            "UPDATE stories SET active_path = ?, updated_at = datetime('now') WHERE id = ?",
            (json.dumps(current_path), story_id),
        )

        await db.commit()

        # Fetch updated node
        updated_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ?", (node_id,)
        )

    return NodeResponse(**_row_to_node(updated_rows[0]))


@router.post("/{story_id}/nodes/{node_id}/reject", status_code=204)
async def reject_node(story_id: str, node_id: str):
    """Reject a draft node — deletes it and its provenance spans."""
    async with get_db() as db:
        # Verify node exists, is a draft, and belongs to story
        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ? AND story_id = ?",
            (node_id, story_id),
        )
        if not node_rows:
            raise HTTPException(status_code=404, detail="Node not found")

        node = node_rows[0]
        if not node["is_draft"]:
            raise HTTPException(status_code=400, detail="Node is not a draft")

        # Delete the draft node (cascading delete removes spans)
        await db.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        await db.commit()

    return None


# ---------- Branch switching endpoints ----------


@router.patch("/{story_id}/active-path", response_model=StoryResponse)
async def switch_active_path(story_id: str, req: SwitchPathRequest):
    """Switch the active path to follow a different branch.

    Walks up the tree from target_node_id via parent_id to build
    the path from root to target, then updates the story's active_path.
    """
    async with get_db() as db:
        # Verify story exists
        story_rows = await db.execute_fetchall(
            "SELECT * FROM stories WHERE id = ?", (story_id,)
        )
        if not story_rows:
            raise HTTPException(status_code=404, detail="Story not found")

        # Verify target node exists and belongs to story
        target_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE id = ? AND story_id = ?",
            (req.target_node_id, story_id),
        )
        if not target_rows:
            raise HTTPException(status_code=404, detail="Target node not found")

        # Build all nodes map for tree traversal
        all_nodes = await db.execute_fetchall(
            "SELECT id, parent_id FROM nodes WHERE story_id = ?", (story_id,)
        )
        node_parent_map = {r["id"]: r["parent_id"] for r in all_nodes}

        # Walk up from target to root to build path
        path: list[str] = []
        current_id: str | None = req.target_node_id
        visited: set[str] = set()

        while current_id is not None:
            if current_id in visited:
                raise HTTPException(
                    status_code=400, detail="Cycle detected in node tree"
                )
            visited.add(current_id)
            path.append(current_id)
            current_id = node_parent_map.get(current_id)

        # Reverse to get root → ... → target order
        path.reverse()

        # Update active_path
        await db.execute(
            "UPDATE stories SET active_path = ?, updated_at = datetime('now') WHERE id = ?",
            (json.dumps(path), story_id),
        )
        await db.commit()

        # Return updated story with all nodes
        story_rows = await db.execute_fetchall(
            "SELECT * FROM stories WHERE id = ?", (story_id,)
        )
        node_rows = await db.execute_fetchall(
            "SELECT * FROM nodes WHERE story_id = ? ORDER BY parent_id, position",
            (story_id,),
        )

        # Fetch provenance spans for response
        node_ids = [r["id"] for r in node_rows]
        spans_by_node: dict[str, list[dict]] = {nid: [] for nid in node_ids}
        if node_ids:
            placeholders = ", ".join("?" for _ in node_ids)
            span_rows = await db.execute_fetchall(
                f"SELECT node_id, start_offset, end_offset, source FROM provenance_spans WHERE node_id IN ({placeholders}) ORDER BY start_offset",
                tuple(node_ids),
            )
            for sr in span_rows:
                spans_by_node[sr["node_id"]].append(
                    {
                        "start_offset": sr["start_offset"],
                        "end_offset": sr["end_offset"],
                        "source": sr["source"],
                    }
                )

    story = story_rows[0]
    nodes = [_row_to_node(r, spans_by_node.get(r["id"], [])) for r in node_rows]
    updated_path = json.loads(story["active_path"]) if story["active_path"] else []

    return StoryResponse(
        id=story["id"],
        title=story["title"],
        premise=story["premise"],
        created_at=story["created_at"],
        updated_at=story["updated_at"],
        active_path=updated_path,
        nodes=nodes,
    )


# ---------- Export endpoints ----------


@router.get("/{story_id}/export")
async def export_story(story_id: str):
    """Export a story as a downloadable markdown file."""
    try:
        markdown = await export_story_markdown(story_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Story not found")

    # Fetch title for the filename
    async with get_db() as db:
        story_rows = await db.execute_fetchall(
            "SELECT title FROM stories WHERE id = ?", (story_id,)
        )
        title = story_rows[0]["title"] if story_rows else "story"

    # Sanitize title for filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()
    if not safe_title:
        safe_title = "story"

    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}.md"'},
    )
