# Wowhead Failed Retry Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a dedicated retry path that reruns only `failed` fetch tasks from an existing manifest, then recomputes aggregate output and retries Lua export for the whole run.

**Architecture:** Reuse the existing fetcher flow by extracting a shared internal task-processing helper keyed by allowed statuses. Keep `fetch_manifest_results()` focused on `planned` tasks and add `retry_failed_manifest_results()`. The script adapter will then call `aggregate_run` and `export_lua`, with export acting as the completeness gate for the entire manifest.

**Tech Stack:** Python 3, unittest

---

### Task 1: Define failed-retry behavior with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_fetcher.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add tests that assert:

- `retry_failed_manifest_results()` only processes `failed` tasks
- successful retry changes `failed` to `fetched`
- retry does not touch `planned` or `fetched`
- `scripts.retry_failed_run.run()` calls retry, aggregate, and export in order
- retry with remaining `planned` tasks raises during export

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because the retry function and script do not exist yet.

**Step 3: Write minimal implementation**

Add test-driven placeholders for the new retry function and script adapter.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to missing retry behavior.

### Task 2: Implement shared fetch execution and retry script

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/fetcher.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/retry_failed_run.py`

**Step 1: Write the failing test**

Extend tests if needed so they also cover:

- failed retry writes or rewrites `<task_id>.json`
- failed retry leaves unsuccessful tasks as `failed`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL on missing shared status-gated execution.

**Step 3: Write minimal implementation**

Implement:

- shared internal helper for processing selected task statuses
- `retry_failed_manifest_results(manifest_path, fetch_url=None)`
- `scripts.retry_failed_run.run(argv=None, fetch_url=None, export_output_path=None)`

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Update docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Update docs**

Document:

- `scripts.retry_failed_run`
- dedicated retry flow for `failed` tasks

**Step 2: Review for consistency**

Ensure docs still describe `fetch_run` as planned-only.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/fetcher.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/retry_failed_run.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_fetcher.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/fetcher.py crawler/scripts/retry_failed_run.py crawler/tests/test_fetcher.py crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-retry-failed-design.md docs/plans/2026-03-14-wowhead-retry-failed.md
git commit -m "feat: add failed task retry script"
```
