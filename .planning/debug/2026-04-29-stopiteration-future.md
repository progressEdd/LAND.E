---
created: 2026-04-29T04:50:00Z
issue: StopIteration interacts badly with generators and cannot be raised into a Future
type: runtime_error
phase: completed (v1.0)
status: resolved
---

## Root Cause

The `stream_continuation()` function in `story.py` bridged a synchronous generator to async using `loop.run_in_executor(None, next, gen)`. When the generator is exhausted, `next()` raises `StopIteration`. Python 3.12+ prohibits `StopIteration` from being raised into a `Future` — it throws `RuntimeError: StopIteration interacts badly with generators and cannot be raised into a Future`.

## Fix

Replaced the `run_in_executor(None, next, gen)` pattern with a `queue.Queue` + daemon thread + sentinel pattern:
- A background thread drains the sync generator into a `queue.Queue`
- The sentinel `_SENTINEL = object()` signals end-of-stream
- Exceptions from the generator are put on the queue and re-raised in the async context
- `run_in_executor(None, q.get)` blocks on queue reads instead of calling `next(gen)` directly

## Verification

1. Start backend + frontend
2. Generate a story continuation
3. Should see "Analyzing story..." → "Writing next paragraph..." → tokens streaming without error
