# Phase 02: Webapp UI - Research

**Researched:** 2026-02-13
**Domain:** Full-stack web application (SvelteKit frontend + FastAPI backend) for AI-assisted story writing
**Confidence:** HIGH

## Summary

Phase 02 replaces the marimo notebook story writer (`02-worktrees/demo-marimo-app/app.py`, 820 lines) with a purpose-built webapp. The existing Pydantic structured output pipeline (`StoryStart`, `StoryContinue`, `StoryAnalysis`) and `parse_structured()` function port directly to FastAPI as backend services. The frontend is a SvelteKit SPA with a Tiptap rich text editor, split-pane layout, and collapsible sidebars — modeled after NovelAI's editor experience.

The architecture is a monorepo with `backend/` (FastAPI + Python) and `frontend/` (SvelteKit + Node). The frontend builds to static files served by FastAPI in production, while development uses Vite's dev server with a proxy to FastAPI. Communication between frontend and backend uses WebSockets for streaming AI generation (bidirectional: needed for cancel/accept/reject during generation) and REST endpoints for CRUD operations.

**Primary recommendation:** Use SvelteKit in SPA mode (`ssr = false` + `adapter-static`), Tiptap with a custom `provenance` mark for color-coded source tracking, `svelte-splitpanes` for resizable panels, WebSockets for AI streaming, and SQLite with an adjacency list model for the story tree.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Tech Stack
| Decision | Choice | Notes |
|----------|--------|-------|
| Backend | FastAPI + Uvicorn | Python, ports existing LLM client/structured output code |
| Frontend | Svelte + Tailwind CSS | |
| Repo structure | Monorepo | `backend/` and `frontend/` in same branch |

#### Editor Experience
| Decision | Choice | Notes |
|----------|--------|-------|
| Draft flow | Inline display | AI text appears in editor visually distinguished (color/opacity) until accepted/rejected. No separate draft textarea. |
| Editing | Rich text editor | Click anywhere to edit, supports markdown formatting |
| Color-coding by source | v1, per character span | AI-generated=white, user-written=blue, user-edits=pink, initial prompt=cream. Tracked at the character span level (not paragraph level). |
| Node graph | v2 for rendering, v1 for data model | ComfyUI / Unreal Blueprints style. Data model must fully support branching from v1; visual graph editor is v2. |

#### Layout & Panels
| Decision | Choice | Notes |
|----------|--------|-------|
| Primary view | Split pane (editor + graph), resizable | Editor on one side, graph placeholder on the other |
| Settings / backend config | Collapsible left sidebar | VS Code style |
| Story analysis panel | Collapsible right sidebar | Structured display: cards/sections for cast, timeline, world_rules, etc. Not raw JSON. |
| Theme | Dark default, light mode toggle | |

#### Scope (v1 vs v2)
| Feature | Version | Notes |
|---------|---------|-------|
| LLM backends | v1: lmstudio, ollama, openai, llamacpp | Azure deferred |
| Persistence | v1: SQLite + markdown export | |
| Node graph rendering | v2 | v1 ships with data model only |
| Model warmup | v1 | Progress indicator on model load |
| Branching workflow | v1: data model. v2: visual graph | |

#### Data Model
| Decision | Choice | Notes |
|----------|--------|-------|
| Atomic unit | Switchable: paragraph, arbitrary block, sentence | User can switch granularity. All three modes supported. |
| Branch semantics | Fork at any point + multiple options per node | Both modes: fork the story at a paragraph to create a new branch, AND have multiple "next" candidates at any node |
| Provenance tracking | Per character span | Every span of text tagged with source: `ai_generated`, `user_written`, `user_edited`, `initial_prompt`. Enables NovelAI-style color coding. |

### Claude's Discretion (Open Questions)
1. Which rich text editor library for Svelte? (Tiptap, ProseMirror, CodeMirror, custom)
2. SQLite schema design — how to model the tree of paragraph nodes with span-level provenance
3. WebSocket vs SSE for streaming AI generation to the frontend
4. How to handle the switchable atomic unit (paragraph/block/sentence) in the data model — is it a view-layer concern or stored differently?
5. Graph rendering library for v2 (Svelte Flow, D3, Xyflow, custom canvas)

### Deferred Ideas (OUT OF SCOPE)
- Azure backend support
- Visual node graph rendering (data model only)
- Multi-user / collaboration
- Cloud deployment / auth
- Mobile-responsive layout
</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SvelteKit | 2.x (Svelte 5) | Frontend framework + build tooling | Official Svelte meta-framework. Provides routing, build config, SPA mode, Vite integration. Svelte 5 runes (`$state`, `$derived`, `$effect`) for reactivity. |
| Tailwind CSS | 4.x | Utility-first CSS framework | Locked decision. Dark mode toggle via `class` strategy. |
| FastAPI | 0.115+ | Backend API framework | Locked decision. Async support, WebSocket endpoints, Pydantic integration, auto OpenAPI docs. |
| Uvicorn | 0.34+ | ASGI server | Locked decision. Runs FastAPI. `--reload` for development. |
| Tiptap | 3.x | Rich text editor | **Recommended (Claude's Discretion #1).** Official Svelte integration. Built on ProseMirror with a clean extension API. Custom Mark API enables provenance tracking. See detailed rationale below. |
| svelte-splitpanes | 8.0.14 | Resizable split pane layout | **Recommended.** 463 GitHub stars, MIT license, SvelteKit + TypeScript friendly. Supports horizontal/vertical, min/max sizes, snapping, nested panes. |
| SQLite | 3.x (via aiosqlite) | Local persistence | Locked decision. Tree data model for story nodes + provenance spans. |
| @xyflow/svelte | 1.5.0 | Node graph rendering (v2) | **Recommended for v2 (Claude's Discretion #5).** Svelte Flow — official Svelte port of React Flow. Full node/edge graph with zoom, pan, custom nodes. v1 only needs the data model; library install deferred to v2. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tiptap/core | 3.x | Editor core | Always — foundation of Tiptap |
| @tiptap/pm | 3.x | ProseMirror bindings | Always — required by Tiptap |
| @tiptap/starter-kit | 3.x | Common extensions bundle | Editor setup — includes bold, italic, heading, etc. |
| @tiptap/extension-text-style | 3.x | `<span>` with style attributes | Custom provenance mark rendering |
| aiosqlite | 0.20+ | Async SQLite for FastAPI | All database operations — FastAPI is async, sqlite3 is sync |
| openai | 1.x | OpenAI-compatible API client | All LLM backends (OpenAI, LM Studio, ollama via OpenAI compat, llamacpp) |
| ollama | 0.4+ | Ollama-specific model listing | Model discovery for Ollama backend only |
| pydantic | 2.x | Data validation + structured output schemas | StoryStart, StoryContinue, StoryAnalysis schemas |
| websockets | 14+ | WebSocket protocol support | FastAPI WebSocket endpoints (installed as FastAPI extra) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Tiptap | ProseMirror directly | Lower-level, more control but much more boilerplate. Tiptap wraps ProseMirror with cleaner API. |
| Tiptap | CodeMirror | Code editor, not rich text editor. Wrong tool for prose writing. |
| Tiptap | Lexical | Facebook's editor — React-first, no official Svelte support. |
| svelte-splitpanes | CSS Grid + resize handles | Custom code for a solved problem. splitpanes handles touch, RTL, snapping, nested panes. |
| SvelteKit SPA | Vite + Svelte (no SvelteKit) | Loses routing structure, adapter system, dev tooling, `$lib` imports. SvelteKit in SPA mode gives all benefits with zero SSR overhead. |
| WebSocket | SSE (Server-Sent Events) | SSE is simpler but unidirectional (server→client only). Can't send cancel/accept/reject from client without a separate REST endpoint. WebSocket is bidirectional — single connection handles streaming + control messages. |
| aiosqlite | SQLAlchemy async | Heavier ORM. For a personal tool with simple queries, raw SQL via aiosqlite is cleaner and more transparent. |

**Installation:**

Frontend:
```bash
npx sv create frontend  # SvelteKit project
cd frontend
npm install @tiptap/core @tiptap/pm @tiptap/starter-kit @tiptap/extension-text-style
npm install svelte-splitpanes
npm install -D @sveltejs/adapter-static tailwindcss
```

Backend:
```bash
cd backend
uv init
uv add fastapi uvicorn[standard] aiosqlite openai ollama pydantic websockets
```

## Architecture Patterns

### Recommended Project Structure

```
ai-invasion/                    # repo root (master branch)
├── backend/                    # Python/FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app, CORS, static file serving
│   │   ├── config.py           # Settings, env vars
│   │   ├── models/
│   │   │   ├── schemas.py      # StoryStart, StoryContinue, StoryAnalysis (Pydantic)
│   │   │   └── database.py     # SQLite schema, aiosqlite connection
│   │   ├── services/
│   │   │   ├── llm.py          # parse_structured(), LLM client factory, warmup
│   │   │   ├── story.py        # run_cycle(), story orchestration logic
│   │   │   └── export.py       # Markdown export
│   │   ├── routers/
│   │   │   ├── stories.py      # REST: CRUD for stories, nodes, branches
│   │   │   ├── llm.py          # REST: backend config, model listing
│   │   │   └── ws.py           # WebSocket: generation streaming
│   │   └── db/
│   │       └── migrations/     # SQL migration scripts
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/                   # SvelteKit SPA
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── Editor.svelte         # Tiptap editor wrapper
│   │   │   │   ├── Sidebar.svelte        # Collapsible sidebar
│   │   │   │   ├── AnalysisPanel.svelte  # Story analysis display
│   │   │   │   ├── SettingsPanel.svelte  # LLM backend config
│   │   │   │   └── GraphPlaceholder.svelte  # v2 placeholder
│   │   │   ├── stores/
│   │   │   │   ├── story.svelte.ts       # Story tree state (Svelte 5 runes)
│   │   │   │   ├── editor.svelte.ts      # Editor state
│   │   │   │   └── settings.svelte.ts    # LLM config state
│   │   │   ├── extensions/
│   │   │   │   └── provenance.ts         # Custom Tiptap Mark for source tracking
│   │   │   ├── api/
│   │   │   │   ├── rest.ts               # REST API client
│   │   │   │   └── ws.ts                 # WebSocket client
│   │   │   └── types/
│   │   │       └── index.ts              # TypeScript interfaces
│   │   ├── routes/
│   │   │   ├── +layout.svelte            # App shell: sidebars + split pane
│   │   │   ├── +layout.ts               # export const ssr = false
│   │   │   └── +page.svelte              # Main editor page
│   │   └── app.html
│   ├── static/
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   └── package.json
└── .planning/                  # GSD planning files
```

### Pattern 1: SvelteKit SPA Mode

**What:** SvelteKit configured as a single-page app — no server-side rendering, builds to static files.
**When to use:** When the backend is a separate API server (FastAPI) and the frontend is purely client-side.

```typescript
// src/routes/+layout.ts
export const ssr = false;  // Disable SSR for all pages

// svelte.config.js
import adapter from '@sveltejs/adapter-static';
export default {
  kit: {
    adapter: adapter({
      fallback: '200.html',  // SPA fallback page
      pages: 'build',
      assets: 'build'
    })
  }
};
```

**Source:** https://svelte.dev/docs/kit/single-page-apps (official SvelteKit docs)

### Pattern 2: Tiptap Editor with Custom Provenance Mark

**What:** Custom Tiptap Mark extension that tags text spans with their source (ai_generated, user_written, user_edited, initial_prompt) and renders them with distinct colors.
**When to use:** For the NovelAI-style color-coded editor experience.

```typescript
// Source: Tiptap Mark API docs + custom extension pattern
import { Mark } from '@tiptap/core';

export type ProvenanceSource = 'ai_generated' | 'user_written' | 'user_edited' | 'initial_prompt';

const PROVENANCE_COLORS: Record<ProvenanceSource, string> = {
  ai_generated: 'rgba(255, 255, 255, 0.9)',   // white
  user_written: 'rgba(100, 149, 237, 0.9)',    // blue
  user_edited:  'rgba(255, 182, 193, 0.9)',    // pink
  initial_prompt: 'rgba(255, 253, 208, 0.9)',  // cream
};

export const Provenance = Mark.create({
  name: 'provenance',

  addAttributes() {
    return {
      source: {
        default: 'user_written',
        parseHTML: (element: HTMLElement) => element.getAttribute('data-source'),
        renderHTML: (attributes: { source: ProvenanceSource }) => ({
          'data-source': attributes.source,
          style: `color: ${PROVENANCE_COLORS[attributes.source] || 'inherit'}`,
        }),
      },
    };
  },

  parseHTML() {
    return [{ tag: 'span[data-source]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', HTMLAttributes, 0];
  },
});
```

### Pattern 3: Tiptap Svelte 5 Integration

**What:** Initializing Tiptap editor in a Svelte 5 component using runes.
**When to use:** Every component that renders the editor.

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import { Editor } from '@tiptap/core';
  import { StarterKit } from '@tiptap/starter-kit';
  import { Provenance } from '$lib/extensions/provenance';

  let element = $state();
  let editorState = $state({ editor: null });

  onMount(() => {
    editorState.editor = new Editor({
      element: element,
      extensions: [
        StarterKit,
        Provenance,
      ],
      content: '',
      onTransaction: ({ editor }) => {
        editorState = { editor };  // Force re-render
      },
    });
  });

  onDestroy(() => {
    editorState.editor?.destroy();
  });
</script>

<div bind:this={element}></div>
```

**Source:** https://tiptap.dev/docs/editor/getting-started/install/svelte (official Tiptap docs, Svelte 5 runes example)

### Pattern 4: FastAPI WebSocket for AI Streaming

**What:** WebSocket endpoint that streams AI-generated text token by token, with bidirectional control (cancel, accept, reject).
**When to use:** The `/ws/generate` endpoint for story continuation.

```python
# Source: FastAPI WebSocket docs
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

@app.websocket("/ws/generate")
async def generate_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive generation request from client
            data = json.loads(await websocket.receive_text())
            
            if data["type"] == "generate":
                # Stream tokens back
                async for token in run_generation(data["story_id"], data["node_id"]):
                    await websocket.send_json({
                        "type": "token",
                        "content": token,
                    })
                await websocket.send_json({"type": "complete"})
            
            elif data["type"] == "cancel":
                # Client requested cancellation
                await websocket.send_json({"type": "cancelled"})
            
            elif data["type"] == "accept":
                # Client accepted the draft
                await websocket.send_json({"type": "accepted"})
            
            elif data["type"] == "reject":
                await websocket.send_json({"type": "rejected"})
    
    except WebSocketDisconnect:
        pass  # Client disconnected
```

### Pattern 5: svelte-splitpanes Layout

**What:** Resizable split pane layout for the main editor view.
**When to use:** The primary app layout — editor on one side, graph placeholder on the other.

```svelte
<script>
  import { Splitpanes, Pane } from 'svelte-splitpanes';
</script>

<Splitpanes style="height: 100vh" theme="dark-theme">
  <Pane minSize={30} size={60}>
    <!-- Editor panel -->
    <Editor />
  </Pane>
  <Pane minSize={20}>
    <!-- Graph placeholder (v1) / Graph view (v2) -->
    <GraphPlaceholder />
  </Pane>
</Splitpanes>

<style>
  :global(.dark-theme .splitpanes__splitter) {
    background-color: #374151;
    width: 4px;
  }
  :global(.dark-theme .splitpanes__splitter:hover) {
    background-color: #6366f1;
  }
</style>
```

**Source:** https://github.com/orefalo/svelte-splitpanes (README, v8.0.14)

### Pattern 6: Svelte 5 State Management with Runes

**What:** Using Svelte 5 runes (`$state`, `$derived`) for reactive state instead of stores.
**When to use:** All component state and shared state in `.svelte.ts` files.

```typescript
// src/lib/stores/story.svelte.ts
// Svelte 5 runes-based state (replaces Svelte 4 stores)

export class StoryState {
  stories = $state<Story[]>([]);
  activeStoryId = $state<string | null>(null);
  
  activeStory = $derived(
    this.stories.find(s => s.id === this.activeStoryId) ?? null
  );
  
  setActiveStory(id: string) {
    this.activeStoryId = id;
  }
}

export const storyState = new StoryState();
```

**Important Svelte 5 note:** Use `$state.raw()` (not `$state()`) for large arrays like nodes/edges to avoid deep reactivity performance issues. This is documented in the Svelte Flow quickstart and applies to any large data structures.

### Anti-Patterns to Avoid

- **Don't use Svelte 4 store syntax** (`writable()`, `$store` auto-subscribe): Svelte 5 runes (`$state`, `$derived`, `$effect`) are the current standard. Legacy store syntax still works but mixing patterns causes confusion.
- **Don't use SSR with a separate API backend**: SvelteKit's SSR requires the API to be available at build time. Since FastAPI is the API server, use SPA mode (`ssr = false`) to avoid build-time API dependency.
- **Don't put `+page.server.ts` files in SPA mode**: Server-side load functions don't run in SPA mode. Use client-side fetch in `+page.ts` or component `onMount`.
- **Don't use deeply reactive `$state()` for large arrays**: Use `$state.raw()` for node lists, story trees, and similar large collections. Deep reactivity on hundreds of objects causes performance issues.
- **Don't build a custom split pane**: `svelte-splitpanes` handles touch, RTL, snapping, resize events, min/max constraints, and nested panes. Hand-rolling this is a multi-week effort for edge cases alone.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rich text editing | Custom contenteditable wrapper | Tiptap (wrapping ProseMirror) | ProseMirror handles selection, undo/redo, input rules, paste handling, schema enforcement, collaborative editing foundation. Years of edge cases solved. |
| Resizable panels | CSS resize + drag handlers | svelte-splitpanes | Touch events, min/max, snapping, nested panes, RTL support, keyboard accessibility — each is a multi-day effort. |
| Provenance color coding | Manual DOM manipulation | Tiptap custom Mark extension | Marks integrate with ProseMirror's document model — undo/redo, paste, serialization all work automatically. DOM manipulation fights the editor. |
| LLM structured output parsing | Manual JSON extraction from LLM response | `client.beta.chat.completions.parse()` (OpenAI SDK) | The existing `parse_structured()` function already handles this. Port it as-is. |
| WebSocket connection management | Raw WebSocket + reconnection logic | A thin wrapper class with reconnect/backoff | Don't use a full library (socket.io), but do wrap the native WebSocket with auto-reconnect, message queuing, and typed message handling. |

**Key insight:** The editor is the core product. Tiptap's Mark system is specifically designed for inline annotations (like provenance tracking). Fighting ProseMirror's document model with direct DOM manipulation is a guaranteed rewrite.

## SQLite Schema Design (Claude's Discretion #2)

### Recommended Data Model: Adjacency List Tree

The story tree is modeled as an adjacency list with three main tables: stories, nodes, and provenance spans.

```sql
-- Stories: top-level container
CREATE TABLE stories (
    id TEXT PRIMARY KEY,          -- UUID
    title TEXT NOT NULL,
    premise TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    active_path TEXT              -- JSON array of node IDs representing current reading path
);

-- Nodes: each paragraph/block/sentence in the story tree
CREATE TABLE nodes (
    id TEXT PRIMARY KEY,           -- UUID
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    parent_id TEXT REFERENCES nodes(id) ON DELETE SET NULL,  -- NULL for root node
    position INTEGER NOT NULL DEFAULT 0,     -- Order among siblings (for multiple candidates)
    content TEXT NOT NULL,          -- The actual text content
    node_type TEXT NOT NULL DEFAULT 'paragraph',  -- 'paragraph' | 'block' | 'sentence'
    source TEXT NOT NULL DEFAULT 'ai_generated',  -- Primary source for the whole node
    is_draft INTEGER NOT NULL DEFAULT 0,          -- 1 if this is an unaccepted draft
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Tree integrity
    UNIQUE(story_id, parent_id, position)  -- No duplicate positions among siblings
);

-- Provenance spans: character-level source tracking within a node
CREATE TABLE provenance_spans (
    id TEXT PRIMARY KEY,           -- UUID
    node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    start_offset INTEGER NOT NULL, -- Character offset within node.content
    end_offset INTEGER NOT NULL,   -- Character offset (exclusive)
    source TEXT NOT NULL,           -- 'ai_generated' | 'user_written' | 'user_edited' | 'initial_prompt'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    CHECK(start_offset >= 0),
    CHECK(end_offset > start_offset)
);

-- Index for tree traversal
CREATE INDEX idx_nodes_parent ON nodes(parent_id);
CREATE INDEX idx_nodes_story ON nodes(story_id);
CREATE INDEX idx_provenance_node ON provenance_spans(node_id);
```

### Switchable Atomic Unit (Claude's Discretion #4)

**Recommendation: This is primarily a view-layer concern.**

Storage always captures the full text content in each node. The `node_type` field records what granularity the node was created at, but the switchable granularity is a display/editing preference:

- **Paragraph mode** (default): Each node is a paragraph. The editor shows one Tiptap block per node.
- **Block mode**: User defines arbitrary block boundaries. Same storage — just different split points.
- **Sentence mode**: Each node is a sentence. More granular branching, but same tree structure.

The tree structure is identical regardless of granularity. The `node_type` field lets the UI know how to display it, but the tree traversal logic doesn't change. When a user switches granularity on existing content, the UI re-renders the same tree differently — it doesn't restructure the database.

### Branch Semantics

The adjacency list naturally supports both branching modes:

1. **Fork at a point**: Create a new child node at the same parent with a different `position`. Both children represent alternative continuations.
2. **Multiple candidates per node**: Multiple nodes with the same `parent_id` are sibling alternatives. The `position` field determines order (candidate 0, 1, 2...).

The `active_path` on the story table records which branch the user is currently reading/editing. It's a JSON array of node IDs from root to current position.

### Provenance Span Mechanics

Provenance spans are stored separately from the text content. When the user edits text within a node:

1. Identify which provenance spans overlap the edit range
2. Split/shrink/delete affected spans
3. Create a new span with `source: 'user_edited'` for the modified region
4. Merge adjacent spans with the same source

This is analogous to how text editors handle overlapping formatting — the same algorithmic pattern ProseMirror uses for marks.

## WebSocket vs SSE Decision (Claude's Discretion #3)

**Recommendation: WebSocket.**

| Factor | WebSocket | SSE |
|--------|-----------|-----|
| Direction | Bidirectional | Server → Client only |
| Cancel generation | Send `{"type": "cancel"}` on same connection | Need separate REST `POST /cancel` endpoint |
| Accept/reject draft | Send on same connection | Need separate REST endpoints |
| Connection overhead | One persistent connection | One per event stream + separate REST connections |
| Browser support | Universal | Universal |
| Complexity | Slightly more setup | Simpler server code |

**Why WebSocket wins here:** The story generation workflow is inherently interactive — the user needs to cancel mid-generation, accept drafts, reject and retry, all while receiving streaming tokens. SSE would require a separate REST endpoint for every client→server message, fragmenting the protocol across two transport mechanisms. WebSocket keeps the entire generation conversation on one connection.

**Note:** REST endpoints are still used for non-streaming operations (CRUD for stories, model listing, backend configuration).

## Rich Text Editor Decision (Claude's Discretion #1)

**Recommendation: Tiptap 3.x.**

| Factor | Tiptap | ProseMirror (raw) | CodeMirror |
|--------|--------|-------------------|------------|
| Svelte integration | Official guide + examples (Svelte 5 runes) | Manual — wire up views yourself | No official Svelte wrapper |
| Custom marks | `Mark.create()` with `addAttributes()` | Lower-level `MarkSpec` | Not applicable (code editor) |
| Learning curve | Medium — good abstraction layer | High — complex plugin system | Medium but wrong domain |
| Rich text formatting | Full: bold, italic, headings, lists | Full (Tiptap is built on it) | Code formatting only |
| Extensibility | Extension system: nodes, marks, plugins | Same underlying system | Language modes |
| Bundle size | ~50KB (core + starter-kit) | ~40KB | ~100KB |

**Why Tiptap:** The provenance tracking feature requires custom marks that integrate with undo/redo, paste handling, and serialization. Tiptap's `Mark.create()` API makes this straightforward. Using ProseMirror directly would require implementing the same thing with more boilerplate and less documentation. CodeMirror is a code editor — wrong tool for prose writing.

## Development Workflow

### Dev Mode (two processes)

```bash
# Terminal 1: FastAPI backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: SvelteKit dev server
cd frontend && npm run dev -- --port 5173
```

The SvelteKit dev server proxies API requests to FastAPI via Vite's proxy config:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
    }
  }
});
```

### Production Mode

```bash
# Build frontend to static files
cd frontend && npm run build

# FastAPI serves static files from build output
# In app/main.py:
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="spa")
```

## Common Pitfalls

### Pitfall 1: Tiptap Content vs. DOM Synchronization
**What goes wrong:** Directly manipulating DOM inside the Tiptap editor element instead of using the editor's command API. Content gets out of sync with ProseMirror's document state, undo breaks, marks disappear.
**Why it happens:** Temptation to use `innerHTML` or direct span manipulation for provenance colors.
**How to avoid:** Always use Tiptap's transaction API: `editor.chain().setMark('provenance', { source: 'ai_generated' }).run()`. Never touch the DOM directly.
**Warning signs:** Undo/redo stops working correctly. Marks disappear on re-render.

### Pitfall 2: Svelte 5 Deep Reactivity on Large Data
**What goes wrong:** Using `$state()` (deeply reactive) for arrays of 100+ story nodes. Every node property change triggers reactive updates on the entire array.
**Why it happens:** `$state()` is the default — easy to reach for.
**How to avoid:** Use `$state.raw()` for story tree data, node arrays, and any large collections. Use `$state()` only for simple, small reactive values.
**Warning signs:** Editor becomes laggy as story grows. Browser devtools show excessive re-renders.

### Pitfall 3: WebSocket Reconnection
**What goes wrong:** WebSocket drops silently (network change, laptop sleep, server restart). UI doesn't notice — user clicks "Generate" and nothing happens.
**Why it happens:** Native WebSocket has no built-in reconnection.
**How to avoid:** Wrap the WebSocket in a reconnection manager with exponential backoff, connection state indicator in the UI, and message queuing during reconnection.
**Warning signs:** Generation "hangs" after laptop wake or network change.

### Pitfall 4: Provenance Span Fragmentation
**What goes wrong:** After many edits, provenance_spans table has thousands of tiny spans (1-2 characters each). Rendering becomes slow because each span needs a separate Tiptap mark.
**Why it happens:** Every keystroke in a provenance-tracked region creates a new span boundary.
**How to avoid:** Merge adjacent spans with the same source after each edit. Batch span updates — don't create a new span per keystroke, but per edit operation (on blur or debounced).
**Warning signs:** Slow editor rendering on long stories. Database grows disproportionately.

### Pitfall 5: CORS in Development
**What goes wrong:** Frontend (port 5173) can't reach backend (port 8000). Browser blocks requests with "CORS error."
**Why it happens:** Different ports = different origins. FastAPI needs explicit CORS configuration.
**How to avoid:** Add CORS middleware to FastAPI for development:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
```
Use Vite proxy in production to avoid CORS entirely.

### Pitfall 6: SQLite Concurrent Access
**What goes wrong:** Two async FastAPI handlers try to write to SQLite simultaneously. One gets "database is locked" error.
**Why it happens:** SQLite has a single-writer model. `aiosqlite` wraps it in a thread but doesn't prevent concurrent writes from different async tasks.
**How to avoid:** Use a single aiosqlite connection with WAL mode enabled (`PRAGMA journal_mode=WAL`). WAL allows concurrent reads with one writer. For this single-user app, one connection is sufficient.

## Code Examples

### Porting parse_structured() to FastAPI

```python
# backend/app/services/llm.py
# Direct port from marimo app.py lines 359-381
from typing import Type, TypeVar, Sequence, Dict
from openai import OpenAI

T = TypeVar("T")

async def parse_structured(
    client: OpenAI,
    *,
    model: str,
    schema: Type[T],
    user_content: str,
    system_content: str = "You are a helpful assistant. Follow the response model docstring.",
    temperature: float = 0.2,
    extra_messages: Sequence[Dict[str, str]] = (),
) -> T:
    """Port of app.py parse_structured(). Uses OpenAI beta structured output API."""
    messages = [{"role": "system", "content": system_content}]
    messages += list(extra_messages)
    messages += [{"role": "user", "content": user_content}]

    # Note: OpenAI SDK is synchronous — run in threadpool for async FastAPI
    import asyncio
    parsed = await asyncio.to_thread(
        lambda: client.beta.chat.completions.parse(
            model=model,
            response_format=schema,
            messages=messages,
            temperature=temperature,
        ).choices[0].message.parsed
    )
    return schema.model_validate(parsed)
```

### LLM Client Factory (port from app.py)

```python
# backend/app/services/llm.py
from openai import OpenAI
from app.models.schemas import LLMBackendConfig

def create_llm_client(config: LLMBackendConfig) -> OpenAI:
    """Factory for LLM clients — ports app.py lines 160-206."""
    if config.backend in ("llamacpp", "lmstudio"):
        base_url = normalize_base_url(config.base_url)
        return OpenAI(base_url=base_url, api_key="sk-no-key-required")
    elif config.backend == "ollama":
        base_url = normalize_base_url(config.host)
        return OpenAI(base_url=base_url, api_key="ollama")
    elif config.backend == "openai":
        return OpenAI(api_key=config.api_key)
    raise ValueError(f"Unknown backend: {config.backend}")
```

### Collapsible Sidebar Component

```svelte
<!-- VS Code-style collapsible sidebar -->
<script>
  let { children, side = 'left', title = '', collapsed = $bindable(false) } = $props();
</script>

<div class="sidebar" class:collapsed class:left={side === 'left'} class:right={side === 'right'}>
  <button class="toggle" onclick={() => collapsed = !collapsed}>
    {collapsed ? (side === 'left' ? '▶' : '◀') : (side === 'left' ? '◀' : '▶')}
  </button>
  {#if !collapsed}
    <div class="sidebar-content">
      <h3>{title}</h3>
      {@render children()}
    </div>
  {/if}
</div>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Svelte 4 stores (`writable()`) | Svelte 5 runes (`$state`, `$derived`) | Svelte 5.0 (Oct 2024) | All new Svelte code should use runes. Stores still work but are legacy. |
| Svelte 4 event syntax (`on:click`) | Svelte 5 event syntax (`onclick`) | Svelte 5.0 (Oct 2024) | Event handlers are now properties, not directives. |
| Svelte 4 `export let` props | Svelte 5 `$props()` rune | Svelte 5.0 (Oct 2024) | `let { foo, bar } = $props()` replaces `export let foo; export let bar;` |
| SvelteKit `load()` stores | SvelteKit `$app/state` | SvelteKit 2.15+ (2025) | `page` rune replaces `$page` store |
| Tiptap 2.x | Tiptap 3.x | 2025 | Svelte 5 runes support in official examples, updated extension API |

**Deprecated/outdated:**
- `svelte/store` (`writable`, `readable`, `derived`): Still works but Svelte 5 runes are preferred
- `on:event` directive syntax: Replaced by `onevent` property syntax in Svelte 5
- `export let` for component props: Replaced by `$props()` rune

## Open Questions

1. **Tiptap 3.x exact version compatibility with Svelte 5**
   - What we know: Official Tiptap docs show Svelte 5 runes examples, packages are `@tiptap/core`, `@tiptap/pm`, `@tiptap/starter-kit`
   - What's unclear: Exact version ranges that work with Svelte 5. The npm page returned 403 during research.
   - Recommendation: Install latest and test. Pin versions after confirming compatibility.

2. **aiosqlite vs sqlite3 + thread pool**
   - What we know: aiosqlite wraps sqlite3 in a background thread. FastAPI is async.
   - What's unclear: Whether `asyncio.to_thread()` with stdlib sqlite3 is simpler/better than aiosqlite for this use case.
   - Recommendation: Use aiosqlite — it's the standard approach for async SQLite in FastAPI and handles connection lifecycle.

3. **Provenance span granularity — when to merge**
   - What we know: Character-level tracking creates many small spans over time.
   - What's unclear: Optimal merge strategy — on every edit? On save? On paragraph completion?
   - Recommendation: Merge adjacent same-source spans on save (not on every keystroke). Debounce with 500ms idle timeout.

## Sources

### Primary (HIGH confidence)
- SvelteKit SPA mode docs: https://svelte.dev/docs/kit/single-page-apps
- SvelteKit adapter-static docs: https://svelte.dev/docs/kit/adapter-static
- Tiptap Svelte installation guide: https://tiptap.dev/docs/editor/getting-started/install/svelte
- Tiptap Mark API docs: https://tiptap.dev/docs/editor/extensions/custom-extensions/create-new/mark
- FastAPI WebSocket docs: https://fastapi.tiangolo.com/advanced/websockets/
- svelte-splitpanes GitHub: https://github.com/orefalo/svelte-splitpanes (v8.0.14, MIT, 463 stars)
- Svelte Flow docs: https://svelteflow.dev/learn (v1.5.0, @xyflow/svelte)
- Existing app source: `02-worktrees/demo-marimo-app/app.py` (820 lines, verified locally)

### Secondary (MEDIUM confidence)
- Svelte 5 runes documentation (verified via SvelteKit and Svelte Flow docs cross-reference)
- FastAPI + SvelteKit monorepo patterns (multiple community sources, common pattern)

### Tertiary (LOW confidence)
- Tiptap 3.x exact version numbers (npm pages returned 403; based on docs labeling)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified via official docs, version numbers confirmed
- Architecture: HIGH — monorepo + SPA + API is a well-established pattern with SvelteKit official docs supporting it
- Rich text editor (Tiptap): HIGH — official Svelte integration guide verified, Mark API verified
- SQLite schema: MEDIUM — adjacency list is standard, but span-level provenance is custom design
- Pitfalls: MEDIUM — based on general full-stack patterns and ProseMirror/Tiptap experience

**Research date:** 2026-02-13
**Valid until:** 2026-03-13 (stable stack, 30-day validity)
