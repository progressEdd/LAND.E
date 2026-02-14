# Codebase Structure

**Analysis Date:** 2026-02-13

## Directory Layout

```
LAND.E/                          # Root worktree (development branch)
├── .foam/                            # VS Code Foam extension templates
│   └── templates/                    # Note templates for daily logs
│       ├── daily-note.md             # Date-stamped daily note template
│       └── new-template.md           # Generic Foam template
├── .planning/                        # GSD AI orchestrator planning system
│   ├── codebase/                     # Codebase analysis documents (this file lives here)
│   │   ├── ARCHITECTURE.md           # Architecture patterns and data flows
│   │   └── STRUCTURE.md              # Directory layout and file locations
│   ├── phases/                       # Execution phase plans and summaries
│   │   └── 01-template-preparation/  # Phase 1 artifacts
│   │       ├── 01-01-PLAN.md         # Plan for README template creation
│   │       ├── 01-01-SUMMARY.md      # Post-execution summary
│   │       └── 01-UAT.md             # User acceptance test results
│   ├── research/                     # Domain research documents
│   │   ├── ARCHITECTURE.md           # Architecture research (git worktrees, components)
│   │   ├── FEATURES.md               # Feature landscape and prioritization
│   │   ├── PITFALLS.md               # Known pitfalls and prevention strategies
│   │   ├── STACK.md                  # Technology stack research
│   │   └── SUMMARY.md                # Executive research summary
│   ├── config.json                   # GSD configuration (mode, depth, model)
│   ├── PROJECT.md                    # Project definition and requirements
│   ├── REQUIREMENTS.md               # Formal requirements with traceability
│   ├── ROADMAP.md                    # Phase definitions and progress
│   └── STATE.md                      # Current execution state and metrics
├── 00-dev-log/                       # Development journal entries
│   ├── 00-template.md                # Template for new dev log entries
│   ├── 2025-12-28.md                 # Dev log: UI tweaks, marimo styling
│   └── 2025-12-29.md                 # Dev log: Firefox screenshot fixes
├── 00-supporting-files/              # Shared data and media assets
│   ├── data/                         # Configuration samples
│   │   └── sample.env.file           # Environment variable template (DO NOT read)
│   └── images/                       # Screenshots and media
│       ├── 2025-12-28/               # Date-organized screenshots
│       ├── 2025-12-29/               # Date-organized screenshots
│       └── README/                   # README-specific images and demos
├── 01-dev-onboarding/                # Git submodule (empty on worktree branches)
├── 02-worktrees/                     # Git worktree container (contents gitignored)
│   └── README.md                     # Worktree usage instructions
├── .gitignore                        # Python-focused gitignore + worktree exclusions
├── .gitmodules                       # Submodule config (01-dev-onboarding)
├── .python-version                   # Python 3.13 version pin
├── LICENSE                           # Project license
├── pyproject.toml                    # Project metadata and dependencies
├── README.md                         # Root repo README with project overview
└── uv.lock                           # Locked dependency resolution
```

## Directory Purposes

**`.planning/`:**
- Purpose: GSD AI orchestrator working directory — all project management happens here
- Contains: Project definition, requirements, roadmap, state, research, phase plans, codebase analysis
- Key files: `PROJECT.md` (what to build), `STATE.md` (where we are), `ROADMAP.md` (how to get there)
- Subdirectory `codebase/`: Machine-generated codebase analysis for GSD context loading
- Subdirectory `phases/`: One directory per phase, containing plans (`NN-NN-PLAN.md`), summaries (`NN-NN-SUMMARY.md`), and UAT (`NN-UAT.md`)
- Subdirectory `research/`: Domain research organized by topic (`ARCHITECTURE.md`, `FEATURES.md`, `PITFALLS.md`, `STACK.md`, `SUMMARY.md`)

**`.foam/templates/`:**
- Purpose: VS Code Foam extension templates for creating new notes
- Contains: `daily-note.md` (date-stamped template with `${CURRENT_YEAR}` variables), `new-template.md` (generic template)
- Used with: VS Code command `Foam: Create New Note From Template`

**`00-dev-log/`:**
- Purpose: Daily development journal — progress tracking, learning notes, decision rationale
- Contains: Date-stamped markdown files following `YYYY-MM-DD.md` naming
- Template: `00-template.md` provides the base structure (sections: Overall Progress, Elaboration)
- Convention: Entries reference images from `00-supporting-files/images/<date>/`

**`00-supporting-files/`:**
- Purpose: Shared assets that support documentation — screenshots, sample configs, demo media
- Contains: `data/` for configuration templates, `images/` for screenshots organized by date
- Key constraint: `sample.env.file` exists in `data/` — note existence only, never read contents
- Images follow `images/<date>/` or `images/<purpose>/` naming

**`01-dev-onboarding/`:**
- Purpose: Git submodule pointing to `https://github.com/progressEdd/dev-onboarding.git`
- Status: Empty directory on worktree branches (submodules are incompatible with git worktrees)
- Exists only on `master`/`development` branches — project branches forked from `00-experiments` do not have this

**`02-worktrees/`:**
- Purpose: Container for all git worktree checkouts — keeps the root clean
- Contents: Gitignored (`02-worktrees/*` in `.gitignore`) except `README.md`
- Active worktrees: `00-experiments`, `demo-marimo-app`, `experiments-with-models`, `marimo-tests`, `use_case`
- Convention: Worktree path basename must match branch name exactly

## Key File Locations

**Entry Points:**
- `README.md`: Root repo overview, project description, active experiments table
- `.planning/PROJECT.md`: GSD project definition — the "what to build" document
- `.planning/STATE.md`: Current execution position — the "where are we" document
- `02-worktrees/README.md`: Worktree usage guide with creation/removal commands

**Configuration:**
- `pyproject.toml`: Python project metadata, dependencies (`ipykernel`, `marimo`, `ollama`, `openai`)
- `.python-version`: Python version pin (`3.13`)
- `uv.lock`: Locked dependency resolution for reproducible environments
- `.gitignore`: Python-focused with worktree exclusions, marimo `__marimo__` exclusion
- `.gitmodules`: Submodule reference (`01-dev-onboarding`)
- `.planning/config.json`: GSD mode (`yolo`), depth (`standard`), model profile (`codex`)

**Core Planning:**
- `.planning/REQUIREMENTS.md`: Formal requirements with IDs (TMPL-01, WKTR-01, etc.) and traceability
- `.planning/ROADMAP.md`: Phase definitions, success criteria, progress tracking
- `.planning/research/SUMMARY.md`: Executive research summary with confidence assessments
- `.planning/research/PITFALLS.md`: Known git worktree pitfalls and prevention strategies

**Documentation:**
- `00-dev-log/2025-12-28.md`: UI tweaks, marimo styling, ChatGPT-assisted development
- `00-dev-log/2025-12-29.md`: Firefox screenshot fix, CSS overrides for marimo

## Naming Conventions

**Files:**
- Markdown docs: `UPPERCASE.md` for GSD system docs (`PROJECT.md`, `REQUIREMENTS.md`, `STATE.md`)
- Dev logs: `YYYY-MM-DD.md` (e.g., `2025-12-28.md`)
- Phase plans: `NN-NN-PLAN.md` where first NN is phase number, second is plan number (e.g., `01-01-PLAN.md`)
- Phase summaries: `NN-NN-SUMMARY.md` (e.g., `01-01-SUMMARY.md`)
- UAT files: `NN-UAT.md` (e.g., `01-UAT.md`)
- Config files: lowercase with dots (`config.json`, `pyproject.toml`, `.python-version`)
- Templates: `00-template.md` (zero-prefix signals "template, not content")

**Directories:**
- Numbered prefix convention: `NN-descriptive-name` (e.g., `00-dev-log`, `01-dev-onboarding`, `02-worktrees`)
- Zero-prefix (`00-`) for shared/template directories
- Planning subdirs: lowercase plural (`phases/`, `research/`, `codebase/`)
- Phase dirs: `NN-kebab-case` matching phase name (e.g., `01-template-preparation`)
- Image dirs: `YYYY-MM-DD` for date-organized screenshots, `README` for purpose-organized

**Branches:**
- `00-experiments`: Base environment branch (numbered prefix matches directory convention)
- Project branches: `kebab-case` descriptive names (e.g., `demo-marimo-app`, `experiments-with-models`)
- Template branches: `master` (main), `development` (active work)
- No strict naming enforcement — user picks meaningful names (per anti-feature A4 in research)

## Where to Add New Code

**New Experiment/Feature Project:**
- Create via: `git worktree add -b <name> 02-worktrees/<name> 00-experiments`
- Primary code: `02-worktrees/<name>/` (Python files, notebooks, app code)
- Dependencies: `02-worktrees/<name>/pyproject.toml` (update name, add deps with `uv add`)
- Tests: Co-located in the worktree (no test convention established yet)
- README: Auto-populated from template on `00-experiments` branch

**New Dev Log Entry:**
- Location: `00-dev-log/YYYY-MM-DD.md`
- Template: Copy from `00-dev-log/00-template.md` or use Foam's `Create New Note From Template`
- Screenshots: Save to `00-supporting-files/images/YYYY-MM-DD/`

**New GSD Phase:**
- Phase directory: `.planning/phases/NN-phase-name/`
- Plan files: `.planning/phases/NN-phase-name/NN-PP-PLAN.md`
- Summary files: `.planning/phases/NN-phase-name/NN-PP-SUMMARY.md`
- UAT file: `.planning/phases/NN-phase-name/NN-UAT.md`

**New Research Document:**
- Location: `.planning/research/TOPIC.md`
- Follow existing format: confidence levels, sources, implications for roadmap

**New Codebase Analysis:**
- Location: `.planning/codebase/DOCNAME.md`
- Follow template structure from GSD mapping system

**New Supporting Data:**
- Configuration samples: `00-supporting-files/data/`
- Images: `00-supporting-files/images/<date-or-purpose>/`

## Special Directories

**`.planning/`:**
- Purpose: GSD AI orchestrator working directory
- Generated: Partially (codebase docs are AI-generated; project docs are human+AI co-created)
- Committed: Yes — essential for GSD context continuity across sessions

**`02-worktrees/`:**
- Purpose: Git worktree checkout container
- Generated: Yes (created by `git worktree add`)
- Committed: No — contents are gitignored; only `README.md` is tracked

**`.venv/`:**
- Purpose: Python virtual environment
- Generated: Yes (created by `uv sync`)
- Committed: No — gitignored; each worktree has its own `.venv`

**`01-dev-onboarding/`:**
- Purpose: Git submodule for developer onboarding resources
- Generated: No (manually configured)
- Committed: Yes (as submodule reference), but empty in worktree checkouts due to git worktree+submodule incompatibility

**`.foam/`:**
- Purpose: VS Code Foam extension configuration
- Generated: No (manually configured)
- Committed: Yes

## Branch-Specific File Trees

The `master`/`development` branches and `00-experiments` branch have **completely different file trees**. Use this reference when working across branches:

**`development` branch (root worktree):**
```
.foam/, .planning/, 00-dev-log/, 00-supporting-files/,
01-dev-onboarding/, 02-worktrees/,
.gitignore, .gitmodules, .python-version, LICENSE, README.md,
pyproject.toml, uv.lock
```

**`00-experiments` branch (base for all projects):**
```
.gitignore, .python-version, pyproject.toml, sandbox.ipynb,
uv.lock, README.md (template with $placeholders)
```

**Project branches (e.g., `demo-marimo-app`):**
```
.gitignore, .python-version, pyproject.toml, uv.lock,
README.md, app.py, custom.css, head.html, layouts/, __marimo__/
```

**Critical rule:** Never branch project work from `master`/`development`. Always branch from `00-experiments` to get the clean Python environment without numbered directories or submodule references.

---

*Structure analysis: 2026-02-13*
