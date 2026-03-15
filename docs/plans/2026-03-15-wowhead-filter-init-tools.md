# Wowhead Filter Init Tools Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a two-step utility that first saves a Wowhead page HTML locally, then extracts raw `Filter.init(...)` data from that local HTML into JSON.

**Architecture:** Keep fetch and parse separate. The fetch script writes raw HTML into `crawler/outputs/filter_pages/`. The extract script reads a local HTML file, locates `Filter.init(...)`, parses its payload, and writes a sibling `.filters.json` output. Shared parsing helpers live in a new `core/filter_init.py`.

**Tech Stack:** Python 3, `unittest`, JSON, regex/string scanning, `urllib.request`

---

### Task 1: Lock parsing behavior with failing tests

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_filter_init.py`

**Step 1: Write the failing test**

Add tests that assert:

- local HTML containing `Filter.init({...});` can be parsed into Python data
- extracted JSON can be written to disk
- fetch helper can write fetched HTML to the target file path when provided a fake fetch function

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_filter_init`

Expected: FAIL because `core.filter_init` and related scripts do not exist yet.

**Step 3: Write minimal implementation**

Add only the smallest interfaces needed for tests to import and exercise the two-step flow.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_filter_init`

Expected: PASS

### Task 2: Add script entrypoints

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/filter_init.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/fetch_filter_page.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/extract_filter_init.py`

**Step 1: Write the failing test**

Extend tests if needed so they also cover:

- default output naming for fetched HTML
- default output naming for extracted JSON
- script entrypoints return output file paths

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_filter_init`

Expected: FAIL because the helpers and scripts do not yet satisfy the expected behavior.

**Step 3: Write minimal implementation**

Implement:

- HTML fetch helper
- `Filter.init(...)` payload extraction helper
- JSON writer
- thin script wrappers

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_filter_init`

Expected: PASS

### Task 3: Update docs and verify

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Document the new tools**

Add the new core module and scripts, and document the two-step workflow:

1. fetch HTML
2. extract `Filter.init`

**Step 2: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

### Task 4: Commit

**Files:**
- Verify all touched code, tests, and docs

**Step 1: Commit**

```bash
git add crawler/core/filter_init.py crawler/scripts/fetch_filter_page.py crawler/scripts/extract_filter_init.py crawler/tests/test_filter_init.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-15-wowhead-filter-init-tools.md
git commit -m "feat: add wowhead filter init tools"
```
