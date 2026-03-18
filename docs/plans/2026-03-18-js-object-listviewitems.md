# JS Object `listviewitems` Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make fetch parsing succeed when Wowhead returns `listviewitems` as JavaScript object literals instead of strict JSON.

**Architecture:** Add a narrow payload-normalization helper in `crawler/core/fetcher.py` that converts observed bare object keys into JSON-compatible quoted keys before `json.loads()`. Verify behavior with parser-level tests and a manifest fetch-flow test using a realistic Wowhead sample.

**Tech Stack:** Python 3, `unittest`, regex-based normalization

---

### Task 1: Define parser behavior for JS object payloads

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing parser test**
- Add a sample HTML fixture whose `listviewitems` contains bare keys such as:
  - `firstseenpatch: 0`
  - `popularity:30`
- Assert `parse_items_from_html()` returns the minimal item list with `itemId` and `name`.

**Step 2: Run focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_parse_items_from_html_parses_js_object_literal_payload`
Expected: FAIL with a JSON decoding error.

### Task 2: Define fetch-flow behavior for JS object payloads

**Files:**
- Modify: `crawler/tests/test_fetcher.py`
- Reference: `crawler/core/fetcher.py`

**Step 1: Write a failing fetch test**
- Add a manifest with one planned task.
- Feed the JS object literal HTML through `fetch_manifest_results()`.
- Assert:
  - task status becomes `fetched`
  - result file exists
  - result file contains the minimal parsed items
  - task does not have `error_message`

**Step 2: Run focused test and verify it fails**
Run: `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_parses_js_object_literal_payload_as_success`
Expected: FAIL because `json.loads()` still rejects the payload.

### Task 3: Implement minimal payload normalization

**Files:**
- Modify: `crawler/core/fetcher.py`
- Test: `crawler/tests/test_fetcher.py`

**Step 1: Add a normalization helper**
- Normalize extracted `listviewitems` text before `json.loads()`.
- Quote observed bare keys without touching already quoted keys.

**Step 2: Use normalized payload in parser**
- Route `parse_items_from_html()` through the normalizer before `json.loads()`.

**Step 3: Run focused tests and verify green**
Run:
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_parse_items_from_html_parses_js_object_literal_payload`
- `cd crawler && python3 -m unittest tests.test_fetcher.FetcherTest.test_fetch_manifest_results_parses_js_object_literal_payload_as_success`
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
git add crawler/core/fetcher.py crawler/tests/test_fetcher.py docs/plans/2026-03-18-js-object-listviewitems-design.md docs/plans/2026-03-18-js-object-listviewitems.md
git commit -m "fix: parse js-style listviewitems payloads"
```
