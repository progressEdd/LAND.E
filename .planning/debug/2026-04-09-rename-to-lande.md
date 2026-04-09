---
created: "2026-04-09T22:51:00.000Z"
issue: Rename "AI Story Writer" branding to "LAND.E" throughout the app
type: logic_error
phase: 03-dashboard-graph-rework
status: resolved
---

## Root Cause

App displayed "AI Story Writer" in two locations instead of the project name "LAND.E".

## Fix

Replaced "AI Story Writer" → "LAND.E" in:
- `+layout.svelte` top bar breadcrumb (dashboard view)
- `Dashboard.svelte` empty state welcome heading

**Files modified:**
- `02-worktrees/webapp-ui/frontend/src/routes/+layout.svelte`
- `02-worktrees/webapp-ui/frontend/src/lib/components/Dashboard.svelte`

## Verification

1. Top bar shows "LAND.E" when on dashboard view
2. Empty state shows "Welcome to LAND.E"
