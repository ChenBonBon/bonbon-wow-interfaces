# Wowhead Run-All Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a single script entrypoint that orchestrates manifest generation, fetching, and unique-item aggregation.

**Architecture:** Keep orchestration outside the `core` modules. `scripts.run_all` simply forwards to `scripts.generate_run`, `scripts.fetch_run`, and `scripts.aggregate_run` in sequence, returning the generated manifest path.

**Tech Stack:** Python 3, unittest

---

### Task 1: Define orchestration behavior with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add a test that asserts `scripts.run_all.run()`:

- creates `manifest.json`
- writes at least one task result file
- writes `items.unique.json`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `scripts.run_all` does not exist yet.

**Step 3: Write minimal implementation**

Add the smallest script adapter needed to import and orchestrate the three steps.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to missing orchestration behavior.

### Task 2: Implement the thin run-all script

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/run_all.py`

**Step 1: Write the failing test**

Extend the script test if needed so it also asserts the returned value is the generated manifest path.

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL on missing orchestration forwarding.

**Step 3: Write minimal implementation**

Implement:

- `run(argv=None, fetch_url=None)`
- `main()`

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Update docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Update docs**

Document:

- `scripts.run_all`
- default flow `generate -> fetch -> aggregate`

**Step 2: Review for consistency**

Ensure docs still describe `retry_failed_run` as a separate manual tool.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/run_all.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/scripts/run_all.py crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-run-all-design.md docs/plans/2026-03-14-wowhead-run-all.md
git commit -m "feat: add wowhead run-all script"
```
