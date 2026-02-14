# Coding Conventions

**Analysis Date:** 2026-02-13

## Overview

This is a **documentation-and-workflow template repository**, not a traditional application codebase. The master branch contains zero Python source files — all executable code lives on feature/experiment branches accessed via git worktrees in `02-worktrees/`. Conventions here cover the template repo's organizational patterns, markdown documentation style, git practices, and the Python patterns established on the `00-experiments` base branch.

## Naming Patterns

**Directories:**
- Use `XX-descriptive-name` numbered prefix convention for top-level directories
- Numbers establish visual ordering: `00-dev-log/`, `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`
- Prefix `00-` is reserved for shared/template resources
- Use lowercase with hyphens for multi-word names

**Branches:**
- Use `XX-descriptive-name` numbered prefix matching the directory convention
- `00-experiments` is the base branch all project branches fork from
- `master` is the template/scaffolding branch — never branch from it for project work
- Feature/experiment branches use lowercase with hyphens: `vibe-coding`, `worktrees`

**Files:**
- Markdown files: lowercase with hyphens for dev logs (`2025-12-28.md`), UPPERCASE for planning docs (`PROJECT.md`, `ROADMAP.md`, `STATE.md`)
- Planning doc naming: `{PHASE_NUMBER}-{PLAN_NUMBER}-{TYPE}.md` (e.g., `01-01-PLAN.md`, `01-01-SUMMARY.md`, `01-UAT.md`)
- Config files: lowercase (`config.json`, `pyproject.toml`)
- Template files: descriptive lowercase (`daily-note.md`, `new-template.md`, `00-template.md`)

**Python (on experiment branches):**
- Project names in `pyproject.toml`: lowercase with hyphens (`ai-invasion`, `template-repo`)
- Python version pinned in `.python-version` file: `3.13`
- Use `snake_case` for Python function names and variables (observed in research code examples)
- Use `PascalCase` for Python classes (standard Python convention — no custom override)

**Planning Documents:**
- Phase directories: `XX-descriptive-name/` (e.g., `01-template-preparation/`)
- Plan files: `{phase}-{plan}-PLAN.md`
- Summary files: `{phase}-{plan}-SUMMARY.md`
- UAT files: `{phase}-UAT.md`

## Code Style

**Formatting:**
- No linter or formatter is configured at the repo level (no `.flake8`, `ruff.toml`, `.prettierrc`, etc.)
- Python code in dev logs and research docs uses 4-space indentation (PEP 8 standard)
- No `[tool.ruff]` or `[tool.black]` section in `pyproject.toml`
- When adding new Python source files, follow PEP 8 defaults unless a formatter is configured

**Linting:**
- No linting tools are configured
- `.gitignore` includes `.ruff_cache/` suggesting ruff may be used in the future
- When introducing a linter, add configuration to `pyproject.toml` under `[tool.ruff]`

**Markdown:**
- Use ATX-style headings (`#`, `##`, `###`)
- Use `- ` for unordered lists (not `*`)
- Use `1. ` for ordered lists
- Use fenced code blocks with language identifiers (`` ```py ``, `` ```bash ``, `` ```json ``)
- Use `>` blockquotes for external references and quoted content
- Use tables with `|` pipe syntax for structured comparisons
- Include `---` separator before metadata footers

## Import Organization

**Python (observed patterns in research docs and plan examples):**

1. Standard library imports first (`re`, `string`, `pathlib`, `subprocess`, `tomllib`, `datetime`)
2. Third-party imports second (`marimo`, `ollama`, `openai`)
3. Local imports third (if any)

**Path Aliases:**
- None configured. Use relative imports within packages.

## Error Handling

**Git Automation Patterns (from research docs):**
- Use `subprocess.run()` with `check=True` to raise on non-zero exit codes
- Use `capture_output=True, text=True` for parseable output
- Validate preconditions before destructive operations (pre-flight checks)
- Use idempotency guards: check sentinel markers (`<!-- TEMPLATE: REPLACE ME -->`) before overwriting files
- Check default values before replacing (e.g., verify `name = "template-repo"` before renaming)

**Pattern:**
```python
# Pre-flight validation before destructive operations
result = subprocess.run(
    ['git', 'worktree', 'list', '--porcelain'],
    capture_output=True, text=True, check=True,
    cwd=repo_path
)
# Parse and validate before proceeding
```

**File Operations:**
- Use `pathlib.Path` for all file I/O
- Use `re.sub()` with `count=1` for targeted single-field replacements
- Raise `ValueError` if expected content is not found (e.g., `if updated == content: raise ValueError(...)`)

## Logging

**Framework:** None (no logging framework configured)

**Patterns:**
- Dev logs are manual markdown files in `00-dev-log/` with date-based naming
- Dev log entries use checkbox-style progress tracking (`- [x]`, `- [ ]`)
- Include before/after screenshots for UI changes in `00-supporting-files/images/{date}/`
- Screenshot naming: `{YYYYMMDDHHmmss}.png` timestamp format

## Comments

**When to Comment:**
- Inline comments for CSS tuning values with adjustment ranges: `"marginTop": "-6px",  # pull buttons up (tune -4px .. -10px)`
- Comments explaining "why" for non-obvious parameter choices
- No JSDoc/TSDoc patterns (no TypeScript in this repo)

**Markdown Documentation:**
- Use `<!-- TEMPLATE: REPLACE ME -->` HTML comments as sentinel markers for tooling detection
- Use `<!-- -->` comments sparingly, only for machine-readable markers

## Git Conventions

**Commit Messages:**
- Lowercase, imperative mood, no period at end
- Short and descriptive: `add README template with placeholder variables`
- GSD-generated commits may use conventional commit prefixes: `docs:`, `test:`, `chore:`
- Human commits tend to skip prefixes: `merge vibecoding from template`, `use lm studio as default lm backend`
- Use em dash (`—`) for inline explanations in commit messages: `mark all v1 phases complete — 10/10 requirements delivered`
- For plan/phase commits, include the plan reference: `docs(01-01): complete README template plan`

**Preferred commit style for new code:**
```
<verb> <what was done>
```
Examples:
- `add custom css to allow full screen screenshots`
- `update placement so that buttons don't overlap`
- `comment out css so that marimo's dev interface doesn't break`

**Branching:**
- All project branches fork from `00-experiments` (never from `master`)
- Use `git worktree add -b <name> 02-worktrees/<name> 00-experiments` for atomic branch+worktree creation
- Use `git -C <worktree-path>` for git commands targeting a specific worktree
- Fetch before branching: `git fetch origin 00-experiments`

**Gitignore:**
- Comprehensive Python `.gitignore` based on GitHub's Python template
- `02-worktrees/*` is gitignored except `02-worktrees/README.md`
- `.env` files are gitignored — use `00-supporting-files/data/sample.env.file` as a template
- Marimo folders (`__marimo__`) are gitignored

## Module/File Design

**Planning Documents:**
- Each phase gets its own directory: `.planning/phases/{phase-name}/`
- Plans, summaries, and UAT files are co-located within the phase directory
- Research docs live in `.planning/research/` (ARCHITECTURE.md, FEATURES.md, PITFALLS.md, STACK.md, SUMMARY.md)
- Codebase analysis docs live in `.planning/codebase/`

**Configuration:**
- `.planning/config.json` holds GSD workflow configuration (mode, depth, parallelization, model profile)
- `pyproject.toml` is the single source of truth for Python project metadata and dependencies
- `.python-version` pins the Python version (`3.13`)
- `uv.lock` is committed to version control for reproducible dependency resolution

**Dev Logs:**
- Template at `00-dev-log/00-template.md` with date heading and progress checklist
- Daily logs named by date: `00-dev-log/YYYY-MM-DD.md`
- Foam VS Code extension templates in `.foam/templates/` for note creation

**Image Assets:**
- Screenshots organized by date: `00-supporting-files/images/YYYY-MM-DD/`
- README images in `00-supporting-files/images/README/`
- Timestamp-based filenames: `YYYYMMDDHHmmss.png`

## Dependency Management

**Package Manager:** uv

**Adding dependencies:**
```bash
uv add <package-name>        # Add a runtime dependency
uv add --dev <package-name>  # Add a dev dependency
uv sync                      # Install all dependencies from lockfile
```

**Key principle:** Each worktree gets its own `.venv`. Run `uv sync` after creating a new worktree to initialize the virtual environment.

**Current dependencies (from `pyproject.toml`):**
- `ipykernel>=6.30.1` — Jupyter kernel support
- `marimo>=0.18.4` — Reactive notebook/app framework
- `ollama>=0.5.3` — Local LLM client
- `openai>=1.101.0` — OpenAI API client (also used for LM Studio compatibility)

---

*Convention analysis: 2026-02-13*
