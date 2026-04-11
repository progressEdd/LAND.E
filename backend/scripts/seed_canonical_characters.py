"""One-shot migration: create canonical characters from all existing character_mentions.

Groups mentions by normalized name, creates one canonical character per group
with confirmed aliases and appearance records.
"""
import asyncio
import sqlite3
import uuid
import re
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "stories.db"


def normalize_character_name(raw_name: str) -> str:
    colon_match = re.match(r'^([^:]+):\s', raw_name)
    if colon_match:
        raw_name = colon_match.group(1).strip()
    name = re.sub(r'\s*\([^)]*\)', '', raw_name).strip()
    name = re.sub(r'^(The|A|An)\s+', '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'\s+', ' ', name)
    return name


def seed():
    print(f"DB: {DB_PATH}")
    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row

    # Get all (character_name, story_id) pairs from character_mentions
    rows = con.execute("""
        SELECT DISTINCT cm.character_name, n.story_id
        FROM character_mentions cm
        JOIN nodes n ON cm.node_id = n.id
    """).fetchall()

    # Group by normalized name
    groups: dict[str, list[tuple[str, str]]] = {}  # norm_name -> [(raw_name, story_id)]
    for r in rows:
        norm = normalize_character_name(r["character_name"])
        if norm not in groups:
            groups[norm] = []
        groups[norm].append((r["character_name"], r["story_id"]))

    print(f"\nFound {len(groups)} character groups:\n")

    cur = con.cursor()
    created = 0

    for norm_name, mentions in sorted(groups.items()):
        story_ids = sorted({sid for _, sid in mentions})
        unique_raw_names = sorted({rn for rn, _ in mentions})
        print(f"  {norm_name}")
        print(f"    raw names: {unique_raw_names}")
        print(f"    stories:   {len(story_ids)}")

        canonical_id = uuid.uuid4().hex

        # Create canonical character
        cur.execute(
            "INSERT INTO canonical_characters (id, canonical_name) VALUES (?, ?)",
            (canonical_id, norm_name),
        )

        # Create aliases for each unique (raw_name, story_id) pair
        for raw_name, story_id in mentions:
            alias_id = uuid.uuid4().hex
            normalized = normalize_character_name(raw_name)
            cur.execute(
                """INSERT OR IGNORE INTO character_aliases
                   (id, canonical_id, story_id, raw_name, normalized_name, status)
                   VALUES (?, ?, ?, ?, ?, 'confirmed')""",
                (alias_id, canonical_id, story_id, raw_name, normalized),
            )

        # Create appearance records per story
        for story_id in story_ids:
            appearance_id = uuid.uuid4().hex
            cur.execute(
                """INSERT OR IGNORE INTO character_story_appearances
                   (id, canonical_id, story_id) VALUES (?, ?, ?)""",
                (appearance_id, canonical_id, story_id),
            )

        created += 1

    con.commit()
    con.close()
    print(f"\n✓ Created {created} canonical characters")


if __name__ == "__main__":
    seed()
