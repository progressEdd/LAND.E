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


class StoryResponse(BaseModel):
    """Response model for a story with its nodes."""

    id: str
    title: str
    premise: str
    created_at: str
    updated_at: str
    active_path: Optional[list[str]] = None
    nodes: list[NodeResponse] = Field(default_factory=list)
