# LAND.E A Local AI Novel Drafting Environment

# Background
- I browse the Level1Techs forum, and came across an interesting project that aimed to replicate NovelAI 
- The original poster used ollama and made a notebook with some starter prompts to come up with a premise, an opening paragraph, and continuing the story with suggested scenarios
- I wanted to improve their prompting and make a demo ui

# Demo
- open running webapp
- Vibe Coded Tech Stack
  - Frontend: Svelte, Tailwind CSS, Vite
  - Backend: app server (Fastapi, Uvicorn), llm procesing (OpenAI, ollama, Pydantic)

# Improving prompting using structured outputs
- I felt they should use structured outputs, as it simplifies parsing out the llm generated text

## What are structured outputs?
- OpenAI defines structured outputs as:
  - > Structured Outputs is a feature that ensures the model will always generate responses that adhere to your supplied JSON Schema, so you don’t need to worry about the model omitting a required key, or hallucinating an invalid enum value.
- Benefits of structured outputs form openai
  > - **Reliable type-safety:** No need to validate or retry incorrectly formatted responses
  > - **Explicit refusals:** Safety-based model refusals are now programmatically detectable
  > - **Simpler prompting:** No need for strongly worded prompts to achieve consistent formatting
- See OpenAI documentation [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs)


## Why structured outputs?
1. Define your schema as python clases using Pydantic (makes it easier to update prompting).
2. Leverage Pydantic's validation functions to ensure a llm will generate a valid JSON that you can easily parse

## Converting their regex + code to my code

<table>
  <thead>
    <tr>
      <th style="width:50%; text-align:left;">Theirs</th>
      <th style="width:50%; text-align:left;">Mine</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Instructions</strong>
        <pre><code>
    You are a sharp, imaginative fiction writer. Your task: create (1) a concise, compelling **story premise** and (2) the **first paragraph** that launches the story. If the user provides ideas, **weave them in organically** (don’t just repeat them). If the user provides no ideas, **invent something fresh** with a surprising combination of genre, setting, protagonist, conflict, and twist.

    **Requirements**

    * Premise: 2–5 sentences, stakes + hook, no spoilers.
    * Opening paragraph: 120–180 words, vivid and concrete, minimal clichés, clear POV, grounded scene, ends with a soft hook.
    * Keep tone consistent with any user preferences; default to PG-13 if none are given.
    * Avoid copying user phrasing verbatim; enrich and reframe.
    * If user ideas conflict, choose one coherent direction and proceed.

    **Output format**
    Premise: <your premise>

    Opening paragraph: <your paragraph>

    # User

    Ideas (optional; may be empty): {{user_ideas}}

    Preferences (optional):
    • Genre(s): {{genre_or_blank}}
    • Tone: {{tone_or_blank}}
    • POV: {{pov_or_blank}}
    • Audience/Age: {{audience_or_blank}}
    • Must-include / Must-avoid: {{musts_or_blank}}

    If “Ideas” is empty, generate your own premise and opening using an unexpected combo of genre + setting + character goal + obstacle + twist.
</code></pre>
      </td>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Instructions</strong>
        <pre><code class="language-markdown">
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
</code></pre>
      </td>
    </tr>
    <tr>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Story continue prompt</strong>
        <pre><code>

            You are a skilled novelist. Your job is to continue the story from the given **premise** (and optional **previous text**) by writing the **next scene** that moves the plot meaningfully forward while preserving continuity of characters, tone, POV, tense, and world rules.

            # Directions

            1. **Parse & anchor continuity.** Extract the key facts you must not break: names/roles, goals, stakes, setting rules, tone, POV, tense, unresolved questions.
            2. **Propose a mini beat plan** (5–7 beats) for the next scene only. Aim for escalation, complication, or choice; no filler.
            3. **Write the scene**:

            * Length target: {{target_words|800-1200}} words.
            * Maintain {{pov|close third}} and {{tense|past}} unless told otherwise.
            * Strong verbs, concrete detail, show > tell; minimal clichés.
            * Use dialogue to reveal motive or conflict; avoid summary dumps.
            * End with a **soft cliff/turn** that naturally invites the next scene.
            1. Just write the follow up paragraph, nothing more
</code></pre>
      </td>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Story continue prompt</strong>
        <pre><code>

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
</code></pre>
      </td>
    </tr>
    <tr>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Story analysis prompt</strong>
        <pre><code>

    # System
    You are a story analyst. Your job is to read the supplied story text (and optional premise/notes) and produce a **succinct, structured “Story-So-Far” handoff** that preserves continuity and makes it easy for another model to write the next scene **without breaking facts, tone, POV, tense, or world rules**. Do **not** write new story prose.

    # Directions

    1. **Extract ground truth.** Pull only what’s on the page (or in the premise). No inventions. If something is unclear, flag it under “Ambiguities”.
    2. **Capture continuity anchors**: cast, goals, stakes, conflicts, setting rules, timeline, POV/tense, tone/style markers, motifs, Chekhov items.
    3. **Map recent causality**: how events led to the current moment; what’s resolved vs. unresolved.
    4. **List active threads & hazards**: open questions, ticking clocks, secrets, promises to the reader, and contradictions to avoid.
    5. **Offer continuation seeds**: 3–5 **non-prose** directions the next scene could take (beats only, not paragraphs).
    6. **Respect constraints**: rating, must-include/avoid, genre norms. Quote key lines **sparingly** only when essential for voice or facts.

    # Output format

    **Logline (1–2 sentences)** <concise premise recap>

    **Cast & relationships (bullets)**

    * <Name>: <role/goal/conflict>; ties to <others>

    **World/Rules (bullets)**

    * <magic/tech/social rules, geography, constraints>

    **POV/Tense/Tone**

    * POV: <e.g., close third on Mara>
    * Tense: <past/present>
    * Tone/Style: <e.g., wry, atmospheric; short sentences; present-tense interiority>

    **Timeline & Causality (5–8 bullets)**

    1. <key event → consequence>
    …

    **Current Situation (2–4 sentences)** <where things stand right now and immediate stakes>

    **Active Threads / Hooks (3–7 bullets)**

    * <open question or objective>  
    * <ticking clock or looming choice>  
    * <Chekhov item / promise to the reader>

    **Continuity Landmines (bullets)**

    * <facts not to break, e.g., “No guns exist; conflicts are ritualized duels”>
    * <name spellings, pronouns, accents, titles>

    **Ambiguities / Gaps (bullets)**

    * <unclear item and suggested safe assumption, if any>

    **Style DNA (bullets + 1–2 tiny quotes max, optional)**

    * <hallmarks of voice; rhythm; imagery types>
    * “<short quote if essential>”

    **Next-Scene Seeds (3–5 beat options, no prose)**

    * Option A: <1–3 beats>
    * Option B: <1–3 beats>
    * Option C: <1–3 beats>

</code></pre>
      </td>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Story Analysis prompt</strong>
        <pre><code>

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
</code></pre>
      </td>
    </tr>
    <tr>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>Supporting code to parse it out</strong>
        <pre><code>

        pattern = re.compile(r"""
        ^\s*
        \*\*(?P<label>[^*\n]+?)\*\*      # top-level bold section header
        \s*
        (?P<body>.*?)                    # everything in the section
        (?=
            ^\s*\*\*[^*\n]+?\*\*\s*      # next top-level bold section header
        | \Z                           # or end of string
        )
        """, flags=re.MULTILINE | re.DOTALL | re.VERBOSE)

        sections = {}

        for m in pattern.finditer(text):
            raw_label = m.group("label").strip()

            # remove trailing punctuation inside the bold header, e.g. "Logline:"
            label = re.sub(r"[\s:：\-—–]+$", "", raw_label)

            body = m.group("body").strip()
            sections[label] = body

        print(sections["Logline"])
        print(sections["Cast & relationships"])
        print(sections["World/Rules"])

</code></pre>
      </td>
      <td style="vertical-align:top; border:1px solid #ccc; padding:8px;">
        <strong>My code</strong>
        <pre><code>

        user_prompt = "let's create a new story no preferences just give me a idea"
        start = client.beta.chat.completions.parse(
            model=model,
            response_format=StoryStart,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Follow the response model docstring."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=2,
        ).choices[0].message.parsed
        start = StoryStart.model_validate(start)

        # 2) Continue (using premise + approved story-so-far text)
        story_so_far = f"Premise:\n{start.premise}\n\nOpening paragraph:\n{start.opening_paragraph}"
        cont = client.beta.chat.completions.parse(
            model=model,
            response_format=StoryContinue,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Follow the response model docstring."},
                {"role": "user", "content": story_so_far},
            ],
            temperature=0.2,
        ).choices[0].message.parsed
        cont = StoryContinue.model_validate(cont)

        # (User edits cont.next_paragraph if desired)

        # 3) Analyze (premise + opening + approved next paragraph)
        story_text = f"{start.opening_paragraph}\n\n{cont.next_paragraph}"
        analysis_input = f"Premise:\n{start.premise}\n\nStory text:\n{story_text}"
        analysis = client.beta.chat.completions.parse(
            model=model,
            response_format=StoryAnalysis,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Follow the response model docstring."},
                {"role": "user", "content": analysis_input},
            ],
            temperature=0.2,
        ).choices[0].message.parsed
        analysis = StoryAnalysis.model_validate(analysis)

        # 4) Continue again (using analysis summary instead of full text)
        cont2_input = (
            f"Premise:\n{start.premise}\n\n"
            f"Story analysis summary:\n{analysis.model_dump_json(indent=2)}"
        )
        cont2 = client.beta.chat.completions.parse(
            model=model,
            response_format=StoryContinue,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Follow the response model docstring."},
                {"role": "user", "content": cont2_input},
            ],
            temperature=0.2,
        ).choices[0].message.parsed
        cont2 = StoryContinue.model_validate(cont2)
</code></pre>
      </td>
    </tr>
  </tbody>
</table>


# Making a demo ui
- I made the initial draft in Marimo
  - ![](../../00-supporting-files/images/README/20251230052537.png)
- Then I had gsd, a vibecoding framework, create the frontend based off of my feedback and the marimo app. The backend was based off notebook explorations