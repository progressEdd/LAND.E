---
wave: 1
depends_on: []
files_modified:
  - 02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts
  - 02-worktrees/webapp-ui/backend/app/routers/ws.py
  - 02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts
  - 02-worktrees/webapp-ui/frontend/src/lib/components/GenerationControls.svelte
  - 02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte
autonomous: true
requirements_addressed: [CONN-01, CONN-02]
---

# Plan 01: WebSocket Heartbeat, Reconnect, and UI Controls

**Objective:** Fix the WebSocket connection indicator going stale after Dashboard inactivity by adding a client-server heartbeat, mount-triggered reconnect, reconnect counter reset, and manual reconnect UI in both the editor indicator and Settings panel.

## Task 01: Add ping/pong heartbeat to WebSocket client

<objective>Implement a periodic ping/pong heartbeat in `ws.ts` that keeps the WebSocket connection alive through the Vite dev proxy and detects stale connections early.</objective>

<read_first>
- `02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts` — Current WebSocket client with connect, reconnect, send, disconnect
- `.planning/phases/05-connection-fix/05-CONTEXT.md` — Locked decisions D-02, D-03
- `.planning/phases/05-connection-fix/05-RESEARCH.md` — Heartbeat implementation sketch
</read_first>

<action>
In `02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts`:

1. Add `{ type: 'ping' }` to the `WSClientMessage` type union.

2. Add `{ type: 'pong' }` to the `WSServerMessage` type union.

3. Add private fields to the `WebSocketClient` class:
   - `heartbeatInterval: ReturnType<typeof setInterval> | null = null`
   - `pongTimeout: ReturnType<typeof setTimeout> | null = null`
   - `heartbeatIntervalMs = 25000` (25 seconds)
   - `pongTimeoutMs = 10000` (10 seconds)

4. Add private method `startHeartbeat(): void`:
   - Call `this.stopHeartbeat()` first
   - Set `this.heartbeatInterval = setInterval(() => { ... }, this.heartbeatIntervalMs)`
   - Inside the interval: if `this.ws?.readyState === WebSocket.OPEN`, call `this.send({ type: 'ping' })`, then set `this.pongTimeout = setTimeout(() => { this.ws?.close(); }, this.pongTimeoutMs)` — closing the socket triggers `onclose` which triggers reconnect

5. Add private method `stopHeartbeat(): void`:
   - `clearInterval(this.heartbeatInterval)` and set to null
   - `clearTimeout(this.pongTimeout)` and set to null

6. In the existing `onopen` handler inside `_connect()`: add `this.startHeartbeat()` after `this.reconnectAttempts = 0;`

7. In the existing `onclose` handler inside `_connect()`: add `this.stopHeartbeat()` before `this._attemptReconnect()`

8. In the existing `onmessage` handler inside `_connect()`: after parsing the message, add a check: if `msg.type === 'pong'`, call `this.stopHeartbeat()` then immediately call `this.startHeartbeat()` to reset the interval timer (this clears the pong timeout and restarts the cycle). Do NOT pass pong messages to `this.onMessage`.

9. In the `disconnect()` method: add `this.stopHeartbeat()` before the existing cleanup code.
</action>

<acceptance_criteria>
- `ws.ts` contains `type: 'ping'` in `WSClientMessage` union
- `ws.ts` contains `type: 'pong'` in `WSServerMessage` union
- `ws.ts` contains `startHeartbeat()` method
- `ws.ts` contains `stopHeartbeat()` method
- `ws.ts` contains `heartbeatIntervalMs` field with value `25000`
- `ws.ts` contains `pongTimeoutMs` field with value `10000`
- `onopen` handler calls `this.startHeartbeat()`
- `onclose` handler calls `this.stopHeartbeat()`
- `onmessage` handler handles `msg.type === 'pong'` and clears timeout
- `disconnect()` method calls `this.stopHeartbeat()`
</acceptance_criteria>

---

## Task 02: Add ping handler to backend WebSocket

<objective>Add server-side handling for ping messages that responds with pong to complete the heartbeat loop.</objective>

<read_first>
- `02-worktrees/webapp-ui/backend/app/routers/ws.py` — Server-side WebSocket handler with message type dispatch
</read_first>

<action>
In `02-worktrees/webapp-ui/backend/app/routers/ws.py`:

1. In the `while True` loop inside `websocket_generate()`, after the existing `elif msg_type == "reject":` block and before the end of the try block, add:

```python
elif msg_type == "ping":
    await websocket.send_json({"type": "pong"})
```

That's it — one handler, one response.
</action>

<acceptance_criteria>
- `ws.py` contains `elif msg_type == "ping":`
- `ws.py` contains `await websocket.send_json({"type": "pong"})` in the ping handler
- The ping handler is at the same indentation level as the existing `elif msg_type == "cancel":`, `elif msg_type == "accept":`, `elif msg_type == "reject":` blocks
</acceptance_criteria>

---

## Task 03: Add reconnect and counter-reset methods to WebSocket client and generation state

<objective>Expose a public `reconnect()` method and a `resetReconnectAttempts()` method on `wsClient`, and expose a `reconnect()` method on `generationState` for UI components to call.</objective>

<read_first>
- `02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts` — WebSocket client with private `_connect()` and `_attemptReconnect()`
- `02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts` — GenerationState store that wraps wsClient
- `.planning/phases/05-connection-fix/05-CONTEXT.md` — Locked decisions D-04, D-05
</read_first>

<action>
In `02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts`:

1. Add public method `resetReconnectAttempts(): void`:
   ```typescript
   resetReconnectAttempts(): void {
     this.reconnectAttempts = 0;
   }
   ```

2. Add public method `reconnect(): void`:
   ```typescript
   reconnect(): void {
     // Stop any existing heartbeat
     this.stopHeartbeat();
     // Clear any pending reconnect timer
     if (this.reconnectTimer) {
       clearTimeout(this.reconnectTimer);
       this.reconnectTimer = null;
     }
     // Close existing socket if any
     this.ws?.close();
     this.ws = null;
     // Reset attempts and connect fresh
     this.reconnectAttempts = 0;
     this._connect();
   }
   ```

In `02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts`:

1. Add public method `reconnect(): void`:
   ```typescript
   reconnect(): void {
     wsClient.reconnect();
   }
   ```

2. Add public method `resetReconnectAttempts(): void`:
   ```typescript
   resetReconnectAttempts(): void {
     wsClient.resetReconnectAttempts();
   }
   ```
</action>

<acceptance_criteria>
- `ws.ts` contains public method `reconnect(): void`
- `ws.ts` contains public method `resetReconnectAttempts(): void`
- `ws.ts` `reconnect()` sets `this.reconnectAttempts = 0` before calling `this._connect()`
- `generation.svelte.ts` contains public method `reconnect(): void`
- `generation.svelte.ts` contains public method `resetReconnectAttempts(): void`
- `generation.svelte.ts` `reconnect()` delegates to `wsClient.reconnect()`
</acceptance_criteria>

---

## Task 04: Add click-to-reconnect on connection indicator in GenerationControls

<objective>Make the connection indicator interactive — clicking it triggers a reconnect. Add a hover tooltip hint so users discover this behavior.</objective>

<read_first>
- `02-worktrees/webapp-ui/frontend/src/lib/components/GenerationControls.svelte` — Connection indicator div with dot and text
- `.planning/phases/05-connection-fix/05-CONTEXT.md` — Locked decisions D-06, D-08
</read_first>

<action>
In `02-worktrees/webapp-ui/frontend/src/lib/components/GenerationControls.svelte`:

1. Add `onMount` import from `svelte` (add to existing imports if present, or add `import { onMount } from 'svelte';`).

2. Add an `onMount` callback:
   ```typescript
   onMount(() => {
     if (generationState.connectionState !== 'connected') {
       generationState.reconnect();
     }
   });
   ```
   This implements decision D-04 — reconnect on mount when stale.

3. Add function `handleIndicatorClick()`:
   ```typescript
   function handleIndicatorClick() {
     generationState.reconnect();
   }
   ```

4. Change the `.connection-indicator` div:
   - Add `onclick={handleIndicatorClick}`
   - Change `title` from `"WebSocket {generationState.connectionState}"` to `title="Click to reconnect · {generationState.connectionState}"`
   - Add `role="button"` and `tabindex="0"` for accessibility
   - Add `onkeydown` handler: `onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleIndicatorClick(); }}`

5. Add CSS for cursor on `.connection-indicator`:
   ```css
   .connection-indicator {
     cursor: pointer;
     /* ...existing styles... */
   }
   .connection-indicator:hover .connection-text {
     color: var(--text-secondary, #d1d5db);
   }
   ```
</action>

<acceptance_criteria>
- `GenerationControls.svelte` imports `onMount` from `svelte`
- `GenerationControls.svelte` has `onMount` callback that checks `generationState.connectionState !== 'connected'` and calls `generationState.reconnect()`
- `GenerationControls.svelte` has `handleIndicatorClick` function
- `.connection-indicator` div has `onclick={handleIndicatorClick}`
- `.connection-indicator` div has `title` attribute containing "Click to reconnect"
- `.connection-indicator` div has `role="button"` and `tabindex="0"`
- `.connection-indicator` has `cursor: pointer` in scoped CSS
</acceptance_criteria>

---

## Task 05: Add reconnect button to SettingsPanel

<objective>Add a reconnect button in the Settings panel's LLM Backend section so users have a second location to trigger reconnection.</objective>

<read_first>
- `02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte` — LLM config panel with backend, URL, model, warmup sections
- `.planning/phases/05-connection-fix/05-CONTEXT.md` — Locked decision D-07
</read_first>

<action>
In `02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte`:

1. Add import at the top of the script:
   ```typescript
   import { generationState } from '$lib/stores/generation.svelte';
   ```

2. Add function:
   ```typescript
   function handleReconnect() {
     generationState.reconnect();
   }
   ```

3. After the warmup button `div.field` block (the last field in the LLM Backend section), add a new `div.field`:
   ```svelte
   <!-- Reconnect button -->
   <div class="field">
     <button class="btn btn-primary" onclick={handleReconnect}>
       Reconnect WebSocket
     </button>
   </div>
   ```
   This places it logically with the other connection/config controls.

No new CSS needed — the existing `.btn.btn-primary` and `.field` styles already handle the appearance.
</action>

<acceptance_criteria>
- `SettingsPanel.svelte` imports `generationState` from `'$lib/stores/generation.svelte'`
- `SettingsPanel.svelte` has `handleReconnect` function that calls `generationState.reconnect()`
- `SettingsPanel.svelte` has a `<button>` with text `Reconnect WebSocket`
- The button has `onclick={handleReconnect}`
- The button uses `class="btn btn-primary"`
</acceptance_criteria>

---

## Task 06: Reset reconnect counter on story activation

<objective>When the user activates a story (enters the editor view from the Dashboard), reset the reconnect attempt counter to give fresh reconnection attempts.</objective>

<read_first>
- `02-worktrees/webapp-ui/frontend/src/routes/+page.svelte` — Page lifecycle with onMount
- `02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts` — GenerationState with resetReconnectAttempts method
- `.planning/phases/05-connection-fix/05-CONTEXT.md` — Locked decision D-05
</read_first>

<action>
In `02-worktrees/webapp-ui/frontend/src/routes/+page.svelte`:

1. No new imports needed — `generationState` is already imported.

2. Add a reactive `$effect()` that watches `storyState.activeStoryId` and resets the reconnect counter when a story is activated:
   ```typescript
   $effect(() => {
     const id = storyState.activeStoryId;
     if (id) {
       generationState.resetReconnectAttempts();
     }
   });
   ```
   Place this after the existing `$effect()` that persists `activeStoryId` to localStorage.

This implements decision D-05 — fresh user actions (selecting a story) reset the reconnect attempt counter.
</action>

<acceptance_criteria>
- `+page.svelte` has an `$effect()` that references `storyState.activeStoryId`
- Inside the effect, when `id` is truthy, calls `generationState.resetReconnectAttempts()`
</acceptance_criteria>

---

## Wave Summary

| Wave | Tasks | What it builds |
| ---- | ----- | -------------- |
| 1    | 01-06 | Heartbeat + reconnect + UI controls — complete fix |

**must_haves** (from phase goal: "I'm Feeling Lucky" no longer breaks the connection indicator):
1. Heartbeat ping/pong keeps connection alive through Vite proxy during Dashboard inactivity
2. Server responds to ping with pong
3. Clicking connection indicator triggers reconnect
4. Settings panel has a reconnect button
5. Reconnect counter resets on user action (story activation)
6. GenerationControls mounts with stale connection trigger reconnect

---

## Verification

After all tasks are complete, run:

```bash
# Verify ping handler in backend
grep -n "ping" 02-worktrees/webapp-ui/backend/app/routers/ws.py

# Verify heartbeat in frontend
grep -n "heartbeat\|ping\|pong" 02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts

# Verify reconnect methods
grep -n "reconnect" 02-worktrees/webapp-ui/frontend/src/lib/api/ws.ts
grep -n "reconnect" 02-worktrees/webapp-ui/frontend/src/lib/stores/generation.svelte.ts

# Verify UI changes
grep -n "reconnect" 02-worktrees/webapp-ui/frontend/src/lib/components/GenerationControls.svelte
grep -n "Reconnect" 02-worktrees/webapp-ui/frontend/src/lib/components/SettingsPanel.svelte

# Verify counter reset on story activation
grep -n "resetReconnectAttempts" 02-worktrees/webapp-ui/frontend/src/routes/+page.svelte
```

All grep commands should return matches with the expected strings.

### Manual Verification

1. Start app: `cd 02-worktrees/webapp-ui && make dev` (or start backend + frontend separately)
2. Stay on Dashboard for 60 seconds
3. Click a story or "I'm Feeling Lucky"
4. Verify connection indicator shows "connected" (green dot)
5. Stop backend server, wait for "disconnected", restart backend, click indicator
6. Verify indicator returns to "connected"
7. Open Settings panel, click "Reconnect WebSocket" button
8. Verify indicator shows "connected"
9. Generate text, verify streaming works normally
