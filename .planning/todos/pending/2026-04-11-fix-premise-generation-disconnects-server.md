---
created: 2026-04-28T20:28:18-05:00
title: Fix premise generation disconnects server status
area: api
files:
  - frontend/src/lib/api/rest.ts:46
  - frontend/src/lib/api/ws.ts:26
  - frontend/src/lib/components/Dashboard.svelte:48
  - frontend/src/lib/components/GenerationControls.svelte:57
  - frontend/src/lib/stores/generation.svelte.ts:17
  - backend/app/routers/stories.py:136
---

## Problem

Clicking the "I'm Feeling Lucky" / generate random premise button in the Dashboard causes the connection status indicator (green dot in GenerationControls) to show as "disconnected". The only way to restore it to "connected" is to navigate to Home and back. The button calls `api.randomPremise()` which hits `GET /api/stories/random-premise` on the backend. After this call, the WebSocket connection state (`generation.svelte.ts` → `connectionState`) appears to become `disconnected` even though the WebSocket hasn't actually dropped. Likely the REST call is triggering a navigation or state reset that tears down or misreports the WebSocket connection.

## Solution

Investigate whether:
1. The random premise REST call is causing a page/component re-render that tears down the WebSocket
2. The `feelingLucky()` function in Dashboard.svelte is triggering a store reset or navigation
3. The WebSocket client in `ws.ts` is incorrectly transitioning to `disconnected` on unrelated REST activity
4. A race condition between the REST response handling and WebSocket heartbeat/polling
