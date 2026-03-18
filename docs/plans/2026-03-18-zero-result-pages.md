# Zero Result Pages Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make zero-result Wowhead pages succeed with `items=[]` instead of being counted as fetch failures.

**Architecture:** Add an explicit empty-state detector in `crawler/core/fetcher.py` and route `parse_items_from_html()` through it when `listviewitems` is absent. Verify this behavior directly at the parser level and through the manifest fetch flow so failed task counts and empty result files reflect the new semantics.

**Tech Stack:** Python 3, `unittest`

---

### Task 1: Define parser behavior for zero-result pages

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing parser test**
- Add a sample HTML fixture representing a Wowhead page with zero results and no `listviewitems`, but containing the empty-state text.
- Assert `parse_items_from_html()` returns `[]`.

**Step 2: Run focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_parse_items_from_html_returns_empty_list_for_zero_result_page`
Expected: FAIL because parser still raises `未找到 listviewitems 数据`.

### Task 2: Define fetch-flow behavior for zero-result pages

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing fetch test**
- Add a manifest with one planned task.
- Feed the zero-result HTML through `fetch_manifest_results()`.
- Assert:
  - task status becomes `fetched`
  - result file exists
  - result file `items` is `[]`
  - task does not have `error_message`

**Step 2: Run focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_treats_zero_result_page_as_success`
Expected: FAIL because fetcher still treats the page as an error.

### Task 3: Implement empty-state detection

**Files:**
- Modify: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Add minimal empty-page detection**
- Add a helper that detects Wowhead's zero-result marker text in the HTML.
- In `parse_items_from_html()`, if `listviewitems` is missing but the empty-state marker exists, return `[]`.

**Step 2: Run focused tests and verify green**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_parse_items_from_html_returns_empty_list_for_zero_result_page`
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_treats_zero_result_page_as_success`
Expected: PASS

### Task 4: Verify no regression

**Files:**
- Modify if needed: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Run fetcher module tests**
Run: `cd crawler && python3 -m unittest tests.test_fetcher`
Expected: PASS

**Step 2: Run full crawler suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS

### Task 5: Commit

**Step 1: Create commit**
```bash
git add crawler/core/fetcher.py crawler/tests/test_fetcher.py docs/plans/2026-03-18-zero-result-pages-design.md docs/plans/2026-03-18-zero-result-pages.md
git commit -m "fix: treat zero-result pages as successful fetches"
```
