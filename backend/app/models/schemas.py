"""Pydantic schemas for story structures, LLM config, and API request/response models."""

from typing import Optional

from pydantic import BaseModel, Field


class StoryStart(BaseModel):
    """
    You are a sharp, imaginative fiction writer.

    Task:
    - Produce (1) a concise, compelling _story _premise and (2) the opening paragraph that launches the _story.

    Rules:
    - If the user provides ideas, weave them in organically (don't just repeat them).
    - If the user provides no ideas, invent something fresh with a surprising combination of
      genre, setting, protagonist, conflict, and twist.
    - premise: 2–5 sentences, stakes + hook, no spoilers.
    - Opening paragraph: 120–180 words, vivid and concrete, minimal clichés, clear POV,
      grounded scene, ends with a soft hook.
    - Tone should follow user preferences; default to PG-13 if none are given.
    - Avoid copying user phrasing verbatim; enrich and reframe.
    - If user ideas conflict, choose one coherent direction and proceed.

    Output only fields that match this schema.
    """

    premise: str = Field(..., description="2–5 sentences. Stakes + hook, no spoilers.")
    opening_paragraph: str = Field(
        ..., description="120–180 words. Vivid, grounded, ends with a soft hook."
    )


class StoryContinue(BaseModel):
    """
    You are a skilled novelist. Write the next paragraph only.

    Inputs:
    - You will be given the _story _premise and the _story-so-far (either the opening paragraph + latest paragraph,
      or a compact analysis summary). Use them to preserve continuity.

    Rules:
    - Output exactly one paragraph of _story prose (no headings, no bullets, no analysis).
    - Preserve continuity: characters, tone, POV, tense, world rules.
    - Length target: ~120–200 words unless told otherwise.
    - Concrete detail, strong verbs, show > tell; minimal clichés.
    - Dialogue (if any) should reveal motive or conflict; avoid summary dumps.
    - End with a soft hook/turn that invites the next paragraph.

    Output only fields that match this schema.
    """

    next_paragraph: str = Field(
        ..., description="Exactly one paragraph of continuation prose."
    )


class StoryAnalysis(BaseModel):
    """
    You are a _story analyst. Produce a succinct "_story-So-Far" handoff so another model can write
    the next paragraph without breaking continuity. Do not write new _story prose.

    Inputs:
    - You will be given the _story _premise and the _story text so far (opening paragraph + one or more continuation paragraphs).

    Rules:
    - Extract ground truth only from the provided text/_premise. No inventions.
    - Capture continuity anchors: cast, goals, stakes, conflicts, setting rules, POV/tense,
      tone/style markers, motifs, and notable objects.
    - Map causality and current situation.
    - List active threads/hazards: open questions, ticking clocks, contradictions to avoid.
    - Provide 3–5 next-paragraph seeds as beats only (no prose paragraphs).

    Output only fields that match this schema.
    """

    logline: str
    cast: list[str] = Field(
        default_factory=list,
        description="Bullets: Name — role/goal/conflict; ties.",
    )
    world_rules: list[str] = Field(
        default_factory=list,
        description="Bullets: constraints/rules implied by text.",
    )
    pov_tense_tone: str = Field(
        ...,
        description="Compact string for POV, tense, and tone/style markers.",
    )
    timeline: list[str] = Field(
        default_factory=list,
        description="Bullets: key event → consequence.",
    )
    current_situation: str
    active_threads: list[str] = Field(default_factory=list)
    continuity_landmines: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    next_paragraph_seeds: list[str] = Field(
        ...,
        min_length=3,
        max_length=5,
        description="Beats-only options, no prose.",
    )


class LLMBackendConfig(BaseModel):
    """Configuration for LLM backend connection."""

    backend: str = "lmstudio"  # "lmstudio" | "ollama" | "openai" | "llamacpp"
    base_url: Optional[str] = None
    host: Optional[str] = None
    api_key: Optional[str] = None


class StoryCreateRequest(BaseModel):
    """Request body for creating a new story."""

    title: str
    premise: str


class ProvenanceSpanResponse(BaseModel):
    """Response model for a provenance span."""

    start_offset: int
    end_offset: int
    source: str


class NodeResponse(BaseModel):
    """Response model for a single story node."""

    id: str
    story_id: str
    parent_id: Optional[str] = None
    position: int
    content: str
    node_type: str
    source: str
    is_draft: bool
    created_at: str
    provenance_spans: list[ProvenanceSpanResponse] = Field(default_factory=list)
    character_mentions: list["CharacterMentionResponse"] = Field(default_factory=list)
    analysis: Optional[StoryAnalysis] = None


class StoryResponse(BaseModel):
    """Response model for a story with its nodes."""

    id: str
    title: str
    premise: str
    created_at: str
    updated_at: str
    active_path: Optional[list[str]] = None
    nodes: list[NodeResponse] = Field(default_factory=list)


# ---------- Graph support models ----------


class CharacterMentionResponse(BaseModel):
    """Response model for a character mention linked to a node."""

    character_name: str
    role: Optional[str] = None


class CharacterSummary(BaseModel):
    """Aggregated character data for supernode rendering in the graph."""

    name: str
    node_ids: list[str] = Field(default_factory=list)


class TreeNodeResponse(BaseModel):
    """A node in the tree structure with recursive children."""

    id: str
    story_id: str
    parent_id: Optional[str] = None
    position: int
    content: str
    node_type: str
    source: str
    is_draft: bool
    created_at: str
    provenance_spans: list[ProvenanceSpanResponse] = Field(default_factory=list)
    character_mentions: list[CharacterMentionResponse] = Field(default_factory=list)
    analysis: Optional[StoryAnalysis] = None
    children: list["TreeNodeResponse"] = Field(default_factory=list)


class TreeResponse(BaseModel):
    """Full tree structure for the graph visualizer."""

    story_id: str
    title: str
    premise: str
    active_path: list[str] = Field(default_factory=list)
    root: Optional[TreeNodeResponse] = None
    characters: list[CharacterSummary] = Field(default_factory=list)


class SwitchPathRequest(BaseModel):
    """Request body for switching the active path to a different branch."""

    target_node_id: str


# ---------- Dashboard overview models ----------


class StoryOverviewStory(BaseModel):
    """A story in the overview, with aggregated character names and node count."""
    id: str
    title: str
    premise: str
    created_at: str
    updated_at: str
    character_names: list[str] = Field(default_factory=list)
    node_count: int = 0


class StoryOverviewCharacter(BaseModel):
    """A character appearing across stories, with the story IDs it appears in."""
    name: str
    story_ids: list[str] = Field(default_factory=list)


class StoryOverviewResponse(BaseModel):
    """Full overview response for the dashboard graph and cards."""
    stories: list[StoryOverviewStory] = Field(default_factory=list)
    characters: list[StoryOverviewCharacter] = Field(default_factory=list)


# ---------- Cross-story character identity models ----------


class CharacterAliasResponse(BaseModel):
    """Response model for a character alias (per-story name mapping)."""
    id: str
    canonical_id: str
    story_id: str
    raw_name: str
    normalized_name: str
    status: str = Field(..., description="One of: suggested, confirmed, split, rejected")
    role_in_story: Optional[str] = None


class CharacterAppearanceResponse(BaseModel):
    """Response model for a canonical character's appearance in a story."""
    story_id: str
    story_title: str
    role: Optional[str] = None
    context: Optional[str] = None
    arc_notes: Optional[str] = None


class CanonicalCharacterResponse(BaseModel):
    """Full response for a canonical character with aliases and appearances."""
    id: str
    canonical_name: str
    description: Optional[str] = None
    traits: list[str] = Field(default_factory=list)
    arc_summary: Optional[str] = None
    aliases: list[CharacterAliasResponse] = Field(default_factory=list)
    appearances: list[CharacterAppearanceResponse] = Field(default_factory=list)
    story_ids: list[str] = Field(default_factory=list)


class CanonicalCharacterSummary(BaseModel):
    """Summary of a canonical character for list views."""
    id: str
    canonical_name: str
    story_count: int = 0
    story_ids: list[str] = Field(default_factory=list)
    raw_names: list[str] = Field(default_factory=list)


class CharacterMentionCandidate(BaseModel):
    """A single character mention found across stories."""
    raw_name: str
    story_id: str
    story_title: str


class CharacterCandidateGroup(BaseModel):
    """A group of character mentions that may be the same canonical character."""
    normalized_name: str
    mentions: list[CharacterMentionCandidate] = Field(default_factory=list)


class LinkMention(BaseModel):
    """A reference to a character mention in a specific story."""
    raw_name: str
    story_id: str


class LinkCharactersRequest(BaseModel):
    """Request to link multiple character mentions as the same canonical character."""
    canonical_name: str
    mentions: list[LinkMention] = Field(..., min_length=2, description="At least 2 mentions to link")


class SplitCharactersRequest(BaseModel):
    """Request to split mentions from an existing canonical character into a new one."""
    canonical_id: str
    mentions_to_split: list[LinkMention] = Field(..., min_length=1, description="Mentions to move to a new canonical character")


class UpdateCharacterRequest(BaseModel):
    """Request to update a canonical character's profile."""
    canonical_name: Optional[str] = None
    description: Optional[str] = None
    traits: Optional[list[str]] = None
    arc_summary: Optional[str] = None


class ManualLinkRequest(BaseModel):
    """Request to manually link a character mention to an existing canonical character."""
    raw_name: str
    story_id: str
    canonical_id: str
