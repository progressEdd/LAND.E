"""REST API endpoints for cross-story character identity management."""

import json
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.models.database import get_db, normalize_character_name
from app.models.schemas import (
    CanonicalCharacterResponse,
    CanonicalCharacterSummary,
    CharacterAliasResponse,
    CharacterAppearanceResponse,
    CharacterCandidateGroup,
    CharacterMentionCandidate,
    LinkCharactersRequest,
    ManualLinkRequest,
    SplitCharactersRequest,
    UpdateCharacterRequest,
)


router = APIRouter(prefix="/api/characters", tags=["characters"])


# ---------- Response models ----------


class CandidatesResponse(BaseModel):
    """Response for auto-suggested character match candidates."""

    candidates: list[CharacterCandidateGroup] = Field(default_factory=list)


class SplitResponse(BaseModel):
    """Response after splitting a canonical character."""

    original: CanonicalCharacterSummary
    new: CanonicalCharacterSummary


# We need Field from pydantic
from pydantic import Field


# ---------- Helper functions ----------


async def _fetch_full_character(canonical_id: str) -> CanonicalCharacterResponse | None:
    """Fetch a full canonical character with aliases and appearances."""
    async with get_db() as db:
        char_rows = await db.execute_fetchall(
            "SELECT * FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        if not char_rows:
            return None

        char = char_rows[0]

        # Fetch aliases
        alias_rows = await db.execute_fetchall(
            "SELECT * FROM character_aliases WHERE canonical_id = ?", (canonical_id,)
        )
        aliases = [
            CharacterAliasResponse(
                id=r["id"],
                canonical_id=r["canonical_id"],
                story_id=r["story_id"],
                raw_name=r["raw_name"],
                normalized_name=r["normalized_name"],
                status=r["status"],
                role_in_story=r["role_in_story"],
            )
            for r in alias_rows
        ]

        # Fetch appearances with story titles
        appearance_rows = await db.execute_fetchall(
            """SELECT csa.*, s.title as story_title
               FROM character_story_appearances csa
               JOIN stories s ON csa.story_id = s.id
               WHERE csa.canonical_id = ?""",
            (canonical_id,),
        )
        appearances = [
            CharacterAppearanceResponse(
                story_id=r["story_id"],
                story_title=r["story_title"],
                role=r["role"],
                context=r["context"],
                arc_notes=r["arc_notes"],
            )
            for r in appearance_rows
        ]

        # Parse traits from JSON
        traits = json.loads(char["traits"]) if char["traits"] else []

        # Derive story_ids from appearances
        story_ids = list({a.story_id for a in appearances})

        return CanonicalCharacterResponse(
            id=char["id"],
            canonical_name=char["canonical_name"],
            description=char["description"],
            traits=traits,
            arc_summary=char["arc_summary"],
            aliases=aliases,
            appearances=appearances,
            story_ids=story_ids,
        )


async def _build_summary(canonical_id: str, db=None) -> CanonicalCharacterSummary:
    """Build a summary for a canonical character."""
    close_db = False
    if db is None:
        db_ctx = get_db()
        db = await db_ctx.__aenter__()
        close_db = True

    try:
        char_rows = await db.execute_fetchall(
            "SELECT * FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        if not char_rows:
            raise HTTPException(status_code=404, detail="Canonical character not found")

        char = char_rows[0]

        alias_rows = await db.execute_fetchall(
            "SELECT raw_name, story_id FROM character_aliases WHERE canonical_id = ?",
            (canonical_id,),
        )
        raw_names = [r["raw_name"] for r in alias_rows]
        story_ids = list({r["story_id"] for r in alias_rows})

        return CanonicalCharacterSummary(
            id=char["id"],
            canonical_name=char["canonical_name"],
            story_count=len(story_ids),
            story_ids=story_ids,
            raw_names=raw_names,
        )
    finally:
        if close_db:
            await db.close()


# ---------- Endpoints ----------


@router.get("/candidates", response_model=CandidatesResponse)
async def get_candidates():
    """Auto-suggest character match candidates by normalizing names across stories.

    Finds character names that, when normalized, match across 2+ different stories
    and are not already linked in character_aliases (confirmed/suggested status).
    """
    async with get_db() as db:
        # Get all distinct (character_name, story_id) pairs from character_mentions
        mention_rows = await db.execute_fetchall(
            """SELECT DISTINCT cm.character_name, n.story_id
               FROM character_mentions cm
               JOIN nodes n ON cm.node_id = n.id"""
        )

        # Get names already linked (confirmed or suggested)
        linked_rows = await db.execute_fetchall(
            """SELECT raw_name, story_id FROM character_aliases
               WHERE status IN ('confirmed', 'suggested')"""
        )
        linked_set = {(r["raw_name"], r["story_id"]) for r in linked_rows}

        # Filter out already-linked mentions
        unlinked = [
            (r["character_name"], r["story_id"])
            for r in mention_rows
            if (r["character_name"], r["story_id"]) not in linked_set
        ]

        # Group by normalized name
        from collections import defaultdict

        groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for raw_name, story_id in unlinked:
            norm = normalize_character_name(raw_name)
            groups[norm].append((raw_name, story_id))

        # Fetch story titles for building candidates
        story_rows = await db.execute_fetchall("SELECT id, title FROM stories")
        story_titles = {r["id"]: r["title"] for r in story_rows}

        # Only include groups with 2+ different stories
        candidates = []
        for norm_name, mentions in sorted(groups.items()):
            story_ids = list({sid for _, sid in mentions})
            if len(story_ids) >= 2:
                candidate_mentions = [
                    CharacterMentionCandidate(
                        raw_name=raw_name,
                        story_id=sid,
                        story_title=story_titles.get(sid, "Unknown"),
                    )
                    for raw_name, sid in mentions
                ]
                candidates.append(
                    CharacterCandidateGroup(
                        normalized_name=norm_name,
                        mentions=candidate_mentions,
                    )
                )

    return CandidatesResponse(candidates=candidates)


@router.post("/link", response_model=CanonicalCharacterResponse, status_code=201)
async def link_characters(req: LinkCharactersRequest):
    """Confirm a match group — create a canonical character and link mentions."""
    canonical_id = uuid.uuid4().hex

    async with get_db() as db:
        # Create canonical character
        await db.execute(
            """INSERT INTO canonical_characters (id, canonical_name)
               VALUES (?, ?)""",
            (canonical_id, req.canonical_name),
        )

        # Insert aliases and track unique story_ids
        seen_story_ids: set[str] = set()
        for mention in req.mentions:
            alias_id = uuid.uuid4().hex
            normalized = normalize_character_name(mention.raw_name)
            await db.execute(
                """INSERT INTO character_aliases (id, canonical_id, story_id, raw_name, normalized_name, status)
                   VALUES (?, ?, ?, ?, ?, 'confirmed')""",
                (alias_id, canonical_id, mention.story_id, mention.raw_name, normalized),
            )
            seen_story_ids.add(mention.story_id)

        # Create appearance records for each unique story
        for story_id in seen_story_ids:
            appearance_id = uuid.uuid4().hex
            await db.execute(
                """INSERT INTO character_story_appearances (id, canonical_id, story_id)
                   VALUES (?, ?, ?)""",
                (appearance_id, canonical_id, story_id),
            )

        await db.commit()

    result = await _fetch_full_character(canonical_id)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to create canonical character")
    return result


@router.post("/{canonical_id}/split", response_model=SplitResponse)
async def split_character(canonical_id: str, req: SplitCharactersRequest):
    """Split mentions from an existing canonical character into a new one."""
    new_canonical_id = uuid.uuid4().hex

    async with get_db() as db:
        # Verify original exists
        char_rows = await db.execute_fetchall(
            "SELECT id FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        if not char_rows:
            raise HTTPException(status_code=404, detail="Canonical character not found")

        # Create new canonical character with first raw_name as name
        new_name = req.mentions_to_split[0].raw_name
        new_name = normalize_character_name(new_name)
        await db.execute(
            """INSERT INTO canonical_characters (id, canonical_name)
               VALUES (?, ?)""",
            (new_canonical_id, new_name),
        )

        # Move specified aliases to new canonical
        for mention in req.mentions_to_split:
            await db.execute(
                """UPDATE character_aliases SET canonical_id = ?, status = 'confirmed'
                   WHERE canonical_id = ? AND raw_name = ? AND story_id = ?""",
                (new_canonical_id, canonical_id, mention.raw_name, mention.story_id),
            )

        # Update appearances: move split story_ids to new canonical where appropriate
        split_story_ids = {m.story_id for m in req.mentions_to_split}
        for story_id in split_story_ids:
            # Check if original canonical still has aliases in this story
            remaining = await db.execute_fetchall(
                """SELECT id FROM character_aliases
                   WHERE canonical_id = ? AND story_id = ?""",
                (canonical_id, story_id),
            )
            if not remaining:
                # Move appearance to new canonical
                await db.execute(
                    """UPDATE character_story_appearances SET canonical_id = ?
                       WHERE canonical_id = ? AND story_id = ?""",
                    (new_canonical_id, canonical_id, story_id),
                )
            else:
                # Create new appearance for new canonical
                appearance_id = uuid.uuid4().hex
                await db.execute(
                    """INSERT OR IGNORE INTO character_story_appearances (id, canonical_id, story_id)
                       VALUES (?, ?, ?)""",
                    (appearance_id, new_canonical_id, story_id),
                )

        # Check if original has any aliases left
        remaining_aliases = await db.execute_fetchall(
            "SELECT id FROM character_aliases WHERE canonical_id = ?", (canonical_id,)
        )
        if not remaining_aliases:
            await db.execute(
                "DELETE FROM canonical_characters WHERE id = ?", (canonical_id,)
            )

        await db.commit()

    original_summary = await _build_summary(canonical_id)
    new_summary = await _build_summary(new_canonical_id)
    return SplitResponse(original=original_summary, new=new_summary)


@router.get("", response_model=list[CanonicalCharacterSummary])
async def list_characters():
    """List all canonical characters with summary data."""
    async with get_db() as db:
        char_rows = await db.execute_fetchall(
            "SELECT id, canonical_name FROM canonical_characters ORDER BY canonical_name"
        )

        summaries = []
        for char in char_rows:
            summary = await _build_summary(char["id"], db=db)
            summaries.append(summary)

    return summaries


@router.get("/{canonical_id}", response_model=CanonicalCharacterResponse)
async def get_character(canonical_id: str):
    """Get full canonical character profile with aliases and appearances."""
    result = await _fetch_full_character(canonical_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Canonical character not found")
    return result


@router.patch("/{canonical_id}", response_model=CanonicalCharacterResponse)
async def update_character(canonical_id: str, req: UpdateCharacterRequest):
    """Edit a canonical character's profile."""
    async with get_db() as db:
        # Verify exists
        char_rows = await db.execute_fetchall(
            "SELECT id FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        if not char_rows:
            raise HTTPException(status_code=404, detail="Canonical character not found")

        # Build update query for non-None fields
        updates = []
        params = []
        if req.canonical_name is not None:
            updates.append("canonical_name = ?")
            params.append(req.canonical_name)
        if req.description is not None:
            updates.append("description = ?")
            params.append(req.description)
        if req.traits is not None:
            updates.append("traits = ?")
            params.append(json.dumps(req.traits))
        if req.arc_summary is not None:
            updates.append("arc_summary = ?")
            params.append(req.arc_summary)

        if updates:
            updates.append("updated_at = datetime('now')")
            params.append(canonical_id)
            await db.execute(
                f"UPDATE canonical_characters SET {', '.join(updates)} WHERE id = ?",
                tuple(params),
            )
            await db.commit()

    result = await _fetch_full_character(canonical_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Canonical character not found")
    return result


@router.post("/{canonical_id}/link-mention", response_model=CanonicalCharacterResponse)
async def link_mention(canonical_id: str, req: ManualLinkRequest):
    """Manually link a character mention to an existing canonical character."""
    async with get_db() as db:
        # Verify canonical exists
        char_rows = await db.execute_fetchall(
            "SELECT id FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        if not char_rows:
            raise HTTPException(status_code=404, detail="Canonical character not found")

        # Verify the (raw_name, story_id) exists in character_mentions
        mention_rows = await db.execute_fetchall(
            """SELECT cm.character_name FROM character_mentions cm
               JOIN nodes n ON cm.node_id = n.id
               WHERE cm.character_name = ? AND n.story_id = ?""",
            (req.raw_name, req.story_id),
        )
        if not mention_rows:
            raise HTTPException(
                status_code=400,
                detail=f"Character mention '{req.raw_name}' not found in story {req.story_id}",
            )

        # Insert alias
        alias_id = uuid.uuid4().hex
        normalized = normalize_character_name(req.raw_name)
        await db.execute(
            """INSERT INTO character_aliases (id, canonical_id, story_id, raw_name, normalized_name, status)
               VALUES (?, ?, ?, ?, ?, 'confirmed')""",
            (alias_id, canonical_id, req.story_id, req.raw_name, normalized),
        )

        # Upsert appearance
        appearance_id = uuid.uuid4().hex
        await db.execute(
            """INSERT OR IGNORE INTO character_story_appearances (id, canonical_id, story_id)
               VALUES (?, ?, ?)""",
            (appearance_id, canonical_id, req.story_id),
        )

        await db.commit()

    result = await _fetch_full_character(canonical_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Canonical character not found")
    return result


@router.delete("/{canonical_id}", status_code=204)
async def delete_character(canonical_id: str):
    """Remove a canonical character (cascades to aliases and appearances).

    Does NOT touch original character_mentions data.
    """
    async with get_db() as db:
        char_rows = await db.execute_fetchall(
            "SELECT id FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        if not char_rows:
            raise HTTPException(status_code=404, detail="Canonical character not found")

        await db.execute(
            "DELETE FROM canonical_characters WHERE id = ?", (canonical_id,)
        )
        await db.commit()

    return Response(status_code=204)
