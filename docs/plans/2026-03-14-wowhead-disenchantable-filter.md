# Wowhead Disenchantable Filter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a semantic `disenchantable` query filter so task configs can generate Wowhead `filter id 8` with `yes / no / any` values.

**Architecture:** Extend the existing `QUERY_FILTERS` map in `mappings.py` with a new `disenchantable` entry and add it into the stable `QUERY_FILTER_ORDER`. The URL builder will pick it up automatically and serialize it into `?filter=` output using the same code path as the existing filters.

**Tech Stack:** Python 3, `unittest`

---

### Task 1: Lock the new query filter with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`

**Step 1: Write the failing test**

Add tests that assert:

- `QUERY_FILTERS["disenchantable"]["wowhead"] == {"id": 8}`
- `validate_task()` accepts `{"disenchantable": "no"}`
- URL builder generates `filter=8;2;0` for a task with only `disenchantable: "no"`
- stable ordering still works when `disenchantable` is combined with existing filters

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings tests.test_url_builder`

Expected: FAIL because the new query filter is not defined yet.

**Step 3: Write minimal implementation**

Add `disenchantable` into `QUERY_FILTERS` and `QUERY_FILTER_ORDER`.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings tests.test_url_builder`

Expected: PASS

### Task 2: Update docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-query-filters.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Document the new filter**

Document that:

- `disenchantable` maps to Wowhead filter id `8`
- it supports `yes / no / any`

**Step 2: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

### Task 3: Commit

**Files:**
- Verify all touched code, tests, and docs

**Step 1: Commit**

```bash
git add crawler/core/mappings.py crawler/tests/test_mappings.py crawler/tests/test_url_builder.py docs/plans/2026-03-14-wowhead-query-filters.md docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-disenchantable-filter.md
git commit -m "feat: add wowhead disenchantable filter"
```
