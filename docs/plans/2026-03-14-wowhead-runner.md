# Wowhead Runner Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a preflight runner that reads semantic task configs, generates planned Wowhead URLs, and writes a per-run `manifest.json`.

**Architecture:** Keep planning separate from fetching. The runner reads tasks, normalizes and validates them through existing mapping helpers, builds URL parts via `url_builder.py`, and writes a structured manifest to a run-specific output directory.

**Tech Stack:** Python 3, unittest, JSON

---

### Task 1: Define runner behavior with failing tests

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_runner.py`

**Step 1: Write the failing test**

Write tests that assert:

- `build_run_manifest()` only includes `enabled: true` tasks
- the manifest contains `run_id`, `generated_at`, `task_count`, and `tasks`
- each planned task includes `status`, `filter_path`, `path`, `query_string`, and `url`
- `write_run_manifest()` creates `<outputs>/<run_id>/manifest.json`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.runner` does not exist yet.

**Step 3: Write minimal implementation**

Create the smallest interface needed for tests to import and call runner helpers.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to specific missing behavior.

### Task 2: Implement runner helpers and CLI

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/runner.py`

**Step 1: Write the failing test**

Extend tests if needed so they also cover:

- stable `run_id` formatting from an injected timestamp
- `task_file` is stored in the manifest
- output JSON matches the returned manifest

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL on missing manifest fields or file output behavior.

**Step 3: Write minimal implementation**

Implement:

- `load_tasks(task_file_path)`
- `build_run_manifest(task_file_path, generated_at=None)`
- `write_run_manifest(task_file_path, outputs_dir=None, generated_at=None)`
- CLI entry with `--task-file`

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Update design docs and example output contract

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/outputs/.gitkeep`

**Step 1: Update docs**

Document:

- `core/runner.py`
- `outputs/<run_id>/manifest.json`
- `status: planned`

**Step 2: Add outputs directory placeholder**

Create `.gitkeep` so the outputs directory exists in the project shape.

**Step 3: Review for consistency**

Ensure docs and tests describe the same manifest structure.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/runner.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_runner.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/outputs/.gitkeep`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/runner.py crawler/tests/test_runner.py crawler/outputs/.gitkeep docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-runner-design.md docs/plans/2026-03-14-wowhead-runner.md
git commit -m "feat: add wowhead task runner"
```
