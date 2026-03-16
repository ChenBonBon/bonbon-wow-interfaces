# Fetch Concurrency 3 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make crawler fetch execution use a fixed concurrency of 3 for planned and failed task retries.

**Architecture:** Keep concurrency inside `crawler/core/fetcher.py` so `fetch_run`, `retry_failed_run`, and `run_all` inherit the same behavior automatically. Preserve manifest/result file format and only parallelize the fetch stage.

**Tech Stack:** Python 3, unittest, concurrent.futures

---

### Task 1: Add a failing fetcher test for fixed concurrency

**Files:**
- Modify: `crawler/tests/test_fetcher.py`

**Step 1: Write the failing test**
- Add a test that creates more than 3 planned tasks.
- Use a thread-safe probe fetcher that records the peak number of concurrent calls.
- Assert the peak concurrency is exactly `3`.

**Step 2: Run the focused test to verify it fails**
Run: `cd crawler && python3 -m unittest crawler.tests.test_fetcher.FetcherTest.test_fetch_manifest_results_uses_fixed_concurrency_of_three`
Expected: FAIL because fetcher is currently sequential.

### Task 2: Implement fixed concurrency in fetcher

**Files:**
- Modify: `crawler/core/fetcher.py`

**Step 1: Add minimal implementation**
- Introduce a single fetch concurrency constant set to `3`.
- Process eligible manifest tasks through a thread pool.
- Keep per-task success/failure handling unchanged.
- Keep manifest output format unchanged.

**Step 2: Run the focused test to verify it passes**
Run: `cd crawler && python3 -m unittest crawler.tests.test_fetcher.FetcherTest.test_fetch_manifest_results_uses_fixed_concurrency_of_three`
Expected: PASS.

### Task 3: Run regression tests

**Files:**
- Verify only

**Step 1: Run fetcher tests**
Run: `cd crawler && python3 -m unittest crawler.tests.test_fetcher`
Expected: PASS.

**Step 2: Run the full crawler test suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS.

### Task 4: Commit

**Files:**
- Commit only after verification succeeds.

**Step 1: Commit**
```bash
git add crawler/core/fetcher.py crawler/tests/test_fetcher.py docs/plans/2026-03-16-fetch-concurrency-3.md
git commit -m "feat: fetch crawler tasks with concurrency 3"
```
