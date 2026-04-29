# Phase 05: Connection Fix - Research

**Researched:** 2026-04-29
**Status:** Complete

## Research Question

What do I need to know to PLAN this phase well? How do we fix the WebSocket connection indicator going stale and showing "disconnected" after Dashboard inactivity or REST API calls?

## Root Cause Analysis

### Confirmed Root Cause

The WebSocket connection goes stale because there is **no heartbeat mechanism**. Here's the chain of events:

1. **App loads** → `+page.svelte` `onMount` calls `generationState.connect()` → WebSocket connects immediately
2. **User sees Dashboard** (no active story) → WebSocket is connected but idle
3. **Vite dev proxy drops idle WebSocket connections** — the proxy config in `vite.config.ts` has no timeout override, so the default idle timeout applies
4. **By the time user navigates to editor** (clicks story or "I'm Feeling Lucky") → the 5 reconnect attempts in `ws.ts` have already exhausted
5. **Result:** Connection indicator shows "disconnected", Generate button is disabled

### Key Evidence

- `ws.ts` has `maxReconnectAttempts = 5` with exponential backoff (1s, 2s, 4s, 8s, 16s) = ~31 seconds total
- `reconnectAttempts` only resets to 0 on successful `onopen` (line: `this.reconnectAttempts = 0;`)
- There is no ping/pong heartbeat — no timer sends periodic messages to keep the connection alive
- The `disconnect()` method sets `reconnectAttempts = maxReconnectAttempts` to prevent further reconnects
- REST API calls (`randomPremise`, `createStory`) are completely independent of WebSocket — they don't cause the disconnection

### Code Paths Examined

**Frontend WebSocket client** (`ws.ts`):
- `connect()` → `_connect()` → creates WebSocket, sets up `onopen`, `onclose`, `onmessage`, `onerror`
- `_attemptReconnect()` → exponential backoff, gives up after 5 attempts
- `disconnect()` → clears timers, sets counter to max, closes socket
- No heartbeat timer exists anywhere in the class

**Backend WebSocket handler** (`ws.py`):
- `websocket_generate()` → accepts connection, loops on `receive_text()`
- Only handles message types: `generate`, `cancel`, `accept`, `reject`
- No ping/pong handling, no server-initiated messages, no idle timeout management

**Connection state consumer** (`generation.svelte.ts`):
- `connect()` → delegates to `wsClient.connect()` with message and connection-state callbacks
- `disconnect()` → delegates to `wsClient.disconnect()`
- No `reconnect()` method exists — user must refresh the page

**UI indicator** (`GenerationControls.svelte`):
- Renders dot with CSS class based on `generationState.connectionState`
- The `.connection-indicator` div has a `title` attribute but no click handler
- No tooltip, no reconnect button

**Settings panel** (`SettingsPanel.svelte`):
- Only handles LLM config (backend, URL, API key, model, warmup)
- No connection-related controls

## Technical Research: Heartbeat / Ping-Pong Patterns

### WebSocket Heartbeat Approaches

**Option A: Application-level ping/pong (JSON messages)**
- Client sends `{ "type": "ping" }` every N seconds
- Server responds with `{ "type": "pong" }`
- If no pong received within timeout → connection is stale → reconnect
- **Pros:** Works through all proxies (Vite, nginx, Cloudflare), framework-agnostic, can carry metadata
- **Cons:** Requires code on both client and server

**Option B: WebSocket protocol-level ping/pong frames**
- Uses `ws.ping()` on server and browser handles pong automatically
- **Pros:** Built into the protocol, lightweight
- **Cons:** Browsers don't expose ping/pong frames to JavaScript — cannot initiate pings from client side. Not viable for this architecture where the client must be the heartbeat initiator.

**Option C: TCP keepalive**
- OS-level socket keepalive
- **Pros:** Zero code changes
- **Cons:** Default interval is 2 hours on Linux, browser WebSocket API doesn't expose keepalive settings. Not viable.

**Recommendation: Option A** — Application-level ping/pong is the only viable approach for browser-initiated heartbeat through the Vite proxy.

### Heartbeat Interval Research

- **Vite dev server proxy:** Uses `http-proxy` under the hood, which has no explicit WebSocket idle timeout — it inherits from Node.js HTTP server defaults and OS TCP keepalive. In practice, idle connections can be dropped after 2 minutes of inactivity.
- **Browser WebSocket idle timeout:** Chrome has a ~5 minute idle timeout for WebSocket connections, but this is not guaranteed across browsers.
- **Recommended interval:** 20-30 seconds for dev environments, 30-60 seconds for production. Since this is a dev-only app, **25 seconds** is a good balance.

### Reconnect Strategy Research

**Current reconnect:**
- 5 attempts with exponential backoff (1s → 16s)
- Counter only resets on successful `onopen`
- No way to trigger reconnect externally

**Needed improvements:**
1. **Counter reset on user action:** When user creates a story or enters editor, reset `reconnectAttempts` to 0
2. **Reconnect on mount:** `GenerationControls` mount should check if connection is stale and reconnect
3. **Public reconnect method:** Expose `wsClient.reconnect()` for manual trigger from UI

**Stale connection detection:**
- Heartbeat timeout (no pong within 10s of ping) → force disconnect → reconnect
- `readyState === WebSocket.CLOSED` → already closed, just reconnect
- `readyState === WebSocket.OPEN` but heartbeat failing → force close then reconnect

## Implementation Points

### Files to Modify

| File | Changes | Complexity |
|------|---------|------------|
| `frontend/src/lib/api/ws.ts` | Add heartbeat timer, pong tracking, public `reconnect()`, counter reset method | Medium |
| `backend/app/routers/ws.py` | Add `elif msg_type == "ping"` handler → send pong | Low |
| `frontend/src/lib/stores/generation.svelte.ts` | Add `reconnect()` method, expose to UI | Low |
| `frontend/src/lib/components/GenerationControls.svelte` | Click handler on indicator, tooltip/hint | Low |
| `frontend/src/lib/components/SettingsPanel.svelte` | Reconnect button in LLM config section | Low |

### Type Changes

**`WSClientMessage` union** — add:
```typescript
| { type: 'ping' }
```

**`WSServerMessage` union** — add:
```typescript
| { type: 'pong' }
```

### Heartbeat Implementation Sketch

```typescript
// In WebSocketClient class
private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
private pongTimeout: ReturnType<typeof setTimeout> | null = null;
private heartbeatIntervalMs = 25000; // 25 seconds
private pongTimeoutMs = 10000; // 10 seconds to wait for pong

private startHeartbeat(): void {
  this.stopHeartbeat();
  this.heartbeatInterval = setInterval(() => {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({ type: 'ping' });
      this.pongTimeout = setTimeout(() => {
        // No pong received — connection is stale
        this.ws?.close();
        // onclose handler will trigger reconnect
      }, this.pongTimeoutMs);
    }
  }, this.heartbeatIntervalMs);
}

private stopHeartbeat(): void {
  if (this.heartbeatInterval) {
    clearInterval(this.heartbeatInterval);
    this.heartbeatInterval = null;
  }
  if (this.pongTimeout) {
    clearTimeout(this.pongTimeout);
    this.pongTimeout = null;
  }
}
```

In `onopen`: call `this.startHeartbeat()`
In `onclose`: call `this.stopHeartbeat()`
In `onmessage`: if `msg.type === 'pong'`, clear `pongTimeout`

### Server-side ping handler sketch

```python
elif msg_type == "ping":
    await websocket.send_json({"type": "pong"})
```

One line in the existing message type chain.

### Reconnect Method

```typescript
reconnect(): void {
  this.disconnect();
  this.reconnectAttempts = 0;  // Fresh attempts
  this._connect();
}
```

### Mount-triggered Reconnect

In `GenerationControls.svelte`:
```svelte
onMount(() => {
  if (generationState.connectionState !== 'connected') {
    generationState.reconnect();
  }
});
```

Or in `generation.svelte.ts`:
```typescript
reconnect(): void {
  wsClient.reconnect();
}
```

### Counter Reset on User Action

The CONTEXT.md decisions say fresh user actions (creating a story, entering editor) should reset the counter. The simplest approach:
- Expose `wsClient.resetReconnectAttempts()` as a public method
- Call it from `generationState` when story is activated or view switches to editor

## Risks and Edge Cases

1. **Heartbeat during generation:** Heartbeat pings should not interfere with active generation. The server's `receive_text()` loop will handle both. Client's `onmessage` already routes by type. Low risk.
2. **Multiple pong responses:** If server somehow sends multiple pongs, the client should handle gracefully. Just clear the timeout on first pong. Low risk.
3. **Reconnect storm:** If heartbeat triggers reconnect and user also clicks reconnect button simultaneously. Solution: check if already connecting before triggering. The `_connect()` method already checks `if (this.ws?.readyState === WebSocket.OPEN) return;`.
4. **Component mount lifecycle:** `GenerationControls` mounts/unmounts as user switches between Dashboard and Editor. The WebSocket connection lifecycle is in `+page.svelte` (mount → connect, destroy → disconnect), so the component mount reconnect is just triggering `wsClient.reconnect()`, not a new connection. Low risk.
5. **Vite proxy reconnection:** After reconnect, the Vite proxy should accept the new WebSocket connection transparently. No special handling needed.

## Dependencies

No new packages required. All changes use existing WebSocket API, existing FastAPI WebSocket support, and existing Svelte 5 patterns.

## Validation Architecture

### Testable Behaviors

1. **Heartbeat keeps connection alive:** After 60s of inactivity on Dashboard, connection indicator is still "connected"
2. **Stale connection detected:** If server goes down and comes back, heartbeat timeout triggers reconnect
3. **Manual reconnect works:** Clicking indicator triggers reconnect, indicator shows "connected" after reconnect
4. **Settings panel reconnect works:** Button in Settings triggers same reconnect logic
5. **Reconnect counter resets:** After exhausted reconnects, user action (story creation) resets counter
6. **Generate works after reconnect:** After any reconnection, Generate button becomes enabled and works
7. **No regression:** Existing generate/cancel/accept/reject flow works identically

### Verification Commands

```bash
# Backend ping handler exists
grep -n "ping" backend/app/routers/ws.py

# Frontend heartbeat timer exists
grep -n "heartbeat" frontend/src/lib/api/ws.ts

# Reconnect method exists on wsClient
grep -n "reconnect" frontend/src/lib/api/ws.ts

# Click handler on connection indicator
grep -n "reconnect" frontend/src/lib/components/GenerationControls.svelte

# Reconnect button in settings
grep -n "reconnect" frontend/src/lib/components/SettingsPanel.svelte
```

---

*Phase: 05-connection-fix*
*Research completed: 2026-04-29*
