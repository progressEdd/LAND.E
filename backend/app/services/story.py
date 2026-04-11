"""Story generation pipeline — orchestrates analysis and continuation.

Ported from 02-worktrees/demo-marimo-app/app.py lines 697-735.
"""

from dataclasses import dataclass

from openai import OpenAI

from app.models.schemas import StoryAnalysis, StoryContinue
from app.services.llm import parse_structured


@dataclass
class CycleResult:
    """Result of a single generation cycle: analysis + draft continuation."""

    draft_next: str
    analysis: StoryAnalysis


def extract_characters(cast: list) -> list[tuple[str, str | None]]:
    """Extract character names and roles from StoryAnalysis.cast entries.

    With the structured CastMember model, the LLM already outputs clean
    (name, role) pairs. This function just converts them to the format
    expected by the character_mentions table.

    Returns deduplicated list of (character_name, role) tuples.
    """
    seen: set[str] = set()
    results: list[tuple[str, str | None]] = []

    for member in cast:
        name = member.name.strip()
        role = member.role.strip() or None

        # Deduplicate by normalized name (case-insensitive)
        name_lower = name.lower()
        if name_lower not in seen and name:
            seen.add(name_lower)
            results.append((name, role))

    return results


async def run_cycle(
    client: OpenAI,
    *,
    model: str,
    premise: str,
    story_text: str,
    seed: str | None = None,
    temperature_continue: float = 0.2,
    temperature_analyze: float = 0.2,
) -> CycleResult:
    """Run a full generation cycle: analyze story, then generate next paragraph.

    Ported from app.py run_cycle() (lines 701-734), made async.

    1. Analyze the story so far (StoryAnalysis) to extract continuity anchors.
    2. Use the analysis summary to generate the next paragraph (StoryContinue).
    3. Return CycleResult with the draft text and analysis.

    If *seed* is provided, it is injected as a directional hint into the
    continuation prompt so the LLM steers toward that story beat.
    """
    # Analyze (premise + approved story text)
    analysis_input = f"Premise:\n{premise}\n\nStory text:\n{story_text}"
    analysis = await parse_structured(
        client,
        model=model,
        schema=StoryAnalysis,
        user_content=analysis_input,
        temperature=temperature_analyze,
    )

    # Continue (use analysis summary, optionally guided by a seed)
    seed_hint = f"\n\nDirectional seed (follow this beat):\n{seed}" if seed else ""
    cont_input = (
        f"Premise:\n{premise}\n\n"
        f"Story analysis summary:\n{analysis.model_dump_json(indent=2)}\n\n"
        f"Write the next paragraph.{seed_hint}"
    )
    continuation = await parse_structured(
        client,
        model=model,
        schema=StoryContinue,
        user_content=cont_input,
        temperature=temperature_continue,
    )

    return CycleResult(
        draft_next=(continuation.next_paragraph or "").strip(),
        analysis=analysis,
    )
