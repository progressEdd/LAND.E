"""WebSocket endpoint for streaming AI generation."""

import asyncio
import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.database import get_db
from app.routers.llm import _current_config
from app.services.llm import create_llm_client
from app.services.story import run_cycle, extract_characters


router = APIRouter(tags=["websocket"])


async def _build_story_text(db, story_id: str, active_path: list[str]) -> str:
    """Walk the active_path and concatenate node contents to build the full story text."""
    if not active_path:
        return ""

    placeholders = ",".join("?" for _ in active_path)
    rows = await db.execute_fetchall(
        f"SELECT id, content FROM nodes WHERE story_id = ? AND id IN ({placeholders})",
        (story_id, *active_path),
    )

    # Build a map for ordering by active_path
    content_map = {row["id"]: row["content"] for row in rows}
    parts = [content_map[nid] for nid in active_path if nid in content_map]
    return "\n\n".join(parts)


async def _get_last_node_id(active_path: list[str]) -> str | None:
    """Get the last node ID from the active path (parent for new draft)."""
    return active_path[-1] if active_path else None


@router.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """WebSocket endpoint for AI generation streaming.

    Message types:
    - generate: Start AI generation for a story
    - cancel: Cancel in-progress generation
    - accept: Accept a draft node
    - reject: Reject (delete) a draft node
    """
    await websocket.accept()

    cancel_flag = False
    current_draft_id: str | None = None

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type")

            if msg_type == "generate":
                cancel_flag = False
                story_id = msg["story_id"]
                node_id = msg.get("node_id")  # parent node to continue from

                async with get_db() as db:
                    # Load story
                    story_rows = await db.execute_fetchall(
                        "SELECT * FROM stories WHERE id = ?", (story_id,)
                    )
                    if not story_rows:
                        await websocket.send_json(
                            {"type": "error", "message": "Story not found"}
                        )
                        continue

                    story = story_rows[0]
                    active_path = (
                        json.loads(story["active_path"]) if story["active_path"] else []
                    )
                    premise = story["premise"]

                    # Build story text from active path
                    story_text = await _build_story_text(db, story_id, active_path)

                    # Determine parent node
                    parent_id = node_id or await _get_last_node_id(active_path)
                    if not parent_id:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "No parent node found — create a story first",
                            }
                        )
                        continue

                    # Calculate next position
                    pos_rows = await db.execute_fetchall(
                        "SELECT COALESCE(MAX(position), -1) + 1 as next_pos FROM nodes WHERE story_id = ? AND parent_id = ?",
                        (story_id, parent_id),
                    )
                    next_position = pos_rows[0]["next_pos"]

                    # Create draft node
                    draft_id = uuid.uuid4().hex
                    current_draft_id = draft_id
                    await db.execute(
                        """INSERT INTO nodes (id, story_id, parent_id, position, content, node_type, source, is_draft)
                           VALUES (?, ?, ?, ?, '', 'paragraph', 'ai_generated', 1)""",
                        (draft_id, story_id, parent_id, next_position),
                    )
                    await db.commit()

                # Notify client of draft creation
                await websocket.send_json(
                    {"type": "draft_created", "node_id": draft_id}
                )

                # Run the generation cycle
                try:
                    config = _current_config
                    if not config.backend:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "No LLM backend configured — set it in Settings",
                            }
                        )
                        continue

                    client = create_llm_client(config)

                    # Determine model — use settings state
                    # The model is sent from the frontend in the generate message
                    model = msg.get("model", "")
                    if not model:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "No model specified — select a model in Settings",
                            }
                        )
                        continue

                    result = await run_cycle(
                        client,
                        model=model,
                        premise=premise,
                        story_text=story_text,
                        seed=msg.get("seed"),
                    )

                    # Stream the draft text character-by-character
                    draft_text = result.draft_next
                    accumulated = ""

                    for char in draft_text:
                        if cancel_flag:
                            break

                        accumulated += char
                        await websocket.send_json({"type": "token", "content": char})
                        await asyncio.sleep(0.01)  # 10ms per character

                    # Update draft node content in DB
                    async with get_db() as db:
                        await db.execute(
                            "UPDATE nodes SET content = ? WHERE id = ?",
                            (accumulated, draft_id),
                        )

                        # Create provenance span for the generated content
                        if accumulated:
                            span_id = uuid.uuid4().hex
                            await db.execute(
                                """INSERT INTO provenance_spans (id, node_id, start_offset, end_offset, source)
                                   VALUES (?, ?, 0, ?, 'ai_generated')""",
                                (span_id, draft_id, len(accumulated)),
                            )

                        # Persist analysis for this node
                        analysis_id = uuid.uuid4().hex
                        await db.execute(
                            """INSERT OR REPLACE INTO node_analyses (id, node_id, analysis_json)
                               VALUES (?, ?, ?)""",
                            (analysis_id, draft_id, result.analysis.model_dump_json()),
                        )

                        # Extract and persist character mentions
                        characters = extract_characters(result.analysis.cast)
                        for char_name, char_role in characters:
                            char_id = uuid.uuid4().hex
                            await db.execute(
                                """INSERT OR IGNORE INTO character_mentions (id, node_id, character_name, role)
                                   VALUES (?, ?, ?, ?)""",
                                (char_id, draft_id, char_name, char_role),
                            )

                        await db.commit()

                    if cancel_flag:
                        await websocket.send_json(
                            {"type": "cancelled", "node_id": draft_id}
                        )
                    else:
                        # Send complete with analysis
                        analysis_dict = result.analysis.model_dump()
                        await websocket.send_json(
                            {
                                "type": "complete",
                                "node_id": draft_id,
                                "analysis": analysis_dict,
                            }
                        )

                except Exception as e:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Generation failed: {type(e).__name__}: {e}",
                        }
                    )

            elif msg_type == "cancel":
                cancel_flag = True

            elif msg_type == "accept":
                accept_node_id = msg["node_id"]
                accept_content = msg.get("content", "")
                accept_spans = msg.get("provenance_spans", [])

                async with get_db() as db:
                    # Update draft node: is_draft=0, update content
                    await db.execute(
                        "UPDATE nodes SET is_draft = 0, content = ? WHERE id = ?",
                        (accept_content, accept_node_id),
                    )

                    # Update active_path to include accepted node
                    story_rows = await db.execute_fetchall(
                        "SELECT story_id FROM nodes WHERE id = ?",
                        (accept_node_id,),
                    )
                    if story_rows:
                        sid = story_rows[0]["story_id"]
                        path_rows = await db.execute_fetchall(
                            "SELECT active_path FROM stories WHERE id = ?", (sid,)
                        )
                        current_path = (
                            json.loads(path_rows[0]["active_path"])
                            if path_rows[0]["active_path"]
                            else []
                        )
                        if accept_node_id not in current_path:
                            current_path.append(accept_node_id)

                        await db.execute(
                            "UPDATE stories SET active_path = ?, updated_at = datetime('now') WHERE id = ?",
                            (json.dumps(current_path), sid),
                        )

                    # Replace provenance spans
                    await db.execute(
                        "DELETE FROM provenance_spans WHERE node_id = ?",
                        (accept_node_id,),
                    )
                    for span in accept_spans:
                        span_id = uuid.uuid4().hex
                        await db.execute(
                            """INSERT INTO provenance_spans (id, node_id, start_offset, end_offset, source)
                               VALUES (?, ?, ?, ?, ?)""",
                            (
                                span_id,
                                accept_node_id,
                                span.get("start_offset", 0),
                                span.get("end_offset", 0),
                                span.get("source", "ai_generated"),
                            ),
                        )

                    await db.commit()

                current_draft_id = None
                await websocket.send_json(
                    {"type": "accepted", "node_id": accept_node_id}
                )

            elif msg_type == "reject":
                reject_node_id = msg["node_id"]

                async with get_db() as db:
                    # Delete the draft node (cascading delete removes spans)
                    await db.execute(
                        "DELETE FROM nodes WHERE id = ?", (reject_node_id,)
                    )
                    await db.commit()

                current_draft_id = None
                await websocket.send_json(
                    {"type": "rejected", "node_id": reject_node_id}
                )

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        pass
    except Exception:
        # Connection closed or other error — just clean up
        pass
