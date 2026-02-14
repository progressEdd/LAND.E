"""Markdown export service for stories."""

import json
from datetime import datetime, timezone

from app.models.database import get_db


async def export_story_markdown(story_id: str) -> str:
    """Export a story as a markdown document by walking the active path.

    Loads the story title, premise, and active_path from SQLite, then
    fetches each node along the path and concatenates their content
    into a formatted markdown document.

    Args:
        story_id: The UUID hex string of the story to export.

    Returns:
        A complete markdown string ready for download.

    Raises:
        ValueError: If the story is not found.
    """
    async with get_db() as db:
        # Load story
        story_rows = await db.execute_fetchall(
            "SELECT * FROM stories WHERE id = ?", (story_id,)
        )
        if not story_rows:
            raise ValueError(f"Story not found: {story_id}")

        story = story_rows[0]
        title = story["title"]
        premise = story["premise"]
        active_path_raw = story["active_path"]

        # Parse active_path
        active_path: list[str] = []
        if active_path_raw:
            try:
                active_path = json.loads(active_path_raw)
            except (json.JSONDecodeError, TypeError):
                active_path = []

        # Build markdown header
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        parts: list[str] = [
            f"# {title}",
            "",
            f"> **Premise:** {premise}",
            "",
            "---",
            "",
        ]

        if active_path:
            # Fetch nodes along the active path in order
            placeholders = ", ".join("?" for _ in active_path)
            node_rows = await db.execute_fetchall(
                f"SELECT id, content FROM nodes WHERE id IN ({placeholders})",
                tuple(active_path),
            )

            # Build a lookup map and emit in path order
            node_map = {row["id"]: row["content"] for row in node_rows}
            for node_id in active_path:
                content = node_map.get(node_id)
                if content:
                    parts.append(content)
                    parts.append("")  # blank line between paragraphs
        else:
            # No active path — just export the premise
            parts.append(premise)
            parts.append("")

        parts.extend(
            [
                "---",
                "",
                f"*Exported from AI Invasion on {now}*",
            ]
        )

        return "\n".join(parts)
