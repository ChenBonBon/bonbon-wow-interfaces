# Wowhead Fetcher Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a fetcher that reads a planned run manifest, fetches Wowhead item pages, extracts `itemId` and `name`, writes per-task JSON files, and updates task status in the manifest.

**Architecture:** Keep fetching downstream from runner output. The fetcher consumes `manifest.json`, extracts `listviewitems` from each task page, converts the embedded data to a minimal item list, writes one result file per task, and persists status updates back to the manifest.

**Tech Stack:** Python 3, unittest, JSON, urllib

---

### Task 1: Define parser behavior with failing tests

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_fetcher.py`

**Step 1: Write the failing test**

Write tests that assert:

- `extract_listviewitems_json()` extracts the array text from sample HTML
- `parse_items_from_html()` returns a list of `{itemId, name}`
- parser ignores all other item fields

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.fetcher` does not exist yet.

**Step 3: Write minimal implementation**

Add the smallest possible parser helpers for tests to import.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to specific parsing behavior.

### Task 2: Implement manifest-driven fetching

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/fetcher.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_fetcher.py`

**Step 1: Write the failing test**

Extend tests so they assert:

- `fetch_manifest_results()` only processes `planned` tasks
- successful fetch writes `<task_id>.json`
- successful fetch updates task status to `fetched`
- failed fetch updates task status to `failed`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because fetching and manifest persistence do not exist yet.

**Step 3: Write minimal implementation**

Implement:

- HTML fetch helper using `urllib.request`
- manifest load/write helpers
- `fetch_manifest_results(manifest_path, fetch_url=None)`

Allow injecting a fake `fetch_url` function in tests.

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Update docs and outputs contract

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Update docs**

Document:

- `core/fetcher.py`
- per-task JSON result files
- manifest status values `planned/fetched/failed`

**Step 2: Review for consistency**

Ensure docs, tests, and output examples all use `itemId` and `name`.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/fetcher.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_fetcher.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-fetcher-design.md`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-fetcher.md`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/fetcher.py crawler/tests/test_fetcher.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-fetcher-design.md docs/plans/2026-03-14-wowhead-fetcher.md
git commit -m "feat: add wowhead manifest fetcher"
```
