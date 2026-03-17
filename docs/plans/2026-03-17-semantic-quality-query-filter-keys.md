# Semantic Quality And Query Filter Keys Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Change crawler mappings so `quality` and `query_filter` keys use semantic names while `slot` and `type` keep `label_value` keys.

**Architecture:** Update the mappings generator to emit semantic keys for qualities and query filters, regenerate the data layer, and migrate task examples/tests/documentation to the new mixed-key scheme. Keep runner/fetcher/export flow unchanged.

**Tech Stack:** Python 3, unittest, JSON config files

---

### Task 1: Add failing generator tests for semantic quality and query filter keys

**Files:**
- Modify: `crawler/tests/test_mappings_generator.py`
- Modify: `crawler/tests/test_mappings.py`
- Modify: `crawler/tests/test_url_builder.py`

**Step 1: Write the failing tests**
- Assert generated `QUALITIES` keys are `uncommon`, `rare`, `epic`.
- Assert generated `QUERY_FILTERS` keys are semantic names like `available_to_players`.
- Assert query filter order uses semantic names.
- Assert validation/url builder accept tasks using semantic quality and query filter keys.

**Step 2: Run focused tests to verify they fail**
Run: `cd crawler && python3 -m unittest tests.test_mappings_generator tests.test_mappings tests.test_url_builder`
Expected: FAIL because current generated keys still use `label_value` for both layers.

### Task 2: Implement semantic key generation and regenerate data consumers

**Files:**
- Modify: `crawler/core/mappings_generator.py`
- Modify: `crawler/core/mappings_data.py`
- Modify: `crawler/tasks/wowhead_items.example.json`
- Modify: `crawler/tasks/wowhead_items.json`
- Modify: `crawler/README.md`
- Modify: tests that embed task fixtures

**Step 1: Write minimal implementation**
- Make quality keys use normalized label only.
- Make query filter keys use normalized label only.
- Keep slot/type keys unchanged.
- Rebuild `QUERY_FILTER_ORDER` against semantic query filter keys.
- Update task fixtures, example files, and docs to the new scheme.

**Step 2: Run focused tests to verify they pass**
Run: `cd crawler && python3 -m unittest tests.test_mappings_generator tests.test_mappings tests.test_url_builder`
Expected: PASS.

### Task 3: Run regression tests

**Files:**
- Verify only

**Step 1: Run crawler regression suite**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS.

### Task 4: Commit

**Step 1: Commit after verification**
```bash
git add crawler/core/mappings_generator.py crawler/core/mappings_data.py crawler/tasks/wowhead_items.example.json crawler/tasks/wowhead_items.json crawler/README.md crawler/tests/test_mappings_generator.py crawler/tests/test_mappings.py crawler/tests/test_url_builder.py crawler/tests/test_runner.py crawler/tests/test_fetcher.py docs/plans/2026-03-17-semantic-quality-query-filter-keys.md
git commit -m "refactor: use semantic quality and filter keys"
```
