# Failure Error Reporting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Persist per-task `error_message` values in fetch manifests and include them in generated run reports.

**Architecture:** Extend `crawler/core/fetcher.py` so task status transitions manage an `error_message` field consistently, then update `crawler/core/run_report.py` to emit structured failed-task details from manifest state. Verify behavior with focused tests for direct fetch failures, retry cleanup, and report generation.

**Tech Stack:** Python 3, `unittest`

---

### Task 1: Define manifest error persistence in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing test for failed task error messages**
- Extend an existing failure-path test or add a new one.
- Assert that after `fetch_manifest_results()` fails a task, the updated manifest task contains:
  - `status: failed`
  - `error_message: <exception text>`

**Step 2: Write a failing test for retry cleanup**
- Start with a failed task that already has `error_message`.
- Retry it successfully.
- Assert the final task state is `fetched` and the stale `error_message` field is removed.

**Step 3: Run focused tests to verify failure**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_persists_error_message`
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_retry_failed_manifest_results_clears_stale_error_message_after_success`
Expected: FAIL because fetcher does not yet manage `error_message`.

### Task 2: Define run report failure detail in tests

**Files:**
- Modify: `crawler/tests/test_run_report.py`
- Reference: `crawler/core/run_report.py`

**Step 1: Write a failing report test**
- Build a manifest with a failed task carrying `error_message`.
- Assert `write_run_report()` produces:
  - `failed_task_ids`
  - `failed_tasks` with `task_id` and `error_message`

**Step 2: Run focused test to verify failure**
Run: `cd crawler && python3 -m unittest tests.test_run_report.RunReportTest.test_write_run_report_includes_failed_task_error_messages`
Expected: FAIL because report output does not yet include detailed failed task data.

### Task 3: Implement minimal error persistence and reporting

**Files:**
- Modify: `crawler/core/fetcher.py`
- Modify: `crawler/core/run_report.py`
- Test: `crawler/tests/test_fetcher.py`
- Test: `crawler/tests/test_run_report.py`

**Step 1: Persist failure messages in fetcher**
- On task failure, set `task["error_message"] = str(exception)`.
- On task success, remove `error_message` if present.

**Step 2: Emit detailed failed task data in reports**
- Extend run report building to produce `failed_tasks` alongside `failed_task_ids`.
- Each item should contain `task_id` and `error_message`.

**Step 3: Run focused tests to verify green**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_persists_error_message`
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_retry_failed_manifest_results_clears_stale_error_message_after_success`
- `cd crawler && python3 -m unittest tests.test_run_report.RunReportTest.test_write_run_report_includes_failed_task_error_messages`
Expected: PASS

### Task 4: Verify no regressions

**Files:**
- Modify if needed: `crawler/core/fetcher.py`
- Modify if needed: `crawler/core/run_report.py`

**Step 1: Run focused modules**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher tests.test_run_report`
Expected: PASS

**Step 2: Run full crawler suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS

### Task 5: Commit

**Step 1: Create commit**
```bash
git add crawler/core/fetcher.py crawler/core/run_report.py crawler/tests/test_fetcher.py crawler/tests/test_run_report.py docs/plans/2026-03-18-failure-error-reporting-design.md docs/plans/2026-03-18-failure-error-reporting.md
git commit -m "feat: persist fetch failure reasons"
```
