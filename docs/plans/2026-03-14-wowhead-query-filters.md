# Wowhead Query Filters Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the crawler task model and URL builder so semantic query filters can generate Wowhead `?filter=` query strings.

**Architecture:** Keep path-based filters and query-string filters separate. `mappings.py` will define semantic query filters with stable ordering and `yes/no/any` value mappings; `url_builder.py` will use those mappings to produce `query_string` and append it to the final URL only when needed.

**Tech Stack:** Python 3, unittest

---

### Task 1: Add query filter metadata to mappings

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`

**Step 1: Write the failing test**

Add tests that assert:

- `QUERY_FILTERS["available_to_players"]` exposes Wowhead filter id `161`
- `QUERY_FILTERS["can_be_worn"]` exposes Wowhead filter id `195`
- `QUERY_FILTERS["disenchantable"]` exposes Wowhead filter id `8`
- both filters support `yes/no/any`
- `normalize_task()` fills missing `query_filters` with an empty dict
- `validate_task()` rejects unknown query filter keys and invalid values

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because query filter metadata and validation do not exist yet.

**Step 3: Write minimal implementation**

Add:

- `QUERY_FILTERS`
- a stable order tuple for query filters
- `normalize_task()` support for default empty `query_filters`
- `validate_task()` support for semantic query filters

**Step 4: Run test to verify it passes**

Run the same command and confirm mapping tests pass.

### Task 2: Extend URL builder to output query strings

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/url_builder.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`

**Step 1: Write the failing test**

Add tests that assert:

- `query_filters={"available_to_players": "yes"}` generates `filter=161;1;0`
- adding `can_be_worn: "yes"` generates `filter=161:195;1:1;0:0`
- `query_filters={"disenchantable": "no"}` generates `filter=8;2;0`
- `any` does not appear in the query string
- when there are no active query filters, `query_string` is empty and `url` has no `?`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because the URL builder does not support query strings yet.

**Step 3: Write minimal implementation**

Implement query filter serialization so the URL builder returns:

- `filter_path`
- `path`
- `query_string`
- `url`

Use stable query filter ordering from `mappings.py`.

**Step 4: Run test to verify it passes**

Run the same command and confirm all URL builder tests pass.

### Task 3: Update example task config and docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.example.json`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-mappings.md`

**Step 1: Update the example task config**

Add at least one example task that includes semantic `query_filters`.

**Step 2: Update documentation**

Document:

- semantic `query_filters`
- `yes/no/any` value rules
- `query_string` output from the URL builder

**Step 3: Review for consistency**

Ensure the example config, tests, and docs all use the same query filter names.

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/url_builder.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.example.json`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/mappings.py crawler/core/url_builder.py crawler/tests/test_mappings.py crawler/tests/test_url_builder.py crawler/tasks/wowhead_items.example.json docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-crawler-mappings.md docs/plans/2026-03-14-wowhead-query-filters.md
git commit -m "feat: add wowhead query filters"
```
