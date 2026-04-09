# Architecture

**Analysis Date:** 2026-02-13

## Pattern Overview

**Overall:** Multi-branch template repository with git worktree-based parallel development

**Key Characteristics:**
- Two distinct branch families with completely different file trees: template branches (`master`, `development`) and project branches (forked from `00-experiments`)
- Git worktrees enable simultaneous work on multiple experiment/feature branches without checkout switching
- No application runtime on the template branches — `master`/`development` are pure scaffolding; all code lives on project branches
- GSD AI orchestrator serves as the automation layer — no shell scripts or CLI tools; workflow is encoded in `.planning/` docs
- Each project branch is self-contained and self-documenting after creation

## Branch Families

**Template Family (`master`, `development`):**
- Purpose: Repository scaffolding, dev logs, supporting files, worktree container, GSD planning
- Location: Root worktree at `/Users/progressedd/personal-projects/LAND.E`
- Contains: Numbered directories (`00-dev-log/`, `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`), `.planning/`, `.foam/`, `LICENSE`, root `README.md`
- The `development` branch is the current active branch on the root worktree
- The `master` branch has an older `03-app/` directory (removed from `development`)
- Depends on: Nothing — provides structure only
- Used by: All project branches inherit the organizational context

**Base Environment (`00-experiments`):**
- Purpose: Inheritable Python 3.13 + uv development environment that all new project branches start from
- Location: `02-worktrees/00-experiments/` (worktree)
- Contains: `pyproject.toml`, `uv.lock`, `.python-version`, `sandbox.ipynb`, `.gitignore`
- File tree is completely different from `master` — no numbered directories, no template structure
- Depends on: Nothing
- Used by: All project branches fork from this branch

**Project Branch Instances (per-experiment):**
- Purpose: Self-contained, self-documenting experiment/feature projects
- Location: `02-worktrees/<branch-name>/` (each in its own worktree)
- Contains: Inherited Python env + project-specific code, populated `README.md`, renamed `pyproject.toml`
- Active instances: `demo-marimo-app`, `experiments-with-models`, `marimo-tests`, `use_case`
- Depends on: `00-experiments` (at creation time only — independent after forking)
- Used by: End users / developers working on experiments

## Layers

**Planning & Documentation Layer:**
- Purpose: Project management, roadmapping, research, codebase analysis for GSD AI orchestration
- Location: `.planning/`
- Contains: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `config.json`, `research/`, `phases/`, `codebase/`
- Depends on: Nothing
- Used by: GSD orchestrator (Claude/Codex) reads these to understand project context and execute workflows

**Dev Log Layer:**
- Purpose: Daily development notes, progress tracking, learning documentation
- Location: `00-dev-log/`
- Contains: Date-stamped markdown files (`YYYY-MM-DD.md`), a template (`00-template.md`)
- Depends on: `.foam/templates/` for daily note creation via VS Code Foam extension
- Used by: Developer for reflection and knowledge capture

**Supporting Files Layer:**
- Purpose: Shared data files, environment configuration samples, screenshots/images for documentation
- Location: `00-supporting-files/`
- Contains: `data/sample.env.file`, `images/` organized by date and purpose (e.g., `images/2025-12-28/`, `images/README/`)
- Depends on: Nothing
- Used by: Dev logs (image references), README (screenshots, demo videos)

**Worktree Container Layer:**
- Purpose: Filesystem container for all git worktree checkouts
- Location: `02-worktrees/`
- Contains: Worktree directories (gitignored), `README.md` with usage instructions
- Key constraint: Contents are gitignored (`02-worktrees/*`) except `README.md`
- Depends on: Git worktree system
- Used by: All project branch instances

## Data Flow

**New Project Creation (primary flow):**

1. GSD reads `.planning/PROJECT.md`, `REQUIREMENTS.md`, and `ROADMAP.md` to understand the template system
2. Pre-flight: `git fetch origin 00-experiments` + `git worktree list --porcelain` to check for duplicates
3. Atomic branch+worktree: `git worktree add -b <name> 02-worktrees/<name> 00-experiments`
4. README population: `string.Template.safe_substitute()` replaces `$placeholder` variables in inherited `README.md`
5. pyproject.toml update: `re.sub()` replaces `name` field with project name
6. Environment setup: `uv sync` creates `.venv` in the worktree
7. Commit on the new branch
8. (Optional) Root README on `master` updated with new project entry via stash/checkout pattern

**Context Inheritance Flow:**

```
00-experiments (base)           →  <project-branch> (inherits, then customizes)
├── pyproject.toml (template)   →  pyproject.toml (name/description updated)
├── .python-version (3.13)      →  .python-version (inherited)
├── uv.lock (locked deps)       →  uv.lock (inherited, updated with new deps)
├── sandbox.ipynb (starter)     →  sandbox.ipynb (inherited, may be extended)
├── README.md (template)        →  README.md (populated with project context)
└── .gitignore (Python)         →  .gitignore (inherited)
```

**State Management:**
- Project state tracked in `.planning/STATE.md` — current phase, progress, performance metrics
- No runtime state — this is a template repo, not an application
- Git branches are the primary state mechanism — each branch is an independent project snapshot
- Worktree list (`git worktree list`) is the source of truth for active projects

## Key Abstractions

**Template Sentinel Pattern:**
- Purpose: Idempotency detection for README population — prevents clobbering user edits on re-run
- Implementation: `<!-- TEMPLATE: REPLACE ME -->` comment as first line of README template on `00-experiments`
- Pattern: Check for sentinel presence before overwriting; remove sentinel after population
- Files: `README.md` on `00-experiments` branch (template), populated `README.md` on project branches

**$Placeholder Variables:**
- Purpose: Machine-populatable fields in README template using Python `string.Template`
- Variables: `$project_name`, `$description`, `$branch_name`, `$created_date`
- Pattern: `string.Template.safe_substitute()` — leaves unresolved placeholders intact
- Files: `README.md` template on `00-experiments` branch

**Numbered Directory Convention:**
- Purpose: Organizational ordering — directories sort predictably in file explorers and `ls` output
- Pattern: `NN-descriptive-name` where NN is a two-digit zero-padded number
- Examples: `00-dev-log/`, `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`
- Used on: `master`/`development` branches only — project branches do not use numbered directories

**GSD Planning System:**
- Purpose: AI-driven project management — plans, executes, and tracks development phases
- Pattern: Research → Roadmap → Plan → Execute → Summarize → UAT
- Files: `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/phases/*/`
- Key: `.planning/config.json` configures GSD mode (`yolo`), depth (`standard`), and model profile (`codex`)

## Entry Points

**Root Worktree (template/scaffolding):**
- Location: `/Users/progressedd/personal-projects/LAND.E/`
- Branch: `development` (currently checked out)
- Responsibilities: GSD planning, dev logs, supporting files, worktree management

**Project Worktrees (per-experiment):**
- Location: `02-worktrees/<branch-name>/`
- Triggers: `git worktree add -b <name> 02-worktrees/<name> 00-experiments`
- Responsibilities: Self-contained Python project with its own code, deps, and docs

**Marimo App (on project branches):**
- Location: `app.py` (on branches like `demo-marimo-app`)
- Trigger: `uv run marimo run 03-app/app.py` (legacy path) or `uv run marimo run app.py` (in worktree)
- Responsibilities: Interactive story generation UI using LLMs via Ollama/OpenAI

## Error Handling

**Strategy:** Prevention via pre-flight checks + idempotency guards

**Patterns:**
- Duplicate branch/worktree detection via `git worktree list --porcelain` before creation
- Sentinel-based idempotency for README population — only overwrites if `<!-- TEMPLATE: REPLACE ME -->` is present
- Default-value check for pyproject.toml — only replaces `name` if it still matches the template default
- Atomic `git worktree add -b` — if creation fails, neither branch nor worktree is created (no partial state)
- `uv sync` failure handling — worktree is usable without venv, user can retry manually

## Cross-Cutting Concerns

**Logging:** No structured logging — this is a template repo, not an application. Dev logs in `00-dev-log/` serve as human-written progress journals.

**Validation:** Pre-flight checks before worktree creation (duplicate detection, branch existence). Post-creation verification via `string.Template` parse tests and `tomllib` TOML validation.

**Authentication:** Not applicable — personal local development. Git SSH keys handle repository access (`git@github.com-primary:`).

**Submodule Isolation:** `01-dev-onboarding` submodule exists on `master` only. The `00-experiments` branch has no `.gitmodules` — this is critical because git worktrees have incomplete submodule support. All project branches fork from `00-experiments` to avoid this issue.

## Multi-Remote Setup

**`origin`:** `git@github.com-primary:progressEdd/LAND.E.git` — the project repository
**`template`:** `git@github.com-primary:progressEdd/project-template.git` — upstream template repo for inheriting worktree infrastructure updates

The `template` remote enables pulling organizational improvements (worktree README updates, `.gitignore` changes) from the shared template repo while keeping project-specific content on `origin`.

---

*Architecture analysis: 2026-02-13*
