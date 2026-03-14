# Wowhead Aggregator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a minimal aggregator that deduplicates fetched items by `itemId` and writes `items.unique.json` for a run.

**Architecture:** Keep aggregation downstream from fetching. The aggregator reads `manifest.json`, loads only `fetched` task result files, flattens their `items`, deduplicates by `itemId`, and writes a single unique item list. A thin script adapter calls the aggregator for manual and scheduled use.

**Tech Stack:** Python 3, unittest, JSON

---

### Task 1: Define aggregation behavior with failing tests

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_aggregator.py`

**Step 1: Write the failing test**

Write tests that assert:

- `build_unique_items()` only includes `fetched` tasks
- duplicate `itemId` values are collapsed to one record
- `write_unique_items()` writes `items.unique.json`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.aggregator` does not exist yet.

**Step 3: Write minimal implementation**

Add the smallest possible functions for tests to import.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to missing aggregation behavior.

### Task 2: Add script adapter for aggregation

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/aggregate_run.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/aggregator.py`

**Step 1: Write the failing test**

Extend script tests so they assert:

- `scripts.aggregate_run.run()` writes `items.unique.json`
- returned path matches the generated output file

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because the script adapter does not exist yet.

**Step 3: Write minimal implementation**

Implement:

- `build_unique_items(manifest_path)`
- `write_unique_items(manifest_path)`
- `scripts.aggregate_run.run(argv=None)`

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Update design docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Update docs**

Document:

- `core/aggregator.py`
- `scripts/aggregate_run.py`
- `outputs/<run_id>/items.unique.json`

**Step 2: Review for consistency**

Ensure docs and tests both describe the same minimal output structure.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/aggregator.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/aggregate_run.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_aggregator.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/aggregator.py crawler/scripts/aggregate_run.py crawler/tests/test_aggregator.py crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-aggregator-design.md docs/plans/2026-03-14-wowhead-aggregator.md
git commit -m "feat: add wowhead item aggregator"
```
