# Wowhead Scripts Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add thin Python script entrypoints for generating run manifests and fetching run results without moving business logic out of the `core` modules.

**Architecture:** Keep scripts as adapters only. `scripts.generate_run` forwards to `core.runner.write_run_manifest`, and `scripts.fetch_run` forwards to `core.fetcher.fetch_manifest_results`.

**Tech Stack:** Python 3, unittest

---

### Task 1: Define script entry behavior with failing tests

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Write tests that assert:

- `scripts.generate_run.run()` creates a manifest file
- `scripts.fetch_run.run()` consumes a manifest and writes a task result file

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because the `scripts` package does not exist yet.

**Step 3: Write minimal implementation**

Create the package and the smallest callable `run()` functions needed by tests.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to specific missing script behavior.

### Task 2: Implement thin script adapters

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/__init__.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/generate_run.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/fetch_run.py`

**Step 1: Write the failing test**

Extend tests if needed so they also cover:

- optional output directory support for `generate_run`
- returned path values from both script adapters

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL on missing forwarding logic.

**Step 3: Write minimal implementation**

Implement thin `run(argv=None, ...)` adapters and `main()` functions.

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Update design docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Update docs**

Document:

- `crawler/scripts/`
- `python3 -m scripts.generate_run`
- `python3 -m scripts.fetch_run`

**Step 2: Review for consistency**

Ensure docs use scripts as the recommended execution path.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/generate_run.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/fetch_run.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/scripts/__init__.py crawler/scripts/generate_run.py crawler/scripts/fetch_run.py crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-scripts-design.md docs/plans/2026-03-14-wowhead-scripts.md
git commit -m "feat: add wowhead script entrypoints"
```
