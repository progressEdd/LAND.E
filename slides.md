---
marp: true
html: true
style: |
  section.fill-media {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    gap: 0.1rem;
    height: 100%;
    padding: 28px 36px;
    overflow: hidden;
    align-content: stretch;
    }

    section.fill-media h1,
    section.fill-media h2 {
    margin: 0 0 0.15rem 0;
    text-align: left;
    justify-self: start;
    align-self: start;
    width: 100%;
    line-height: 1.05;
    }

    section.fill-media .media-wrap {
    min-height: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;   /* horizontal centering */
    align-items: center;       /* vertical centering */
    overflow: hidden;
    }

    section.fill-media .media-wrap img,
    section.fill-media .media-wrap video {
    width: auto;
    height: 100%;              /* use all remaining height */
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    object-position: center center;
    display: block;
    }

    section.side-diff {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    gap: 0.35rem;
    padding: 28px 36px;
    box-sizing: border-box;
    height: 100%;
    overflow: hidden;
    align-content: stretch;
    }

    section.side-diff h1,
    section.side-diff h2 {
    margin: 0;
    text-align: left;
    justify-self: start;
    align-self: start;
    width: 100%;
    }

    section.side-diff h1 {
    font-size: 1rem;
    line-height: 1.4;
    padding-bottom: 0.06em;
    }

    section.side-diff .diff-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 0.5rem;
    width: 100%;
    height: 100%;
    min-height: 0;
    overflow: hidden;
    }

    section.side-diff .diff-panel {
    position: relative;
    border: 1px solid #999;
    border-radius: 8px;
    overflow: hidden;
    min-width: 0;
    min-height: 0;
    display: flex;
    flex-direction: column;
    background: #f7f8f9;
    }

    section.side-diff .diff-header {
    font-weight: 700;
    padding: 0.22rem 0.35rem;
    font-size: 0.34rem;
    flex: 0 0 auto;
    }

    section.side-diff .old .diff-header {
    background: #fbe4e6;
    color: #7a1f2b;
    }

    section.side-diff .new .diff-header {
    background: #e3f3e6;
    color: #1f5e2b;
    }

    section.side-diff pre {
    margin: 0;
    padding: 0.28rem 0.34rem 0.5rem 0.34rem;
    font-size: 0.33rem;
    line-height: 1.22;
    flex: 1 1 auto;
    min-height: 0;
    overflow-x: hidden;
    overflow-y: auto;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    word-break: break-word;
    scrollbar-gutter: stable;
    box-sizing: border-box;
    }

    section.side-diff .diff-panel::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 0.45rem;
    pointer-events: none;
    background: linear-gradient(
        to bottom,
        rgba(247, 248, 249, 0),
        rgba(247, 248, 249, 0.96)
    );
    }

    section.side-diff code {
    white-space: inherit;
    overflow-wrap: inherit;
    word-break: inherit;
    }

    section.side-diff .del,
    section.side-diff .add,
    section.side-diff .ctx {
    display: block;
    white-space: inherit;
    overflow-wrap: inherit;
    word-break: inherit;
    padding: 0.03em 0.14em;
    border-radius: 4px;
    color: #4b5563;
    }

    section.side-diff .del {
    background: #fdecee;
    }

    section.side-diff .add {
    background: #ebf7ee;
    }

    section.side-diff .ctx {
    background: transparent;
    }

    section.side-diff .diff-prefix {
    opacity: 0.75;
    color: inherit;
    }

    /* Python syntax highlighting inside diff lines */
    section.side-diff .del .tok-kw,
    section.side-diff .add .tok-kw,
    section.side-diff .ctx .tok-kw {
    color: #7c3aed !important;
    font-weight: 700;
    }

    section.side-diff .del .tok-builtin,
    section.side-diff .add .tok-builtin,
    section.side-diff .ctx .tok-builtin {
    color: #2563eb !important;
    }

    section.side-diff .del .tok-class,
    section.side-diff .add .tok-class,
    section.side-diff .ctx .tok-class {
    color: #0f766e !important;
    font-weight: 700;
    }

    section.side-diff .del .tok-name,
    section.side-diff .add .tok-name,
    section.side-diff .ctx .tok-name {
    color: #374151 !important;
    }

    section.side-diff .del .tok-str,
    section.side-diff .add .tok-str,
    section.side-diff .ctx .tok-str {
    color: #b45309 !important;
    }

    section.side-diff .del .tok-num,
    section.side-diff .add .tok-num,
    section.side-diff .ctx .tok-num {
    color: #c2410c !important;
    }

    section.side-diff .del .tok-cmt,
    section.side-diff .add .tok-cmt,
    section.side-diff .ctx .tok-cmt {
    color: #6b7280 !important;
    font-style: italic;
    }

    section.side-diff .del .tok-op,
    section.side-diff .add .tok-op,
    section.side-diff .ctx .tok-op {
    color: #111827 !important;
    }

  section.tweet-slide {
    display: flex;
    justify-content: center;
    align-items: stretch;
    padding: 8px 12px;
    background: #000;
  }

  section.tweet-slide h1 {
    display: none;
  }

  .tweet-card {
    width: 100%;
    max-width: 1160px;
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 10px 14px 10px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: auto 0;
  }

  .tweet-header {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .tweet-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6c63ff, #3b82f6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    color: #fff;
    flex-shrink: 0;
  }

  .tweet-user-info {
    display: flex;
    flex-direction: column;
    line-height: 1.3;
  }

  .tweet-display-name {
    font-weight: 700;
    font-size: 14px;
    color: #e7e9ea;
  }

  .tweet-handle {
    font-size: 12px;
    color: #71767b;
  }

  .tweet-verified {
    display: inline-block;
    width: 18px;
    height: 18px;
    background: #1d9bf0;
    border-radius: 50%;
    color: #fff;
    font-size: 11px;
    font-weight: 900;
    text-align: center;
    line-height: 18px;
    margin-left: 4px;
    vertical-align: middle;
  }

  .tweet-labels {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 4px;
    font-size: 16px;
    color: #e7e9ea;
    font-weight: 400;
    line-height: 1;
    text-align: left;
    padding: 0 0 2px;
  }

  .tweet-photos {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 4px;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #2a2a4a;
    flex: 1 1 auto;
    min-height: 0;
  }

  .tweet-photo {
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #111;
    min-height: 0;
  }

  .tweet-photo.started {
    padding: 40px;
    box-sizing: border-box;
  }

  .tweet-photo.started img {
    width: 100%;
    height: 100%;
    object-fit: scale-down;
    object-position: center center;
    display: block;
  }

  .tweet-photo.going img {
    width: 130%;
    height: 130%;
    object-fit: scale-down;
    object-position: center center;
    display: block;
  }


  section.flow-slide {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 64px;
  }

  section.flow-slide h2 {
    margin-bottom: 48px;
  }

  .flow-images {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: center;
    justify-items: center;
    column-gap: 36px;
    width: 100%;
  }

  .flow-captions {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    justify-items: center;
    column-gap: 36px;
    width: 100%;
    margin-top: 18px;
  }

  .flow-logo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 240px;
    height: 240px;
  }

  .flow-logo {
    max-width: 220px;
    max-height: 220px;
    width: auto;
    height: auto;
    object-fit: contain;
    display: block;
  }

  .flow-arrow {
    font-size: 56px;
    font-weight: 700;
    line-height: 1;
    opacity: 0.85;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .flow-caption {
    font-size: 28px;
    font-weight: 600;
    text-align: center;
    line-height: 1.2;
  }

  .flow-empty {
    visibility: hidden;
  }
  
   section.vs-slide {
    padding: 0;
    overflow: hidden;
    background: #000;
  }

  section.vs-slide .vs-wrap {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #000;
  }

  /* Left / right halves */
  section.vs-slide .vs-side {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 50%;
    overflow: hidden;
    background: #02040a;
  }

  section.vs-slide .vs-side.left {
    left: 0;
  }

  section.vs-slide .vs-side.right {
    right: 0;
  }

  /* Top angled header bar */
  section.vs-slide .vs-topbar {
    position: absolute;
    top: 0;
    height: 78px;
    width: 100%;
    background: #020612;
    z-index: 4;
  }

  section.vs-slide .vs-side.left .vs-topbar {
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0 84%);
  }

  section.vs-slide .vs-side.right .vs-topbar {
    clip-path: polygon(0 0, 100% 0, 100% 84%, 0 100%);
  }

  /* Main image area */
  section.vs-slide .vs-image {
    position: absolute;
    top: 60px;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1;
  }

  section.vs-slide .vs-image img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    object-position: center center;
  }

  /* Color overlays to make it feel more like the reference */
  section.vs-slide .vs-side.left::after,
  section.vs-slide .vs-side.right::after {
    content: "";
    position: absolute;
    inset: 60px 0 0 0;
    z-index: 2;
    pointer-events: none;
  }

  section.vs-slide .vs-side.left::after {
    background:
      linear-gradient(to bottom, rgba(255, 70, 55, 0.16), rgba(0,0,0,0) 28%),
      linear-gradient(to top, rgba(95, 0, 0, 0.42), rgba(0,0,0,0) 35%);
    mix-blend-mode: screen;
  }

  section.vs-slide .vs-side.right::after {
    background:
      linear-gradient(to bottom, rgba(80, 140, 255, 0.16), rgba(0,0,0,0) 28%),
      linear-gradient(to top, rgba(0, 60, 110, 0.40), rgba(0,0,0,0) 35%);
    mix-blend-mode: screen;
  }

  /* Corner player labels */
  section.vs-slide .vs-player {
    position: absolute;
    top: 10px;
    z-index: 6;
    font-size: 0.42rem;
    font-style: italic;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 0.01em;
    text-shadow: 0 2px 8px rgba(0,0,0,0.45);
  }

  section.vs-slide .vs-side.left .vs-player {
    left: 12px;
    color: #ff4b4b;
  }

  section.vs-slide .vs-side.right .vs-player {
    left: 12px;
    color: #4d88ff;
  }

  /* Big names at top */
  section.vs-slide .vs-name {
    position: absolute;
    top: 6px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 6;
    margin: 0;
    color: #fff;
    font-size: 0.92rem;
    font-weight: 900;
    letter-spacing: 0.02em;
    line-height: 1;
    text-transform: uppercase;
    text-shadow: 0 3px 10px rgba(0,0,0,0.45);
    white-space: nowrap;
  }

  /* Optional small tag under top bar */
  section.vs-slide .vs-tag {
    position: absolute;
    top: 86px;
    left: 0;
    z-index: 6;
    font-size: 0.28rem;
    font-weight: 700;
    color: #fff;
    padding: 0.12rem 0.34rem;
    text-transform: none;
  }

  section.vs-slide .vs-side.left .vs-tag {
    background: linear-gradient(90deg, rgba(255,95,95,0.95), rgba(255,95,95,0.72));
  }

  section.vs-slide .vs-side.right .vs-tag {
    background: linear-gradient(90deg, rgba(70,140,255,0.95), rgba(70,140,255,0.72));
  }

  /* Center divider */
  section.vs-slide .vs-divider {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    width: 4px;
    transform: translateX(-50%);
    z-index: 7;
    background: linear-gradient(
      to bottom,
      rgba(90,130,255,0.00) 0%,
      rgba(132,108,255,0.85) 18%,
      rgba(130,160,255,1.0) 50%,
      rgba(132,108,255,0.85) 82%,
      rgba(90,130,255,0.00) 100%
    );
    box-shadow:
      0 0 12px rgba(130,160,255,0.75),
      0 0 28px rgba(130,160,255,0.45);
  }

  /* Big center VS */
  section.vs-slide .vs-center {
    position: absolute;
    left: 50%;
    top: 58%;
    transform: translate(-50%, -50%);
    z-index: 8;
    color: #fff;
    font-size: 1.35rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.03em;
    text-shadow:
      0 0 10px rgba(255,255,255,0.55),
      0 3px 18px rgba(0,0,0,0.55);
  }

  /* Optional lower glow / particles vibe */
  section.vs-slide .vs-glow {
    position: absolute;
    left: 50%;
    bottom: 0;
    transform: translateX(-50%);
    width: 280px;
    height: 160px;
    z-index: 3;
    pointer-events: none;
    background: radial-gradient(
      ellipse at center,
      rgba(120,160,255,0.28) 0%,
      rgba(120,160,255,0.10) 35%,
      rgba(0,0,0,0) 75%
    );
    filter: blur(8px);
  }

  /* If your source images need different framing, tweak here */
  section.vs-slide .vs-side.left .vs-image img {
    object-position: center center;
  }

  section.vs-slide .vs-side.right .vs-image img {
  object-position: 00% center;
  }
  
---


# LAND.E a Local AI Drafting Environment
## Edd's vibecoding adventure

---

<!-- _class: fill-media -->
# 
<div class="media-wrap">
  <video autoplay muted loop playsinline>
    <source src="00-supporting-files/images/slides/Im-Troy-Mcclure.mp4" type="video/mp4" />
  </video>
</div>

--- 

<!-- _class: fill-media -->

<div class="media-wrap">
  <img src="00-supporting-files/images/slides/20260427235754.png" />
</div>

---

<!-- _class: fill-media -->

<div class="media-wrap">
  <img src="00-supporting-files/images/slides/20260427093122.png" />
</div>

---
<!-- _class: tweet-slide -->

# How it Started

<div class="tweet-card">
  <div class="tweet-header">
    <div class="tweet-avatar">E</div>
    <div class="tweet-user-info">
      <span class="tweet-display-name">Edd</span>
      <span class="tweet-handle">@progressEdd · 2h</span>
    </div>`
  </div>
  <div class="tweet-labels">
    <span>how it started</span>
    <span>how it's going</span>
  </div>
  <div class="tweet-photos">
    <div class="tweet-photo started">
      <img src="00-supporting-files/images/slides/20260427231910.png" />
    </div>
    <div class="tweet-photo going">
      <img src="00-supporting-files/images/slides/20260427231840.png" />
    </div>
  </div>
</div>

---
<!-- _class: fill-media -->
# 
<div class="media-wrap">
  <img src="00-supporting-files/images/slides/structured-outputs.png" />
</div>

---
# Improving Prompting Using Structured Outputs
- What are Structured Outputs?
  - > Structured Outputs is a feature that ensures the model will always generate responses that adhere to your supplied JSON Schema, so you don’t need to worry about the model omitting a required key, or hallucinating an invalid enum value.
- Why Structured Outputs?
  - Easier Prompting
  - Easier Parsing

---
<!-- _class: side-diff --> 
## Story Premise
<div class="diff-grid"> <div class="diff-panel old"> <div class="diff-header">Theirs</div> <pre><code><span class="del"><span class="diff-prefix">- </span>You are a sharp, imaginative fiction writer. Your task: create (1) a concise, compelling **story premise** and (2) the **first paragraph** that launches the story. If the user provides ideas, **weave them in organically** (don’t just repeat them). If the user provides no ideas, **invent something fresh** with a surprising combination of genre, setting, protagonist, conflict, and twist.</span><span class="del"><span class="diff-prefix">- </span>**Requirements**</span><span class="del"><span class="diff-prefix">- </span>* Premise: 2–5 sentences, stakes + hook, no spoilers.</span><span class="del"><span class="diff-prefix">- </span>* Opening paragraph: 120–180 words, vivid and concrete, minimal clichés, clear POV, grounded scene, ends with a soft hook.</span><span class="del"><span class="diff-prefix">- </span>* Keep tone consistent with any user preferences; default to PG-13 if none are given.</span><span class="del"><span class="diff-prefix">- </span>* Avoid copying user phrasing verbatim; enrich and reframe.</span><span class="del"><span class="diff-prefix">- </span>* If user ideas conflict, choose one coherent direction and proceed.</span><span class="del"><span class="diff-prefix">- </span>**Output format**</span><span class="del"><span class="diff-prefix">- </span>Premise: &lt;your premise&gt;</span><span class="del"><span class="diff-prefix">- </span>Opening paragraph: &lt;your paragraph&gt;</span><span class="del"><span class="diff-prefix">- </span># User</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>Ideas (optional; may be empty): {{user_ideas}}</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>Preferences (optional):</span><span class="del"><span class="diff-prefix">- </span>• Genre(s): {{genre_or_blank}}</span><span class="del"><span class="diff-prefix">- </span>• Tone: {{tone_or_blank}}</span><span class="del"><span class="diff-prefix">- </span>• POV: {{pov_or_blank}}</span><span class="del"><span class="diff-prefix">- </span>• Audience/Age: {{audience_or_blank}}</span><span class="del"><span class="diff-prefix">- </span>• Must-include / Must-avoid: {{musts_or_blank}}</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>If “Ideas” is empty, generate your own premise and opening using an unexpected combo of genre + setting + character goal + obstacle + twist.</span></code></pre> </div> <div class="diff-panel new"> <div class="diff-header">Mine</div> <pre><code><span class="add"><span class="diff-prefix">+ </span><span class="tok-kw">class</span> <span class="tok-class">StoryStart</span><span class="tok-op">(</span><span class="tok-class">BaseModel</span><span class="tok-op">)</span><span class="tok-op">:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str">&quot;&quot;&quot;</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> You are a sharp, imaginative fiction writer.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Task:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Produce (1) a concise, compelling _story _premise and (2) the opening paragraph that launches the _story.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Rules:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - If the user provides ideas, weave them in organically (don&#x27;t just repeat them).</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - If the user provides no ideas, invent something fresh with a surprising combination of</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> genre, setting, protagonist, conflict, and twist.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - premise: 2–5 sentences, stakes + hook, no spoilers.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Opening paragraph: 120–180 words, vivid and concrete, minimal clichés, clear POV,</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> grounded scene, ends with a soft hook.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Tone should follow user preferences; default to PG-13 if none are given.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Avoid copying user phrasing verbatim; enrich and reframe.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - If user ideas conflict, choose one coherent direction and proceed.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Output only fields that match this schema.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> &quot;&quot;&quot;</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">premise</span><span class="tok-op">:</span> <span class="tok-builtin">str</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span><span class="tok-op">...</span><span class="tok-op">,</span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;2–5 sentences. Stakes + hook, no spoilers.&quot;</span><span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">opening_paragraph</span><span class="tok-op">:</span> <span class="tok-builtin">str</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">...</span><span class="tok-op">,</span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;120–180 words. Vivid, grounded, ends with a soft hook.&quot;</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span></code></pre> </div> </div>

---

<!-- _class: side-diff --> 
## Story Analysis
<div class="diff-grid"> <div class="diff-panel old"> <div class="diff-header">Theirs</div> <pre><code><span class="del"><span class="diff-prefix">- </span># System</span><span class="del"><span class="diff-prefix">- </span>You are a story analyst. Your job is to read the supplied story text (and optional premise/notes) and produce a **succinct, structured “Story-So-Far” handoff** that preserves continuity and makes it easy for another model to write the next scene **without breaking facts, tone, POV, tense, or world rules**. Do **not** write new story prose.</span><span class="del"><span class="diff-prefix">- </span># Directions</span><span class="del"><span class="diff-prefix">- </span>1. **Extract ground truth.** Pull only what’s on the page (or in the premise). No inventions. If something is unclear, flag it under “Ambiguities”.</span><span class="del"><span class="diff-prefix">- </span>2. **Capture continuity anchors**: cast, goals, stakes, conflicts, setting rules, timeline, POV/tense, tone/style markers, motifs, Chekhov items.</span><span class="del"><span class="diff-prefix">- </span>3. **Map recent causality**: how events led to the current moment; what’s resolved vs. unresolved.</span><span class="del"><span class="diff-prefix">- </span>4. **List active threads &amp; hazards**: open questions, ticking clocks, secrets, promises to the reader, and contradictions to avoid.</span><span class="del"><span class="diff-prefix">- </span>5. **Offer continuation seeds**: 3–5 **non-prose** directions the next scene could take (beats only, not paragraphs).</span><span class="del"><span class="diff-prefix">- </span>6. **Respect constraints**: rating, must-include/avoid, genre norms. Quote key lines **sparingly** only when essential for voice or facts.</span><span class="del"><span class="diff-prefix">- </span># Output format</span><span class="del"><span class="diff-prefix">- </span>**Logline (1–2 sentences)** &lt;concise premise recap&gt;</span><span class="del"><span class="diff-prefix">- </span>**Cast &amp; relationships (bullets)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* &lt;Name&gt;: &lt;role/goal/conflict&gt;; ties to &lt;others&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**World/Rules (bullets)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* &lt;magic/tech/social rules, geography, constraints&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**POV/Tense/Tone**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* POV: &lt;e.g., close third on Mara&gt;</span><span class="del"><span class="diff-prefix">- </span>* Tense: &lt;past/present&gt;</span><span class="del"><span class="diff-prefix">- </span>* Tone/Style: &lt;e.g., wry, atmospheric; short sentences; present-tense interiority&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Timeline &amp; Causality (5–8 bullets)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>1. &lt;key event → consequence&gt;</span><span class="del"><span class="diff-prefix">- </span>…</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Current Situation (2–4 sentences)** &lt;where things stand right now and immediate stakes&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Active Threads / Hooks (3–7 bullets)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* &lt;open question or objective&gt; </span><span class="del"><span class="diff-prefix">- </span>* &lt;ticking clock or looming choice&gt; </span><span class="del"><span class="diff-prefix">- </span>* &lt;Chekhov item / promise to the reader&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Continuity Landmines (bullets)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* &lt;facts not to break, e.g., “No guns exist; conflicts are ritualized duels”&gt;</span><span class="del"><span class="diff-prefix">- </span>* &lt;name spellings, pronouns, accents, titles&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Ambiguities / Gaps (bullets)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* &lt;unclear item and suggested safe assumption, if any&gt;</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Style DNA (bullets + 1–2 tiny quotes max, optional)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* &lt;hallmarks of voice; rhythm; imagery types&gt;</span><span class="del"><span class="diff-prefix">- </span>* “&lt;short quote if essential&gt;”</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>**Next-Scene Seeds (3–5 beat options, no prose)**</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>* Option A: &lt;1–3 beats&gt;</span><span class="del"><span class="diff-prefix">- </span>* Option B: &lt;1–3 beats&gt;</span><span class="del"><span class="diff-prefix">- </span>* Option C: &lt;1–3 beats&gt;</span></code></pre> </div> <div class="diff-panel new"> <div class="diff-header">Mine</div> <pre><code><span class="add"><span class="diff-prefix">+ </span><span class="tok-kw">class</span> <span class="tok-class">StoryAnalysis</span><span class="tok-op">(</span><span class="tok-class">BaseModel</span><span class="tok-op">)</span><span class="tok-op">:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str">&quot;&quot;&quot;</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> You are a _story analyst. Produce a succinct &quot;_story-So-Far&quot; handoff so another model can write</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> the next paragraph without breaking continuity. Do not write new _story prose.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Inputs:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - You will be given the _story _premise and the _story text so far (opening paragraph + one or more continuation paragraphs).</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Rules:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Extract ground truth only from the provided text/_premise. No inventions.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Capture continuity anchors: cast, goals, stakes, conflicts, setting rules, POV/tense,</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> tone/style markers, motifs, and notable objects.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Map causality and current situation.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - List active threads/hazards: open questions, ticking clocks, contradictions to avoid.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Provide 3–5 next-paragraph seeds as beats only (no prose paragraphs).</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Output only fields that match this schema.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> &quot;&quot;&quot;</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">logline</span><span class="tok-op">:</span> <span class="tok-builtin">str</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">cast</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">default_factory</span><span class="tok-op">=</span><span class="tok-builtin">list</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;Bullets: Name — role/goal/conflict; ties.&quot;</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">world_rules</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">default_factory</span><span class="tok-op">=</span><span class="tok-builtin">list</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;Bullets: constraints/rules implied by text.&quot;</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">pov_tense_tone</span><span class="tok-op">:</span> <span class="tok-builtin">str</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">...</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;Compact string for POV, tense, and tone/style markers.&quot;</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">timeline</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">default_factory</span><span class="tok-op">=</span><span class="tok-builtin">list</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;Bullets: key event → consequence.&quot;</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">current_situation</span><span class="tok-op">:</span> <span class="tok-builtin">str</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">active_threads</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span><span class="tok-name">default_factory</span><span class="tok-op">=</span><span class="tok-builtin">list</span><span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">continuity_landmines</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span><span class="tok-name">default_factory</span><span class="tok-op">=</span><span class="tok-builtin">list</span><span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">ambiguities</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span><span class="tok-name">default_factory</span><span class="tok-op">=</span><span class="tok-builtin">list</span><span class="tok-op">)</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">next_paragraph_seeds</span><span class="tok-op">:</span> <span class="tok-builtin">list</span><span class="tok-op">[</span><span class="tok-builtin">str</span><span class="tok-op">]</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">...</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">min_length</span><span class="tok-op">=</span><span class="tok-num">3</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">max_length</span><span class="tok-op">=</span><span class="tok-num">5</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;Beats-only options, no prose.&quot;</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span></code></pre> </div> </div>

---
<!-- _class: side-diff --> 
## Story Continue 
<div class="diff-grid"> <div class="diff-panel old"> <div class="diff-header">Theirs</div> <pre><code><span class="del"><span class="diff-prefix">- </span>You are a skilled novelist. Your job is to continue the story from the given **premise** (and optional **previous text**) by writing the **next scene** that moves the plot meaningfully forward while preserving continuity of characters, tone, POV, tense, and world rules.</span><span class="del"><span class="diff-prefix">- </span># Directions</span><span class="del"><span class="diff-prefix">- </span>1. **Parse &amp; anchor continuity.** Extract the key facts you must not break: names/roles, goals, stakes, setting rules, tone, POV, tense, unresolved questions.</span><span class="del"><span class="diff-prefix">- </span>2. **Propose a mini beat plan** (5–7 beats) for the next scene only. Aim for escalation, complication, or choice; no filler.</span><span class="del"><span class="diff-prefix">- </span>3. **Write the scene**:</span><span class="del"><span class="diff-prefix">- </span>* Length target: {{target_words|800-1200}} words.</span><span class="del"><span class="diff-prefix">- </span>* Maintain {{pov|close third}} and {{tense|past}} unless told otherwise.</span><span class="del"><span class="diff-prefix">- </span>* Strong verbs, concrete detail, show &gt; tell; minimal clichés.</span><span class="del"><span class="diff-prefix">- </span>* Use dialogue to reveal motive or conflict; avoid summary dumps.</span><span class="del"><span class="diff-prefix">- </span>* End with a **soft cliff/turn** that naturally invites the next scene.</span><span class="del"><span class="diff-prefix">- </span>1. Just write the follow up paragraph, nothing more</span></code></pre> </div> <div class="diff-panel new"> <div class="diff-header">Mine</div> <pre><code><span class="add"><span class="diff-prefix">+ </span><span class="tok-kw">class</span> <span class="tok-class">StoryContinue</span><span class="tok-op">(</span><span class="tok-class">BaseModel</span><span class="tok-op">)</span><span class="tok-op">:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str">&quot;&quot;&quot;</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> You are a skilled novelist. Write the next paragraph only.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Inputs:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - You will be given the _story _premise and the _story-so-far (either the opening paragraph + latest paragraph,</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> or a compact analysis summary). Use them to preserve continuity.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Rules:</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Output exactly one paragraph of _story prose (no headings, no bullets, no analysis).</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Preserve continuity: characters, tone, POV, tense, world rules.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Length target: ~120–200 words unless told otherwise.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Concrete detail, strong verbs, show &gt; tell; minimal clichés.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - Dialogue (if any) should reveal motive or conflict; avoid summary dumps.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> - End with a soft hook/turn that invites the next paragraph.</span></span><span class="add"><span class="diff-prefix">+ </span>&nbsp;</span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> Output only fields that match this schema.</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-str"> &quot;&quot;&quot;</span></span><span class="add"><span class="diff-prefix">+ </span>&nbsp;</span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-name">next_paragraph</span><span class="tok-op">:</span> <span class="tok-builtin">str</span> <span class="tok-op">=</span> <span class="tok-class">Field</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">...</span><span class="tok-op">,</span> <span class="tok-name">description</span><span class="tok-op">=</span><span class="tok-str">&quot;Exactly one paragraph of continuation prose.&quot;</span></span><span class="add"><span class="diff-prefix">+ </span> <span class="tok-op">)</span></span></code></pre> </div> </div>

---



<!-- _class: side-diff -->

## Supporting Code

<div class="diff-grid">
  <div class="diff-panel old">
    <div class="diff-header">Theirs</div>
    <pre><code><span class="del"><span class="diff-prefix">- </span>pattern = re.compile(r&quot;&quot;&quot;</span><span class="del"><span class="diff-prefix">- </span>^\s*</span><span class="del"><span class="diff-prefix">- </span>\*\*(?P&lt;label&gt;[^*\n]+?)\*\*      # top-level bold section header</span><span class="del"><span class="diff-prefix">- </span>\s*</span><span class="del"><span class="diff-prefix">- </span>(?P&lt;body&gt;.*?)                    # everything in the section</span><span class="del"><span class="diff-prefix">- </span>(?=</span><span class="del"><span class="diff-prefix">- </span>    ^\s*\*\*[^*\n]+?\*\*\s*      # next top-level bold section header</span><span class="del"><span class="diff-prefix">- </span>| \Z                           # or end of string</span><span class="del"><span class="diff-prefix">- </span>)</span><span class="del"><span class="diff-prefix">- </span>&quot;&quot;&quot;, flags=re.MULTILINE | re.DOTALL | re.VERBOSE)</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>sections = {}</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>for m in pattern.finditer(text):</span><span class="del"><span class="diff-prefix">- </span>    raw_label = m.group(&quot;label&quot;).strip()</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>    # remove trailing punctuation inside the bold header, e.g. &quot;Logline:&quot;</span><span class="del"><span class="diff-prefix">- </span>    label = re.sub(r&quot;[\s:：\-—–]+$&quot;, &quot;&quot;, raw_label)</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>    body = m.group(&quot;body&quot;).strip()</span><span class="del"><span class="diff-prefix">- </span>    sections[label] = body</span><span class="del"><span class="diff-prefix">- </span>&nbsp;</span><span class="del"><span class="diff-prefix">- </span>print(sections[&quot;Logline&quot;])</span><span class="del"><span class="diff-prefix">- </span>print(sections[&quot;Cast &amp; relationships&quot;])</span><span class="del"><span class="diff-prefix">- </span>print(sections[&quot;World/Rules&quot;])</span></code></pre>
  </div>

  <div class="diff-panel new">
    <div class="diff-header">Mine</div>
    <pre><code><span class="add"><span class="diff-prefix">+ </span><span class="tok-cmt"># 3) Analyze (premise + opening + approved next paragraph)</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-name">story_text</span> <span class="tok-op">=</span> f&quot;<span class="tok-op">{</span><span class="tok-name">start</span><span class="tok-op">.</span><span class="tok-name">opening_paragraph</span><span class="tok-op">}</span>\n\n<span class="tok-op">{</span><span class="tok-name">cont</span><span class="tok-op">.</span><span class="tok-name">next_paragraph</span><span class="tok-op">}</span>&quot;</span><span class="add"><span class="diff-prefix">+ </span><span class="tok-name">analysis_input</span> <span class="tok-op">=</span> f&quot;Premise:\n<span class="tok-op">{</span><span class="tok-name">start</span><span class="tok-op">.</span><span class="tok-name">premise</span><span class="tok-op">}</span>\n\nStory text:\n<span class="tok-op">{</span><span class="tok-name">story_text</span><span class="tok-op">}</span>&quot;</span><span class="add"><span class="diff-prefix">+ </span><span class="tok-name">analysis</span> <span class="tok-op">=</span> <span class="tok-name">client</span><span class="tok-op">.</span><span class="tok-name">beta</span><span class="tok-op">.</span><span class="tok-name">chat</span><span class="tok-op">.</span><span class="tok-name">completions</span><span class="tok-op">.</span><span class="tok-name">parse</span><span class="tok-op">(</span></span><span class="add"><span class="diff-prefix">+ </span>    <span class="tok-name">model</span><span class="tok-op">=</span><span class="tok-name">model</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span>    <span class="tok-name">response_format</span><span class="tok-op">=</span><span class="tok-class">StoryAnalysis</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span>    <span class="tok-name">messages</span><span class="tok-op">=</span><span class="tok-op">[</span></span><span class="add"><span class="diff-prefix">+ </span>        <span class="tok-op">{</span><span class="tok-str">&quot;role&quot;</span><span class="tok-op">:</span> <span class="tok-str">&quot;system&quot;</span><span class="tok-op">,</span> <span class="tok-str">&quot;content&quot;</span><span class="tok-op">:</span> <span class="tok-str">&quot;You are a helpful assistant. Follow the response model docstring.&quot;</span><span class="tok-op">}</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span>        <span class="tok-op">{</span><span class="tok-str">&quot;role&quot;</span><span class="tok-op">:</span> <span class="tok-str">&quot;user&quot;</span><span class="tok-op">,</span> <span class="tok-str">&quot;content&quot;</span><span class="tok-op">:</span> <span class="tok-name">analysis_input</span><span class="tok-op">}</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span>    <span class="tok-op">]</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span>    <span class="tok-name">temperature</span><span class="tok-op">=</span><span class="tok-num">0.2</span><span class="tok-op">,</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-op">)</span><span class="tok-op">.</span><span class="tok-name">choices</span><span class="tok-op">[</span><span class="tok-num">0</span><span class="tok-op">]</span><span class="tok-op">.</span><span class="tok-name">message</span><span class="tok-op">.</span><span class="tok-name">parsed</span></span><span class="add"><span class="diff-prefix">+ </span><span class="tok-name">analysis</span> <span class="tok-op">=</span> <span class="tok-class">StoryAnalysis</span><span class="tok-op">.</span><span class="tok-name">model_validate</span><span class="tok-op">(</span><span class="tok-name">analysis</span><span class="tok-op">)</span></span></code></pre>
  </div>
</div>

---

# Vibecoding Tips & Tricks
---

<!-- _class: fill-media -->

## 

<div class="media-wrap">
  <video autoplay muted loop playsinline>
    <source src="00-supporting-files/images/slides/spongebob-patrick.mp4" type="video/mp4" />
  </video>
</div>

---
<!-- _class: fill-media -->

<div class="media-wrap">
  <img src="00-supporting-files/images/slides/Evolution.png" />
</div>

<!-- <div class="media-wrap">
  <img src="00-supporting-files/images/slides/Evolution.png" />
</div> -->

---
<!-- _class: flow-slide -->

## Current Setup

<div class="flow-images">
  <div class="flow-logo-wrap">
    <img class="flow-logo" src="00-supporting-files/images/slides/zai-logo.svg" />
  </div>

  <div class="flow-arrow">→</div>

  <div class="flow-logo-wrap">
    <img class="flow-logo" src="00-supporting-files/images/slides/pi-logo-loop-true-vector.svg" />
  </div>

  <div class="flow-arrow">→</div>

  <div class="flow-logo-wrap">
    <img class="flow-logo" src="00-supporting-files/images/slides/gsd-logo-2000.svg" />
  </div>
</div>

<div class="flow-captions">
  <div class="flow-caption">Zai<br />GLM Coding Plan</div>
  <div class="flow-empty">.</div>
  <div class="flow-caption">Pi<br />Coding Harness</div>
  <div class="flow-empty">.</div>
  <div class="flow-caption">GSD<br />Vibecoding Framework</div>
</div>

---

<!-- _class: fill-media -->

## Recommendations For model endpoints
<div class="media-wrap">
  <img src="00-supporting-files/images/slides/3-paths.png" />
</div>

---

<!-- _class: vs-slide -->

<div class="vs-wrap">
  <div class="vs-side left">
    <div class="vs-topbar"></div>
    <div class="vs-player">P1</div>
    <div class="vs-name">Agent Mode</div>
    <div class="vs-tag">GitHub Copilot</div>
    <div class="vs-image">
      <img src="00-supporting-files/images/slides/copilot-agent-dropdown.png" alt="Copilot agent dropdown" />
    </div>
  </div>

  <div class="vs-side right">
    <div class="vs-topbar"></div>
    <div class="vs-player">P2</div>
    <div class="vs-name">Vibecoding Frameworks</div>
    <div class="vs-tag">Terminal</div>
    <div class="vs-image">
      <img src="00-supporting-files/images/slides/terminal.svg" alt="Terminal" />
    </div>
  </div>

  <div class="vs-glow"></div>
  <div class="vs-divider"></div>
  <div class="vs-center">VS</div>
</div>

---
<!-- _class: fill-media -->

# 
<div class="media-wrap">
  <video autoplay muted loop playsinline>
    <source src="00-supporting-files/images/slides/yu-gi-oh-yugi-muto.mp4" type="video/mp4" />
  </video>
</div>

---
# Summary
- You got exposed to an app I vibecoded
- You learned about my vibecoding setup and workflow

---
# Thanks!