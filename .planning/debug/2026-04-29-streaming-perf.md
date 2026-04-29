---
created: 2026-04-29T04:44:47Z
issue: Streaming takes a long time — tokens appear slowly after a long delay
type: performance
phase: completed (v1.0)
status: resolved
---

## Root Cause

The WebSocket streaming in `ws.py` was **fake streaming** — it ran two sequential non-streaming LLM calls (`StoryAnalysis` + `StoryContinue`) via `parse_structured()` (which uses `beta.chat.completions.parse`), waited for both to complete (~7.2s total), then re-streamed the already-complete text character-by-character with artificial 10ms delays (`asyncio.sleep(0.01)` per char). The user saw dead silence for ~7 seconds, then slow token dribble for another ~1.8s.

## Fix

Split the generation pipeline into two steps with real streaming for the continuation:

1. **`story.py`**: Added `run_analysis()` (standalone analysis step) and `stream_continuation()` (async generator that uses `client.chat.completions.create(stream=True)` for true token-by-token streaming from the LLM). Kept `run_cycle()` for backwards compatibility.

2. **`ws.py`**: Replaced the `run_cycle()` + fake-char-streaming loop with:
   - Step 1: Send `{"type": "status", "message": "Analyzing story..."}` then run `run_analysis()` (non-streaming, still needs structured output)
   - Step 2: Send `{"type": "status", "message": "Writing next paragraph..."}` then stream via `stream_continuation()` — tokens are forwarded to the WebSocket as they arrive from the LLM
   - Removed `asyncio.sleep(0.01)` artificial delay

3. **`ws.ts`**: Added `{ type: 'status'; message: string }` to `WSServerMessage` union type

4. **`generation.svelte.ts`**: Added `analyzing` status, `statusMessage` state, handles `status` messages from server

5. **`GenerationControls.svelte`**: Shows `statusMessage` during generation/analyzing, cancel button visible during both states

6. **`Editor.svelte`** + **`NodeGraph.svelte`**: Updated `isGenerating` check to include `analyzing` state

## Verification

1. Start the backend: `cd 02-worktrees/webapp-ui && uv run python -m backend.app.main`
2. Start the frontend: `cd 02-worktrees/webapp-ui/frontend && npm run dev`
3. Generate a story continuation — should see:
   - "Analyzing story..." status message immediately
   - "Writing next paragraph..." after analysis completes
   - Tokens streaming in real-time from the LLM (no artificial delay)
4. Total perceived latency should drop from ~9s to ~4s (analysis is still non-streaming, but the continuation streams as it generates)
