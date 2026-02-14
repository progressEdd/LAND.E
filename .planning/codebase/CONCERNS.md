# Codebase Concerns

**Analysis Date:** 2026-02-13

## Tech Debt

**Root worktree on wrong branch:**
- Issue: The root worktree (repo root) is checked out on `development`, not `master`. The `development` branch is 12 commits ahead of `master` and has no upstream tracking remote configured. The `reorganized-branch` points to the same commit (`c9121f1`) as `development`, suggesting `development` is a rename or continuation of `reorganized-branch` without cleanup.
- Files: Root `.git/HEAD`, `git config --local`
- Impact: The root README update workflow (Phase 3 of the GSD roadmap) expects the root to be on `master`. Cross-branch edits require stash/checkout/commit/checkout-back pattern, adding fragility. New contributors cloning the repo will see `master` content, not the current working state. `development` has no remote tracking, so `git push` from the root will fail without explicit `--set-upstream`.
- Fix approach: Decide whether `development` should merge into `master` and become the new HEAD. Set up remote tracking for `development` (`git push -u origin development`), or fast-forward `master` to `development` and switch the root worktree back to `master`. Remove `reorganized-branch` if it's a duplicate.

**Stale `03-app/` references in README and dev logs:**
- Issue: `README.md` references `uv run marimo run 03-app/app.py` but `03-app/` was removed from the `development` branch. Dev log `00-dev-log/2025-12-29.md` references `../03-app/head.html`. These are broken paths.
- Files: `README.md` (line 29), `00-dev-log/2025-12-29.md` (line 121)
- Impact: Users following the README build instructions will get a file-not-found error. The app code now lives on the `demo-marimo-app` worktree branch, but the README doesn't reflect this.
- Fix approach: Update `README.md` to point to the correct branch/worktree location. Dev log references are historical and can be left as-is (they document what was true at the time), but add a note that `03-app/` was moved.

**Placeholder `pyproject.toml` description:**
- Issue: The root `pyproject.toml` still has `description = "Add your description here"` — the default uv scaffold placeholder.
- Files: `pyproject.toml` (line 4)
- Impact: Minor — no functional impact, but signals an unfinished setup. Anyone inspecting the project metadata sees a placeholder.
- Fix approach: Update to a real description, e.g., `description = "Local AI story writer experiments using Ollama and Marimo"`.

**Previous codebase docs committed then deleted:**
- Issue: The `development` branch has 7 codebase analysis files (ARCHITECTURE.md, CONCERNS.md, CONVENTIONS.md, INTEGRATIONS.md, STACK.md, STRUCTURE.md, TESTING.md) in git history at HEAD, but they are staged as deleted in the working tree. These were written for the template repo context, not the current ai-invasion project. They are being replaced by this fresh analysis.
- Files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/STACK.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/TESTING.md`
- Impact: Until the deletions are committed, `git status` shows 7 deleted files as unstaged changes. This creates noise and could cause confusion if someone runs `git checkout .` or `git restore .` — the old template-focused docs would reappear.
- Fix approach: Commit the deletions alongside the new codebase analysis documents.

## Known Bugs

**Prunable `use_case` worktree:**
- Symptoms: `git worktree list` shows `use_case` as `prunable` with message "gitdir file points to non-existent location". The worktree directory at `02-worktrees/use_case/` is empty (no files, just `.` and `..`).
- Files: `.git/worktrees/use_case/` (admin directory), `02-worktrees/use_case/` (empty)
- Trigger: The worktree's `.git` file (which should point back to the main repo's admin directory) is missing or the admin entry's `gitdir` points to a path that no longer exists. Likely caused by manual deletion of the worktree directory without using `git worktree remove`.
- Workaround: Run `git worktree prune` to clean up the stale admin entry, then `git branch -d use_case` if the branch is no longer needed. The `use_case` branch tracks `template/00-experiments` (not `origin`), suggesting it was created from the template remote and may be obsolete.

**Uninitialized `01-dev-onboarding` submodule:**
- Symptoms: The `01-dev-onboarding/` directory exists but is empty (no files). `git submodule status` shows a `-` prefix indicating the submodule is not initialized.
- Files: `.gitmodules`, `01-dev-onboarding/`
- Trigger: After cloning, `git submodule init && git submodule update` was never run. The submodule URL in `.gitmodules` uses HTTPS (`https://github.com/progressEdd/dev-onboarding.git`) while the origin remote uses SSH (`git@github.com-primary:...`), which could also cause auth issues during initialization.
- Workaround: Run `git submodule update --init` if the submodule content is needed. If the submodule is no longer relevant to this project (it was inherited from the template), consider removing it with `git rm 01-dev-onboarding && git config --remove-section submodule.01-dev-onboarding`.

## Security Considerations

**Mixed SSH/HTTPS remote protocols:**
- Risk: The `origin` and `template` remotes use different SSH host aliases (`git@github.com-primary:...`) while `.gitmodules` uses HTTPS (`https://github.com/...`). The `template` remote also has a mismatch — `git config` shows `git@github.com-primary:progressEdd/project-template.git` but `.gitmodules` references `https://github.com/progressEdd/dev-onboarding.git`.
- Files: `.gitmodules`, `.git/config`
- Current mitigation: The SSH host alias `github.com-primary` is configured in the user's `~/.ssh/config`, which handles key routing. This is a valid multi-account SSH pattern.
- Recommendations: Ensure `.gitmodules` URL is consistent with the SSH pattern if submodule is kept. If the submodule is removed, this becomes moot.

**`.DS_Store` not in `.gitignore`:**
- Risk: macOS `.DS_Store` files contain directory metadata (icon positions, view settings). While not a direct security risk, they can leak directory structure information and are unnecessary tracked files. Currently `.DS_Store` exists in the working tree but is not tracked by git (it is gitignored via the global gitignore or OS-level config, not the repo's `.gitignore`).
- Files: `.gitignore` (missing `.DS_Store` rule), `.DS_Store` (present in working tree)
- Current mitigation: The file is currently ignored (verified via `git check-ignore .DS_Store`), likely by a global gitignore. However, this relies on each contributor having the same global config.
- Recommendations: Add `.DS_Store` and `**/.DS_Store` to the repo's `.gitignore` for explicit, portable exclusion.

**`sample.env.file` in tracked supporting files:**
- Risk: A file at `00-supporting-files/data/sample.env.file` is tracked in git. If it contains actual secrets or API keys (even as examples), they are committed to history.
- Files: `00-supporting-files/data/sample.env.file`
- Current mitigation: The `.gitignore` excludes `.env` but `sample.env.file` does not match that pattern, so it is tracked. This is likely intentional (a template showing env var structure), but the contents should be verified to contain only placeholder values.
- Recommendations: Verify the file contains only placeholder/example values. If it contains real keys, remove it from git history with `git filter-repo`.

## Performance Bottlenecks

**Binary files in git history (no Git LFS):**
- Problem: The repository tracks 16MB of images and a 10MB MP4 video file directly in git objects. Every clone downloads all of this, even if the files are never needed.
- Files: `00-supporting-files/images/README/novelai-killer-demo.mp4` (10.4MB), `00-supporting-files/images/` (16MB total), various `.ipynb` files on worktree branches (~1MB each with embedded outputs)
- Cause: Binary files are committed directly to git without Git LFS. The MP4 alone is 10.4MB and will remain in the object store forever, even if deleted from HEAD.
- Improvement path: For a personal project, 15MB of git objects is tolerable. If the repo grows with more screenshots/demos, consider: (1) enabling Git LFS for `*.mp4`, `*.png` patterns, (2) using external hosting (GitHub releases, S3) for demo videos, (3) compressing screenshots before committing.

## Fragile Areas

**Cross-branch root README updates (Phase 3 workflow):**
- Files: `README.md` (on `master` branch), `.planning/STATE.md`
- Why fragile: Updating the root README requires the root worktree to be on `master`. The current root worktree is on `development`. The Phase 3 workflow used a stash/checkout/edit/commit/checkout-back pattern, which can fail if there are uncommitted changes, merge conflicts, or if the user interrupts the process mid-way.
- Safe modification: Always verify current branch with `git branch --show-current` before attempting cross-branch edits. Use `git stash push -m "cross-branch-edit"` with named stashes to avoid the shared-stash confusion documented in `.planning/research/PITFALLS.md`.
- Test coverage: No automated tests exist. The workflow was verified manually during Phase 3 execution.

**Worktree admin directory naming inconsistency:**
- Files: `.git/worktrees/` (admin directory)
- Why fragile: As documented in `.planning/research/PITFALLS.md`, the admin directory name is derived from the worktree path basename at creation time, not the branch name. The `00-experiments` worktree's admin directory is named `experiments` (from its original creation path). Any automation that assumes admin-dir == branch-name will break.
- Safe modification: Always use `git worktree list --porcelain` to discover worktree-to-branch mappings. Never derive branch names from directory names.
- Test coverage: None.

## Scaling Limits

**Worktree count and disk usage:**
- Current capacity: 5 active worktrees (00-experiments, demo-marimo-app, experiments-with-models, marimo-tests, use_case). Each worktree with a `.venv` can be 50-200MB.
- Limit: Git handles many worktrees efficiently (shared object store), but disk space grows linearly. At 20+ worktrees with venvs, expect 1-4GB of disk usage.
- Scaling path: Use `git worktree remove` to clean up completed experiments. Run `uv cache clean` periodically. The `use_case` worktree is already prunable and should be cleaned up as a precedent.

**Git object database growth from binary files:**
- Current capacity: 14.15MB in pack files, 193 loose objects.
- Limit: Git performance degrades noticeably above ~1GB object stores, especially for operations like `git gc`, `git clone`, and `git fetch`.
- Scaling path: Current size is fine. Monitor growth if more screenshots/videos are added. Consider Git LFS before the object store exceeds 100MB.

## Dependencies at Risk

**Root `pyproject.toml` dependencies are vestigial:**
- Risk: The root `pyproject.toml` lists `ipykernel`, `marimo`, `ollama`, and `openai` as dependencies, but the root branch (`development`/`master`) has no application code — all app code lives on worktree branches. These dependencies exist from before the worktree reorganization and serve no purpose on the root branch.
- Impact: `uv sync` on the root installs unnecessary packages. The `uv.lock` (963 lines) locks dependencies that aren't used here.
- Migration plan: Either (1) strip the root `pyproject.toml` to minimal dependencies (just what's needed for template management, if anything), or (2) accept the bloat since the root isn't where active development happens. If stripped, the worktree branches inherit their own `pyproject.toml` from `00-experiments` anyway.

**`template` remote may diverge:**
- Risk: The `template` remote (`git@github.com-primary:progressEdd/project-template.git`) is a separate repo. Changes to the template repo won't automatically propagate to this repo. The `use_case` branch tracks `template/00-experiments`, not `origin/00-experiments`, creating confusion about which remote is authoritative.
- Impact: Template updates require manual `git fetch template` and selective merging. The `vibe-coding-gsd` branch was merged from `template` into `development`, suggesting this has already happened at least once.
- Migration plan: Decide if the template remote is still needed. If this repo has fully diverged from the template, remove the remote: `git remote remove template`. If ongoing sync is desired, document the merge workflow.

## Missing Critical Features

**No automated tests:**
- Problem: Zero test files exist anywhere in the repository. The GSD workflow was validated manually (UAT in `.planning/phases/01-template-preparation/01-UAT.md`), but there are no repeatable automated tests for any functionality.
- Blocks: Cannot verify that worktree creation, README templating, or pyproject.toml updates work correctly after code changes. Regressions will be discovered manually.

**No automation scripts exist:**
- Problem: The GSD workflow (branch creation, file population, root README update) was executed interactively by an AI orchestrator. There are no standalone scripts that encode this workflow. If the GSD system is unavailable, the workflow must be performed entirely manually.
- Blocks: Workflow reproducibility depends on the AI orchestrator having access to `.planning/` context. A human without GSD cannot easily replicate the automated workflow.

**`development` branch not pushed to origin:**
- Problem: The `development` branch has no upstream tracking. `git push` will fail. The 12 commits of GSD planning/research work exist only locally.
- Blocks: No remote backup of the current working branch. A disk failure would lose all `.planning/` work.

## Test Coverage Gaps

**Entire codebase is untested:**
- What's not tested: Everything. No test framework is configured. No test files exist. No CI/CD pipeline exists.
- Files: All files in the repository
- Risk: Any changes to the worktree workflow, template system, or project structure could introduce regressions that go undetected. The GSD UAT (`.planning/phases/01-template-preparation/01-UAT.md`) was a one-time manual verification.
- Priority: Low — this is a personal project template with no application logic on the root branch. The worktree branches may have their own test needs, but the template infrastructure itself is simple enough that manual verification is acceptable for now. If automation scripts are added (see "Missing Critical Features"), tests should accompany them.

---

*Concerns audit: 2026-02-13*
