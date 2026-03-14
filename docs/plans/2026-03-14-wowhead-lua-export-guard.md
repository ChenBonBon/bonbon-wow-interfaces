# Lua Export Guard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `export_lua` export addon data only when every manifest task has already been fetched successfully.

**Architecture:** Keep `export_lua` as an independent script, but change its stable input from `items.unique.json` to `manifest.json`. The exporter will validate that every task status is `fetched`, then read the sibling `items.unique.json` file and render the Lua itemId set as before.

**Tech Stack:** Python 3, `unittest`, JSON file IO, existing crawler script layer

---

### Task 1: Lock the new behavior with tests

**Files:**
- Modify: `crawler/tests/test_lua_exporter.py`
- Modify: `crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add tests that prove:
- export succeeds when all manifest tasks are `fetched`
- export raises an error when any task is `failed`
- export raises an error when any task is `planned`
- script entrypoint now expects `manifest.json`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_lua_exporter crawler.tests.test_scripts`

Expected: FAIL because the exporter still reads `items.unique.json` directly.

**Step 3: Write minimal implementation**

Update the exporter and script entrypoint to use `manifest.json` and enforce task completeness.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_lua_exporter crawler.tests.test_scripts`

Expected: PASS

**Step 5: Commit**

```bash
git add docs/plans/2026-03-14-wowhead-lua-export-guard.md crawler/core/lua_exporter.py crawler/scripts/export_lua.py crawler/tests/test_lua_exporter.py crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-lua-export-design.md docs/plans/2026-03-14-wowhead-lua-export.md docs/plans/2026-03-14-wowhead-crawler-design.md
git commit -m "fix: require complete manifest before lua export"
```

### Task 2: Update docs to match the guarded export flow

**Files:**
- Modify: `docs/plans/2026-03-14-wowhead-lua-export-design.md`
- Modify: `docs/plans/2026-03-14-wowhead-lua-export.md`
- Modify: `docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Write the failing test**

No automated test needed; this task is documentation-only.

**Step 2: Run test to verify it fails**

Not applicable.

**Step 3: Write minimal implementation**

Document that:
- `export_lua` takes `manifest.json`
- export only proceeds when every task is `fetched`
- exporter reads sibling `items.unique.json`

**Step 4: Run test to verify it passes**

Run the full crawler test suite to ensure behavior and script usage still match the docs:

`cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 5: Commit**

Use the same commit from Task 1 after verification.
