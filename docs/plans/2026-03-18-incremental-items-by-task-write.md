# Incremental `items.by-task.json` Write Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Persist `items.by-task.json` incrementally during fetch execution so partial results are visible before the full run completes.

**Architecture:** Reuse the existing run-scoped result map in `crawler/core/fetcher.py`, but move file writes from the end of the fetch pass into the task-completion loop. Verify the behavior with a background-thread fetch test that keeps one task blocked so the result file can be observed while the overall fetch is still running.

**Tech Stack:** Python 3, `unittest`, threading

---

### Task 1: Define incremental write behavior in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing incremental-write test**
- Create a manifest with two planned tasks.
- Patch fetch concurrency to `1`.
- Make the first fetch return immediately and the second fetch block on an event.
- Run `fetch_manifest_results()` in a background thread.
- Assert that while the second task is still blocked:
  - `items.by-task.json` already exists
  - it already contains the first task result
  - the fetch thread is still alive

**Step 2: Run the focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_updates_items_by_task_file_incrementally`
Expected: FAIL because `items.by-task.json` is currently written only after the fetch loop completes.

### Task 2: Implement incremental writes in fetcher

**Files:**
- Modify: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Move result-file writes into the completion loop**
- After each successful completion, write the updated `items.by-task.json` immediately.
- After each failed completion, remove stale task data and rewrite the file immediately.

**Step 2: Keep end-of-run cleanup behavior correct**
- Preserve the current behavior where the file is absent if there are no successful results.
- Avoid extra writes that would leave stale data behind.

**Step 3: Run the focused test and verify green**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_updates_items_by_task_file_incrementally`
Expected: PASS

### Task 3: Verify no regression

**Files:**
- Modify if needed: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Run fetcher tests**
Run: `cd crawler && python3 -m unittest tests.test_fetcher`
Expected: PASS

**Step 2: Run full crawler suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS

### Task 4: Commit

**Step 1: Create commit**
```bash
git add crawler/core/fetcher.py crawler/tests/test_fetcher.py docs/plans/2026-03-18-incremental-items-by-task-write-design.md docs/plans/2026-03-18-incremental-items-by-task-write.md
git commit -m "feat: update run result file incrementally"
```
