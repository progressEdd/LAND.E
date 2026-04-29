# Phase 05: Connection Fix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 05-connection-fix
**Areas discussed:** Root Cause Scope, Fix Strategy, Indicator Placement, Manual Reconnect Locations

---

## Root Cause Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Frontend-only state bug | Connection state not read reactively when component mounts | |
| Frontend + backend issue | REST calls interfere with WebSocket somehow | |
| WebSocket goes stale (no heartbeat) | Vite proxy drops idle WS, reconnect attempts exhaust before user reaches editor | ✓ |

**User's choice:** WebSocket goes stale — confirmed by behavior: reliably reproducible on fresh app start, Generate button disabled, stays red until manual page refresh, backend was running the whole time.

**Notes:** User confirmed: (1) Generate button is disabled when indicator shows disconnected, (2) reliably reproducible on new app start, (3) once a new chat is created and generation succeeds it goes away, (4) stays red unless manually creating a new chat, (5) backend was loaded. This eliminated race conditions and pointed to stale connection + exhausted reconnect.

---

## Fix Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Heartbeat/ping-pong only | Keep connection alive through proxy | |
| Reconnect on mount only | Safety net when entering editor | |
| Reset reconnect counter only | Give more attempts on user action | |
| All three + manual reconnect | Heartbeat + mount reconnect + counter reset + click-to-reconnect | ✓ |

**User's choice:** All three complementary fixes plus a manual reconnect mechanism.

**Notes:** All three mechanisms address different failure modes: heartbeat prevents the staleness, mount reconnect catches edge cases, counter reset ensures user actions always get fresh attempts. Manual reconnect is the user-visible escape hatch.

---

## Indicator Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Move to app shell (always visible) | Indicator in +page.svelte or +layout.svelte, visible from Dashboard | |
| Editor only (GenerationControls) | Keep current placement — heartbeat makes it reliable | ✓ |

**User's choice:** Editor only — heartbeat makes Dashboard visibility unnecessary since the connection won't go stale anymore.

---

## Manual Reconnect Locations

| Option | Description | Selected |
|--------|-------------|----------|
| Click indicator only | Single reconnect point in editor | |
| Settings panel only | Reconnect in the config panel | |
| Both indicator + Settings panel | Click indicator in editor, button in Settings | ✓ |

**User's choice:** Both locations. Click indicator for quick access, Settings panel as the natural "connection/config" location. Both trigger same reconnect logic. Indicator has a `?` tooltip for discoverability.

---

## the agent's Discretion

- Heartbeat interval (suggested 15-30 seconds)
- Ping/pong message format
- Pong timeout duration
- Tooltip text for indicator hint
- Settings panel reconnect button styling
- Whether to show "reconnecting..." state during manual reconnect

## Deferred Ideas

None — all discussion stayed within the connection fix scope.
