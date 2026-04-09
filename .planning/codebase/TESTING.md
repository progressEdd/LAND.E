# Testing Patterns

**Analysis Date:** 2026-02-13

## Test Framework

**Runner:**
- No test framework is installed or configured
- No `pytest`, `unittest`, `vitest`, or any test runner in `pyproject.toml` dependencies
- No test configuration files exist (`pytest.ini`, `pyproject.toml [tool.pytest]`, `conftest.py`, etc.)
- `.gitignore` includes `.pytest_cache/`, `.hypothesis/`, `htmlcov/`, `coverage.xml` — suggesting pytest is the intended future framework

**Assertion Library:**
- None configured
- Research code examples use bare Python `assert` statements for validation

**Run Commands:**
```bash
# No test commands are currently configured
# When pytest is added:
uv add --dev pytest           # Install
uv run pytest                 # Run all tests
uv run pytest --tb=short      # Run with short tracebacks
uv run pytest -x              # Stop on first failure
uv run pytest --cov           # Run with coverage (requires pytest-cov)
```

## Current Testing Approach

This repository uses **manual verification and UAT (User Acceptance Testing)** instead of automated tests. Testing is document-driven:

### UAT Pattern

**Location:** `.planning/phases/{phase-name}/{phase}-UAT.md`

**Structure (from `01-UAT.md`):**
```markdown
---
status: complete
phase: 01-template-preparation
source: 01-01-SUMMARY.md
started: 2026-02-14T00:05:00Z
updated: 2026-02-14T00:08:00Z
---

## Current Test

[testing complete]

## Tests

### 1. README template exists on 00-experiments
expected: Running `cat 02-worktrees/00-experiments/README.md` shows a non-empty file...
result: pass

### 2. Sentinel comment on first line
expected: The very first line of `02-worktrees/00-experiments/README.md` is exactly...
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0

## Gaps

[none yet]
```

**Patterns:**
- Each test has a numbered heading, an `expected:` description, and a `result:` field (`pass`/`fail`)
- Summary section tracks totals at the end
- Gaps section documents missing test coverage
- YAML frontmatter tracks status, phase, source summary, and timestamps

### Plan-Level Verification

**Location:** Within plan files (e.g., `01-01-PLAN.md`)

**Structure:**
```markdown
<verify>
1. File exists and is non-empty: `test -s 02-worktrees/00-experiments/README.md && echo "OK"`
2. Sentinel present: `grep -c 'TEMPLATE: REPLACE ME' 02-worktrees/00-experiments/README.md`
3. All placeholders present: `grep -c '\$project_name\|\$description\|\$branch_name\|\$created_date'...`
4. Committed: `git -C 02-worktrees/00-experiments log -1 --oneline`
5. No `${...}` syntax used: `grep -c '\${' 02-worktrees/00-experiments/README.md`
</verify>
```

**Patterns:**
- Verification steps use shell one-liners that can be copy-pasted and run
- Each step checks one specific condition with a clear pass/fail outcome
- Verification is embedded in the plan, not in a separate test file

### Python One-Liner Validation

**Pattern (from plan files):**
```python
python3 -c "
from string import Template
content = open('02-worktrees/00-experiments/README.md').read()
t = Template(content)
result = t.safe_substitute(
    project_name='Test Project',
    description='A test',
    branch_name='test-branch',
    created_date='2026-01-01'
)
assert '\$project_name' not in result, 'project_name not substituted'
assert '\$description' not in result, 'description not substituted'
print('All placeholders substitute correctly')
"
```

**Usage:**
- Inline Python scripts run via `python3 -c "..."` for quick validation
- Uses bare `assert` statements with descriptive failure messages
- Tests real file contents, not mocked data
- Validates cross-file consistency (e.g., pyproject.toml `readme` field resolves to an actual file)

## Test File Organization

**Location:**
- No dedicated test directory exists (`tests/`, `test/`, etc.)
- UAT documents live alongside plan documents in `.planning/phases/{phase}/`
- Verification logic is embedded in plan files, not extracted into test modules

**Naming:**
- UAT files: `{phase-number}-UAT.md`
- No `test_*.py`, `*_test.py`, or `*.spec.*` files exist anywhere in the repository

## Mocking

**Framework:** None

**Current approach:**
- All verification runs against real files in real git worktrees
- No mocking, stubbing, or test doubles are used
- Tests validate actual git state (`git log`, `git status`) and file contents

## Fixtures and Factories

**Test Data:**
- No fixtures directory or factory pattern exists
- `00-supporting-files/data/sample.env.file` serves as a reference environment file (not a test fixture)
- Plan verification uses hardcoded test values inline:
  ```python
  t.safe_substitute(
      project_name='Test Project',
      description='A test',
      branch_name='test-branch',
      created_date='2026-01-01'
  )
  ```

## Coverage

**Requirements:** None enforced

**Current state:**
- No coverage tool is configured
- No coverage thresholds or requirements exist
- `.gitignore` includes coverage-related entries (`htmlcov/`, `.coverage`, `coverage.xml`) for when coverage is eventually added

## Test Types

**Unit Tests:**
- None exist. No Python source files on the master branch to unit test.
- Experiment branches may contain their own tests, but each branch is independent.

**Integration Tests:**
- None exist as automated tests.
- UAT documents serve as manual integration test scripts — they verify end-to-end outcomes (file created + content correct + git state clean).

**E2E Tests:**
- Not applicable for a template/workflow repository.
- The UAT process is effectively E2E: it validates the full workflow outcome from plan execution through file creation to git commit.

**Validation Scripts:**
- Python one-liners embedded in plan files serve as lightweight smoke tests
- Shell commands (`test -s`, `grep -c`, `git status --porcelain`) validate postconditions

## Recommended Testing Setup (When Adding Tests)

When Python source files are introduced on experiment branches, use this setup:

**Install:**
```bash
uv add --dev pytest pytest-cov
```

**Configure in `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
show_missing = true
fail_under = 80
```

**Directory structure:**
```
project-root/
├── src/           # Source code (if using src layout)
│   └── ...
├── tests/         # Test files
│   ├── conftest.py
│   ├── test_*.py
│   └── ...
├── pyproject.toml
└── ...
```

**Test pattern:**
```python
# tests/test_example.py
import pytest

def test_something():
    """Describe what this test validates."""
    result = function_under_test()
    assert result == expected_value

class TestGroupName:
    """Group related tests."""

    def test_case_one(self):
        assert True

    def test_edge_case(self):
        with pytest.raises(ValueError, match="expected message"):
            function_that_raises()
```

**Async testing (for LLM client code):**
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result is not None
```

## Common Verification Patterns

**File existence and content:**
```bash
test -s path/to/file && echo "OK"              # File exists and is non-empty
grep -c 'expected pattern' path/to/file         # Pattern appears N times
head -1 path/to/file                            # Check first line content
```

**Git state validation:**
```bash
git -C <worktree> status --porcelain            # Should be empty (clean)
git -C <worktree> log -1 --oneline              # Verify last commit
git worktree list --porcelain                   # Verify worktree state
```

**Python validation:**
```bash
python3 -c "
import tomllib
with open('path/to/pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
assert data['project']['name'] == 'expected-name'
print('OK')
"
```

---

*Testing analysis: 2026-02-13*
