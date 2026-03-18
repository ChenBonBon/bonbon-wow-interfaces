# Consecutive Failure Cutoff Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Abort long-running crawls after 10 consecutive failed task completions and write a summary report before exiting.

**Architecture:** Refactor fetch scheduling in `crawler/core/fetcher.py` from eager submission of all eligible tasks to bounded submission up to the fixed concurrency of 3. This allows the fetch loop to stop feeding new work once the consecutive-failure threshold is reached, while preserving existing task status updates and per-task result files.

**Tech Stack:** Python 3, `unittest`, `ThreadPoolExecutor`

---

### Task 1: Define cutoff behavior in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`
- Reference: `crawler/core/run_report.py`

**Step 1: Write a failing abort test**
- Add a test with 12 planned tasks.
- Force fetches to fail.
- Patch fetch concurrency to `1` so completion order is deterministic.
- Assert that `fetch_manifest_results()` raises after the 10th consecutive failure.
- Assert the run directory now contains `run-report.json`.
- Assert the report contains:
  - `aborted_due_to_consecutive_failures: true`
  - `consecutive_failure_limit: 10`
  - `failed_count: 10`
  - `planned_count: 2`

**Step 2: Run the focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_aborts_after_ten_consecutive_failures`
Expected: FAIL because no abort limit exists yet.

### Task 2: Define streak reset behavior in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing reset test**
- Add a test whose completion sequence is 9 failures, 1 success, then 2 failures.
- Patch fetch concurrency to `1`.
- Assert the fetch run completes without raising.
- Assert the manifest ends with 11 failed tasks and 1 fetched task, proving success reset the streak.

**Step 2: Run the focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_resets_consecutive_failure_streak_after_success`
Expected: FAIL because no streak tracking exists yet.

### Task 3: Implement bounded scheduling and cutoff logic

**Files:**
- Modify: `crawler/core/fetcher.py`
- Modify: `crawler/core/run_report.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Add constants and abort metadata**
- Add a fixed limit constant for consecutive failures.
- Teach report writing to optionally include abort metadata.

**Step 2: Refactor fetch scheduling**
- Replace eager submission of all tasks with a bounded queue of at most `FETCH_CONCURRENCY` in-flight futures.
- Continue replenishing from remaining tasks only while not aborted.

**Step 3: Track and enforce streak state**
- Increment the consecutive failure counter on each failed completion.
- Reset it on each successful completion.
- When the counter hits 10:
  - log `ABORT ...`
  - stop scheduling new tasks
  - persist `manifest.json`
  - write `run-report.json`
  - raise an exception after in-flight tasks are resolved

**Step 4: Run focused tests and verify they pass**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_aborts_after_ten_consecutive_failures`
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_resets_consecutive_failure_streak_after_success`
Expected: PASS

### Task 4: Verify module and suite behavior

**Files:**
- Modify if needed: `crawler/core/fetcher.py`
- Modify if needed: `crawler/core/run_report.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Run fetcher tests**
Run: `cd crawler && python3 -m unittest tests.test_fetcher`
Expected: PASS

**Step 2: Run full crawler suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS

### Task 5: Commit

**Files:**
- Commit fetcher/report/tests/plan docs

**Step 1: Create commit**
```bash
git add crawler/core/fetcher.py crawler/core/run_report.py crawler/tests/test_fetcher.py docs/plans/2026-03-18-consecutive-failure-cutoff-design.md docs/plans/2026-03-18-consecutive-failure-cutoff.md
git commit -m "feat: abort fetches after repeated failures"
```
