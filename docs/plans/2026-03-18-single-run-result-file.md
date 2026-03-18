# Single Run Result File Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Store all fetched task results for a run in one JSON file instead of one file per task.

**Architecture:** Introduce a shared run-level results file (`items.by-task.json`) and route `fetcher`, `aggregator`, and `run_report` through it. Maintain task-level result grouping keyed by `task_id` so existing status semantics and empty-result reporting remain intact.

**Tech Stack:** Python 3, `unittest`, JSON file IO

---

### Task 1: Define new run result file behavior in tests

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Modify: `crawler/tests/test_run_report.py`
- Possibly modify: `crawler/tests/test_aggregator.py`

**Step 1: Write failing fetcher test for single-file output**
- Replace or extend an existing successful fetch test.
- Assert `fetch_manifest_results()` writes `items.by-task.json`.
- Assert the fetched task result lives under its `task_id` key.
- Assert no `<task_id>.json` file is created.

**Step 2: Write failing report test for single-file input**
- Build a manifest plus `items.by-task.json`.
- Assert `run_report` still identifies empty fetched tasks.

**Step 3: Write failing aggregator test for single-file input**
- Build a manifest plus `items.by-task.json` with duplicate item IDs across tasks.
- Assert `build_unique_items()` still produces a unique list.

**Step 4: Run focused tests and verify failure**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_writes_items_by_task_file`
- `cd crawler && python3 -m unittest tests.test_run_report.RunReportTest.test_write_run_report_reads_items_by_task_file`
- `cd crawler && python3 -m unittest tests.test_aggregator.AggregatorTest.test_build_unique_items_reads_items_by_task_file`
Expected: FAIL because code still expects one file per task.

### Task 2: Implement shared result file support

**Files:**
- Modify: `crawler/core/fetcher.py`
- Modify: `crawler/core/aggregator.py`
- Modify: `crawler/core/run_report.py`
- Possibly modify: `crawler/scripts/aggregate_run.py`
- Test: `crawler/tests/test_fetcher.py`
- Test: `crawler/tests/test_run_report.py`
- Test: `crawler/tests/test_aggregator.py`

**Step 1: Add shared result file helpers**
- Define a single file name constant for `items.by-task.json`.
- Add read/write helpers around that file.

**Step 2: Update fetcher writes**
- On success, write the task result into `items.by-task.json` under its `task_id`.
- Do not create `<task_id>.json` anymore.

**Step 3: Update report reads**
- Load `items.by-task.json` once.
- Use it to determine which fetched tasks have zero items.

**Step 4: Update aggregator reads**
- Load `items.by-task.json` once.
- Aggregate unique items from fetched tasks only.

**Step 5: Run focused tests and verify green**
Run the same focused tests from Task 1.
Expected: PASS

### Task 3: Verify no regression

**Files:**
- Modify if needed: `crawler/core/fetcher.py`
- Modify if needed: `crawler/core/aggregator.py`
- Modify if needed: `crawler/core/run_report.py`

**Step 1: Run focused modules**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher tests.test_run_report tests.test_aggregator`
Expected: PASS

**Step 2: Run full crawler suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS

### Task 4: Commit

**Step 1: Create commit**
```bash
git add crawler/core/fetcher.py crawler/core/aggregator.py crawler/core/run_report.py crawler/tests/test_fetcher.py crawler/tests/test_run_report.py crawler/tests/test_aggregator.py docs/plans/2026-03-18-single-run-result-file-design.md docs/plans/2026-03-18-single-run-result-file.md
git commit -m "refactor: store run results in a single file"
```
