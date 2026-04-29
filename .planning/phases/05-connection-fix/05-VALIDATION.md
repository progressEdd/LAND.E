---
phase: 05
slug: connection-fix
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 05 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property               | Value                                                    |
| ---------------------- | -------------------------------------------------------- |
| **Framework**          | No test framework installed — manual verification only    |
| **Config file**        | none                                                     |
| **Quick run command**  | `grep -n "ping\|pong\|heartbeat\|reconnect" frontend/src/lib/api/ws.ts backend/app/routers/ws.py frontend/src/lib/components/GenerationControls.svelte frontend/src/lib/components/SettingsPanel.svelte` |
| **Full suite command** | Manual: start app, verify behaviors below                |
| **Estimated runtime**  | ~120 seconds (manual)                                    |

---

## Sampling Rate

- **After every task commit:** Run `grep` verification commands from RESEARCH.md
- **After every plan wave:** Start dev servers and manually verify connection behaviors
- **Before `/gsd-verify-work`:** All manual behaviors verified
- **Max feedback latency:** 30 seconds (grep commands)

---

## Per-Task Verification Map

| Task ID   | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status    |
| --------- | ---- | ---- | ----------- | --------- | ----------------- | ----------- | --------- |
| 05-01-01  | 01   | 1    | CONN-01     | grep      | `grep "ping" backend/app/routers/ws.py` | ⬜ W0 | ⬜ pending |
| 05-01-02  | 01   | 1    | CONN-01     | grep      | `grep "heartbeat\|ping\|pong" frontend/src/lib/api/ws.ts` | ⬜ W0 | ⬜ pending |
| 05-01-03  | 01   | 1    | CONN-02     | grep      | `grep "reconnect" frontend/src/lib/api/ws.ts` | ⬜ W0 | ⬜ pending |
| 05-01-04  | 01   | 1    | CONN-02     | grep      | `grep "reconnect" frontend/src/lib/components/GenerationControls.svelte` | ⬜ W0 | ⬜ pending |
| 05-01-05  | 01   | 1    | CONN-02     | grep      | `grep "reconnect" frontend/src/lib/components/SettingsPanel.svelte` | ⬜ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No test framework needed — this is a focused bug fix validated by grep and manual testing.*

---

## Manual-Only Verifications

| Behavior                                              | Requirement | Why Manual              | Test Instructions                                                                                                    |
| ----------------------------------------------------- | ----------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Heartbeat keeps connection alive on Dashboard         | CONN-01     | Requires running server | Start app, stay on Dashboard 60s, open editor, verify indicator is "connected"                                       |
| "I'm Feeling Lucky" keeps connection green            | CONN-01     | Requires running server | Start app, click "I'm Feeling Lucky", verify indicator stays green through premise → story → editor flow             |
| Click indicator triggers reconnect                    | CONN-02     | Requires running server | Disconnect server, wait for "disconnected", restart server, click indicator, verify "connected"                      |
| Settings reconnect button works                       | CONN-02     | Requires running server | Open Settings panel, click Reconnect button, verify indicator shows "connected"                                      |
| Generate works after reconnect                        | CONN-01     | Requires running server | After any reconnect, click Generate, verify streaming works                                                          |
| No regression in existing generate/cancel/accept flow | CONN-01     | Requires running server | Generate text, cancel, accept, reject — all work identically to before                                               |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
