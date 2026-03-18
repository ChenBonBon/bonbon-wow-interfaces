# Fetch Progress Logging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add timestamped fetch progress logs so long-running Wowhead crawls visibly report task start, completion, failure, and periodic progress.

**Architecture:** Keep logging inside `crawler/core/fetcher.py` so every existing entrypoint (`run_all`, `fetch_run`, `retry_failed_run`) inherits the behavior automatically. Use injectable logger and timestamp helpers so tests can verify exact output without relying on real stdout or wall-clock time.

**Tech Stack:** Python 3, `unittest`, `ThreadPoolExecutor`

---

### Task 1: Define observable logging behavior in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write failing tests for start/done/progress logging**
- Add a test that runs `fetch_manifest_results()` with 10 planned tasks.
- Inject a fake logger and fixed timestamp function.
- Assert that logs contain:
  - `START <task_id>` for processed tasks
  - `DONE <task_id> item_count=<n>` when a task succeeds
  - `PROGRESS done=10/10 fetched=10 failed=0` after the tenth completion

**Step 2: Run focused tests to verify failure**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_logs_start_done_and_progress`
Expected: FAIL because fetcher does not yet accept logging hooks or emit progress lines.

### Task 2: Define failure logging behavior in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write failing test for failure logging**
- Add a test that runs `fetch_manifest_results()` with one planned task and a failing `fetch_url`.
- Inject fake logger and fixed timestamp function.
- Assert logs contain:
  - `START <task_id>`
  - `FAIL <task_id>`

**Step 2: Run focused tests to verify failure**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_logs_failures`
Expected: FAIL because fetcher does not yet emit failure logs.

### Task 3: Implement minimal logging hooks in fetcher

**Files:**
- Modify: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Add injectable logging helpers**
- Add optional `logger` and `timestamp_fn` parameters to:
  - `fetch_manifest_results()`
  - `retry_failed_manifest_results()`
  - internal manifest processing helpers as needed
- Default logger to `print`
- Default timestamp function to a formatted current time helper

**Step 2: Emit task lifecycle logs**
- Log `START <task_id>` before each task fetch begins.
- Log `DONE <task_id> item_count=<n>` when a task succeeds.
- Log `FAIL <task_id>` when a task raises.
- Prefix every line with `[YYYY-MM-DD HH:MM:SS] `.

**Step 3: Emit periodic progress logs**
- Track completed, fetched, and failed counts in the manifest processing loop.
- After every 10 completed tasks, log:
  - `PROGRESS done=<done>/<total> fetched=<fetched> failed=<failed>`

**Step 4: Run focused tests to verify green**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_logs_start_done_and_progress`
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_logs_failures`
Expected: PASS

### Task 4: Verify no regression in fetcher behavior

**Files:**
- Modify if needed: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Run fetcher test module**
Run: `cd crawler && python3 -m unittest tests.test_fetcher`
Expected: PASS

**Step 2: Run full crawler test suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS

### Task 5: Commit

**Files:**
- Commit modified fetcher/tests/plan files

**Step 1: Create commit**
```bash
git add crawler/core/fetcher.py crawler/tests/test_fetcher.py docs/plans/2026-03-18-fetch-progress-logging.md
git commit -m "feat: add fetch progress logging"
```
