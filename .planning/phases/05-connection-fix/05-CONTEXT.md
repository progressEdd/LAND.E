# Phase 05: Connection Fix - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix the WebSocket connection indicator showing "disconnected" after clicking "I'm Feeling Lucky" or after any period of Dashboard inactivity. The WebSocket connection goes stale because there is no heartbeat — the Vite dev proxy drops idle WebSocket connections, and by the time the user reaches the editor view, the 5 reconnect attempts have exhausted. The fix must make the connection indicator reliable and give users a way to manually reconnect without refreshing the page.

</domain>

<decisions>
## Implementation Decisions

### Root Cause
- **D-01:** WebSocket goes stale on Dashboard — no heartbeat mechanism, Vite proxy drops idle WS connections, 5 reconnect attempts exhaust before user reaches editor. The REST calls (randomPremise, createStory) are unrelated — they don't touch the WebSocket.

### Fix: Heartbeat / Ping-Pong
- **D-02:** Client sends periodic ping messages to the server. Server responds with pong messages. This keeps the connection alive through the Vite proxy and detects stale connections early.
- **D-03:** If a ping fails (no pong within timeout), trigger an immediate reconnect instead of waiting for `onclose`.

### Fix: Reconnect on Mount
- **D-04:** When `GenerationControls` mounts (user enters editor view), check if the WebSocket connection is stale and trigger a reconnect. Safety net for any edge case the heartbeat doesn't catch.

### Fix: Reset Reconnect Counter
- **D-05:** Fresh user actions (creating a story, entering editor) reset the reconnect attempt counter back to 0, giving another 5 reconnect attempts. Currently the counter only resets on successful `onopen`.

### Manual Reconnect (Two Locations)
- **D-06:** Clicking the connection indicator (dot or text) in `GenerationControls.svelte` triggers a manual reconnect. A `?` tooltip or hover hint makes this discoverable.
- **D-07:** A reconnect button also appears in the Settings panel (`SettingsPanel.svelte`) — the natural "connection/config" location. Both locations trigger the same reconnect logic.

### Indicator Placement
- **D-08:** Connection indicator stays in the editor only (`GenerationControls.svelte`). Not added to Dashboard. The heartbeat fix makes this reliable — connection won't go stale on the Dashboard anymore.

### the agent's Discretion
- Heartbeat interval (reasonable default: 15-30 seconds)
- Ping/pong message format (simple JSON `{type: "ping"}` / `{type: "pong"}` or raw text)
- Pong timeout duration before triggering reconnect
- Exact tooltip text for the `?` hint on the indicator
- Settings panel reconnect button styling and placement
- Whether to show a brief "reconnecting..." state in the indicator during manual reconnect

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### WebSocket Client (primary fix target)
- `02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts` — WebSocket client with connect, reconnect, send, disconnect. Reconnect logic (5 attempts, exponential backoff) needs counter reset. Heartbeat ping timer needs adding.
- `02-worktrees/webapp-ui/backend/app/routers/ws.py` — Server-side WebSocket handler. Currently only handles generate/cancel/accept/reject. Needs ping message handling and pong response.

### Connection State (consumer of fix)
- `02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts` — GenerationState holds `connectionState`, `connect()`, `disconnect()`. Needs reconnect method exposed. Mount-triggered reconnect check goes here or in GenerationControls.
- `02-worktrees/webapp-ui/frontend/src/lib/components/GenerationControls.svelte` — Renders the connection indicator dot/text and Generate button. Click-to-reconnect handler goes here. `?` tooltip hint.

### Settings Panel (secondary reconnect location)
- `02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte` — LLM config panel. Add reconnect button here.

### Context (for understanding the flow)
- `02-worktrees/webapp-ui/frontend/src/routes/+page.svelte` — Page lifecycle: `onMount` calls `generationState.connect()`, `onDestroy` calls `disconnect()`. WebSocket connects once on page load.
- `02-worktrees/webapp-ui/frontend/vite.config.ts` — Vite proxy config: `/ws` proxies to `ws://localhost:8000` with `ws: true`. This proxy drops idle connections.
- `02-worktrees/webapp-ui/backend/app/main.py` — FastAPI app setup, no WebSocket-specific middleware or timeout config.

### Planning Context
- `.planning/codebase/ARCHITECTURE.md` — Full architecture docs.
- `.planning/codebase/CONVENTIONS.md` — Svelte 5 runes, CSS custom properties, component patterns.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `wsClient` singleton (`ws.ts`): Already has `_connect()`, `_attemptReconnect()`, `reconnectAttempts` counter, `setConnectionState()`. Heartbeat timer and counter reset fit naturally into this class.
- `generationState` singleton (`generation.svelte.ts`): Exposes `connectionState` reactively. `connect()` and `disconnect()` delegate to `wsClient`. A new `reconnect()` method would follow the same pattern.
- `SettingsPanel.svelte`: Already imports `settingsState` and `api` — adding a reconnect button is a small addition.

### Established Patterns
- Svelte 5 runes (`$state`, `$derived`) for reactive state
- Singleton stores exported from `*.svelte.ts` files
- WebSocket message types are discriminated unions in `ws.ts` (add `ping`/`pong` to the types)
- Server-side WebSocket handler uses `msg_type == "..."` string matching (add `"ping"` case)
- CSS custom properties for theming (`--text-secondary`, `--text-muted`, etc.)

### Integration Points
- `ws.ts` `WebSocketClient` class: Add heartbeat timer (setInterval in `_connect` onopen, clearInterval in disconnect/onclose), pong timeout, reset method for reconnect counter.
- `ws.py` server handler: Add `elif msg_type == "ping"` → `await websocket.send_json({"type": "pong"})`.
- `generation.svelte.ts`: Add `reconnect()` method that calls `wsClient.disconnect()` then `wsClient._connect()` (or expose a public reconnect on wsClient).
- `GenerationControls.svelte`: Add `onclick` handler on the `.connection-indicator` div that calls `generationState.reconnect()`. Add `?` tooltip.
- `SettingsPanel.svelte`: Add reconnect button that calls `generationState.reconnect()`.
- `WSServerMessage` type union in `ws.ts`: Add `{ type: 'pong' }`.
- `WSClientMessage` type union in `ws.ts`: Add `{ type: 'ping' }`.

</code_context>

<specifics>
## Specific Ideas

- The heartbeat keeps the connection alive through the Vite proxy during Dashboard time — the core problem. Without it, any amount of reconnect logic is just treating the symptom.
- Clicking the indicator to reconnect should be discoverable — a small `?` hover hint or tooltip saying something like "Click to reconnect" so users know it's interactive.
- Settings panel reconnect button is the secondary escape hatch — for users who think "I need to fix the connection" and naturally go to Settings.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-connection-fix*
*Context gathered: 2026-04-29*
