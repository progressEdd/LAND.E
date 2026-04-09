# Codebase Concerns

**Analysis Date:** 2026-04-09

## Tech Debt

**Root worktree on master but development branch has planning work:**
- Issue: Root worktree is on `master`. The `development` branch has GSD planning work that hasn't been merged to master. The latest commit on master merges development, but development still has newer commits.
- Files: Root `.git/HEAD`, git branch history
- Impact: Planning work may not be fully synchronized between branches. The `.planning/` directory exists on `master` but may be slightly behind `development`.
- Fix approach: Merge `development` into `master` to synchronize.

**Backend `pyproject.toml` placeholder description:**
- Issue: `backend/pyproject.toml` still has `description = "Add your description here"` — the default uv scaffold placeholder.
- Files: `02-worktrees/webapp-ui/backend/pyproject.toml`
- Impact: Minor — no functional impact, but signals incomplete setup.
- Fix approach: Update to a real description.

**No linter or formatter configured:**
- Issue: Neither backend (Python) nor frontend (TypeScript/Svelte) has a linter or formatter configured. No ruff, black, ESLint, or Prettie
- Files: No config files exist (`.flake8`, `ruff.toml`, `.prettierrc`, `.eslintrc`)
- Impact: Inconsistent code style across files. May accumulate style drift over time.
- Fix approach: Add ruff for Python (`pyproject.toml [tool.ruff]`) and Prettier + ESLint for frontend.

**Module-level LLM config (no persistence):**
- Issue: LLM backend config stored as `_current_config = LLMBackendConfig()` module-level variable in `routers/llm.py`. Lost on server restart.
- Files: `backend/app/routers/llm.py` line 12
- Impact: User must reconfigure LLM backend every time the server restarts. Frontend localStorage partially mitigates this.
- Fix approach: Persist config to a JSON file or SQLite table, or accept as single-session state.

**All Pydantic schemas in single file:**
- Issue: `schemas.py` is 209 lines with all Pydantic models (request, response, LLM, graph). As the app grows, this will become unwieldy.
- Files: `backend/app/models/schemas.py`
- Impact: Harder to navigate and maintain as schema count grows.
- Fix approach: Split into `schemas/stories.py`, `schemas/llm.py`, `schemas/graph.py` when needed.

## Known Bugs

**Prunable `use_case` worktree (may be resolved):**
- Symptoms: Was previously reported as prunable with empty directory. May have been cleaned up.
- Files: `02-worktrees/use_case/` (may not exist locally)
- Fix: `git worktree prune` to clean up stale entries.

**Uninitialized `01-dev-onboarding` submodule:**
- Symptoms: The `01-dev-onboarding/` directory exists but is empty. Submodule not initialized.
- Files: `.gitmodules`, `01-dev-onboarding/`
- Impact: Low — submodule content not needed for active development.
- Fix approach: Run `git submodule update --init` if needed, or remove the submodule if no longer relevant.

## Security Considerations

**Mixed SSH/HTTPS remote protocols:**
- Risk: `origin` and `template` remotes use SSH (`git@github.com-primary:...`) while `.gitmodules` uses HTTPS (`https://github.com/...`).
- Files: `.gitmodules`, `.git/config`
- Current mitigation: SSH host alias configured in `~/.ssh/config`.
- Recommendations: Keep as-is if working. Remove `template` remote if no longer syncing.

**No `.DS_Store` in `.gitignore`:**
- Risk: macOS `.DS_Store` files may be accidentally committed.
- Files: `.gitignore` (missing explicit rule)
- Current mitigation: Likely handled by global gitignore.
- Recommendations: Add `.DS_Store` and `**/.DS_Store` to repo `.gitignore`.

**`sample.env.file` in tracked files:**
- Risk: If it contains real API keys, they'd be in git history.
- Files: `00-supporting-files/data/sample.env.file`
- Recommendations: Verify only placeholder values exist.

## Performance Bottlenecks

**Character-by-character WebSocket streaming with 10ms delay:**
- Problem: Each character of AI-generated text is sent as a separate WebSocket message with a 10ms sleep. A 150-word paragraph (~750 chars) takes ~7.5 seconds just for streaming delay.
- Files: `backend/app/routers/ws.py` lines ~165-170
- Cause: Intentional — provides a visual "typing" effect in the editor.
- Improvement path: Configurable streaming speed, or batch characters (2-3 at a time).

**Synchronous OpenAI SDK wrapped in asyncio.to_thread():**
- Problem: Each LLM call occupies a thread from the default thread pool. Multiple concurrent generations would exhaust the pool.
- Files: `backend/app/services/llm.py`
- Cause: OpenAI Python SDK is synchronous; `asyncio.to_thread()` is the standard async wrapper.
- Improvement path: Acceptable for single-user app. For multi-user, consider `asyncio.Semaphore` to limit concurrent LLM calls.

**No database connection pooling:**
- Problem: Each request opens a new SQLite connection via `get_db()`. No connection reuse.
- Files: `backend/app/models/database.py`
- Cause: aiosqlite doesn't natively pool connections; simple app doesn't need it yet.
- Improvement path: Add connection pooling if request volume increases.

**Binary files in git history:**
- Problem: 16MB+ of images and videos tracked directly in git without LFS.
- Files: `00-supporting-files/images/` (README demos, screenshots)
- Improvement path: Current size is manageable. Consider Git LFS if media grows.

## Fragile Areas

**WebSocket state management in ws.py:**
- Files: `backend/app/routers/ws.py`
- Why fragile: Single `cancel_flag` boolean and `current_draft_id` tracked per connection. Race conditions possible if messages arrive during generation. No explicit state machine.
- Safe modification: Add explicit state enum (IDLE, GENERATING, STREAMING) with transitions.

**Active path JSON stored as TEXT in SQLite:**
- Files: `backend/app/db/migrations/001_initial.sql` (active_path column)
- Why fragile: JSON string parsed on every read. No referential integrity between active_path node IDs and actual nodes. If a node is deleted without updating active_path, the path breaks.
- Safe modification: Always validate active_path entries exist when loading. Consider a junction table instead.

**Story text concatenation for LLM context:**
- Files: `backend/app/routers/ws.py` (`_build_story_text()`)
- Why fragile: Concatenates all nodes in active_path with `\n\n` separator. Long stories may exceed LLM context window silently. No truncation or summarization strategy.
- Safe modification: Add token counting and context window limits.

**Frontend story caching in memory:**
- Files: `frontend/src/lib/stores/story.svelte.ts`
- Why fragile: `loadedStories` Map caches full story data. No cache invalidation — stale data possible if backend is modified externally.
- Safe modification: Add cache TTL or explicit refresh mechanism.

**Cross-branch root README updates:**
- Files: `README.md` (on master)
- Why fragile: Requires stash/checkout/edit/commit/checkout-back pattern. Risk of losing uncommitted changes.
- Safe modification: Always verify current branch before cross-branch edits.

## Scaling Limits

**Single-user SQLite database:**
- Current capacity: Designed for one user. SQLite handles concurrent reads well but concurrent writes are serialized.
- Limit: Not suitable for multi-user deployment without switching to PostgreSQL.
- Scaling path: Accept as-is for personal use. If multi-user needed, migrate to PostgreSQL with asyncpg.

**Story tree depth and breadth:**
- Current capacity: No explicit limits on tree depth or number of branches per node.
- Limit: Deep trees will slow graph rendering (d3-hierarchy recomputation). Wide trees (many branches per node) make the SVG hard to read.
- Scaling path: Add pagination or virtualization for the graph visualizer. Limit tree breadth in UI.

**No pagination on story/node lists:**
- Current capacity: `GET /api/stories` returns all stories. `GET /api/stories/{id}` returns all nodes.
- Limit: Will slow down with hundreds of stories or thousands of nodes.
- Scaling path: Add pagination parameters (limit, offset) to list endpoints.

## Dependencies at Risk

**OpenAI SDK version sensitivity:**
- Risk: `client.beta.chat.completions.parse()` is a beta API. Future breaking changes possible.
- Impact: Structured output parsing is core to the application. A breaking change would halt generation.
- Migration plan: Pin OpenAI SDK version. Watch changelog for beta API changes.

**Tiptap 3 major version:**
- Risk: Tiptap v3 is a major version. Extension API may change in future minor/patch updates.
- Impact: Custom provenance mark extension (`provenance.ts`) uses internal ProseMirror APIs.
- Migration plan: Pin Tiptap version. Test upgrades carefully.

**Svelte 5 runes API stability:**
- Risk: Svelte 5 runes (`$state`, `$derived`, `$effect`) are relatively new. Breaking changes unlikely but possible.
- Impact: All frontend state management uses runes.
- Migration plan: Pin Svelte version. Follow Svelte changelog.

## Missing Critical Features

**No automated tests:**
- Problem: Zero test files exist. No test framework configured for backend or frontend.
- Blocks: Cannot verify regressions after changes. Manual testing only.
- Recommendation: Add pytest for backend, vitest for frontend when starting next development cycle.

**No error recovery for failed generations:**
- Problem: If the backend crashes mid-generation, the draft node remains in the database as `is_draft=1` with empty content. No cleanup mechanism.
- Blocks: Orphaned draft nodes accumulate over time.
- Recommendation: Add a startup cleanup that removes empty draft nodes, or a "clear drafts" admin endpoint.

**No story import:**
- Problem: Stories can be created and exported (markdown) but cannot be imported from external files.
- Blocks: No way to migrate stories between databases or restore from exports.
- Recommendation: Add markdown import endpoint.

**Frontend not built for production:**
- Problem: Frontend runs via `bun run dev` (Vite dev server). No production build pipeline configured for serving the SPA.
- Blocks: Requires both backend and frontend dev servers running separately.
- Recommendation: Build frontend to static files, serve from FastAPI via `StaticFiles` mount.

---

*Concerns audit: 2026-04-09*
