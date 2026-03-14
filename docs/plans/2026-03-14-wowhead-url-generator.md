# Wowhead URL Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a URL generator that converts semantic crawler tasks into stable Wowhead item listing URLs.

**Architecture:** Keep URL assembly separate from the semantic mappings module. `mappings.py` owns Wowhead metadata for category, quality, slot, and type; a new `url_builder.py` module validates tasks, reads that metadata, and returns `url`, `path`, and `filter_path` in a fixed order.

**Tech Stack:** Python 3, unittest

---

### Task 1: Extend mappings metadata for category paths

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`

**Step 1: Write the failing test**

Add a test that asserts `weapon` exposes Wowhead path `weapons` and `armor` exposes Wowhead path `armor`.

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because category metadata does not include Wowhead path yet.

**Step 3: Write minimal implementation**

Add `wowhead.path` to `CATEGORIES` entries.

**Step 4: Run test to verify it passes**

Run the same command and confirm the new assertion passes.

### Task 2: Add URL builder behavior

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/url_builder.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`

**Step 1: Write the failing test**

Add tests that assert:

- an armor task builds `path` as `items/armor/quality:2/slot:1/type:1`
- a weapon task builds `path` as `items/weapons/quality:3/slot:21/type:15`
- `url` prefixes the generated path with `https://www.wowhead.com/`
- `filter_path` only includes the filter portion in `quality/slot/type` order

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.url_builder` does not exist yet.

**Step 3: Write minimal implementation**

Implement a pure helper that validates the task, reads Wowhead metadata from mappings, and returns:

- `url`
- `path`
- `filter_path`

**Step 4: Run test to verify it passes**

Run the same command and confirm all crawler tests pass.

### Task 3: Update design docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-mappings.md`

**Step 1: Write the doc update**

Document that `category` now also exposes `wowhead.path` and participates in URL assembly.

**Step 2: Verify docs reflect the new contract**

Check the updated sections for:

- `category -> path`
- `quality/slot/type -> facet/value`
- URL output fields `url`, `path`, `filter_path`

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/url_builder.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/mappings.py crawler/core/url_builder.py crawler/tests/test_mappings.py crawler/tests/test_url_builder.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-crawler-mappings.md docs/plans/2026-03-14-wowhead-url-generator.md
git commit -m "feat: add wowhead url generator"
```
