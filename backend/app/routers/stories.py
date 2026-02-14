"""REST API endpoints for story and node CRUD operations."""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.models.schemas import NodeResponse, StoryCreateRequest, StoryResponse
from app.services.export import export_story_markdown


router = APIRouter(prefix="/api/stories", tags=["stories"])


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


def _row_to_node(row, spans: list[dict] | None = None) -> dict:
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


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """Get a story with its full node tree and provenance spans."""
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
