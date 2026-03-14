# Wowhead Lua Export Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Export unique Wowhead item IDs into a Lua data file that QuickDisenchant can load directly.

**Architecture:** Keep export separate from aggregation. A dedicated exporter reads `items.unique.json`, renders a stable Lua table of `itemId -> true`, writes a new Lua file into the addon folder, and the addon `.toc` loads that file before bag-scan logic runs.

**Tech Stack:** Python 3, unittest, JSON

---

### Task 1: Define Lua export behavior with failing tests

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_lua_exporter.py`

**Step 1: Write the failing test**

Write tests that assert:

- `render_lua_item_id_table()` produces a Lua table keyed by `itemId`
- output is sorted by `itemId`
- `write_lua_item_id_table()` writes a Lua file from `items.unique.json`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.lua_exporter` does not exist yet.

**Step 3: Write minimal implementation**

Add the smallest possible exporter interface for tests to import.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to missing render/write behavior.

### Task 2: Add script adapter and toc integration

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/lua_exporter.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/export_lua.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/QuickDisenchant/QuickDisenchant.toc`

**Step 1: Write the failing test**

Extend tests so they assert:

- `scripts.export_lua.run()` writes the Lua file
- `QuickDisenchant.toc` contains `DisenchantableByWowhead.lua`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because the script and toc integration do not exist yet.

**Step 3: Write minimal implementation**

Implement:

- `render_lua_item_id_table(items)`
- `write_lua_item_id_table(items_unique_path, output_path=None)`
- `scripts.export_lua.run(argv=None)`
- `.toc` entry for `DisenchantableByWowhead.lua`

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Add generated Lua file placeholder and update docs

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/QuickDisenchant/DisenchantableByWowhead.lua`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Add placeholder file**

Create an initial minimal Lua file with an empty `QD.WOWHEAD_DISENCHANTABLE_ITEM_IDS` table.

**Step 2: Update docs**

Document:

- Lua export step
- target Lua file path

### Task 4: Verify and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/lua_exporter.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/scripts/export_lua.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_lua_exporter.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/QuickDisenchant/DisenchantableByWowhead.lua`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/QuickDisenchant/QuickDisenchant.toc`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/core/lua_exporter.py crawler/scripts/export_lua.py crawler/tests/test_lua_exporter.py crawler/tests/test_scripts.py QuickDisenchant/DisenchantableByWowhead.lua QuickDisenchant/QuickDisenchant.toc docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-lua-export-design.md docs/plans/2026-03-14-wowhead-lua-export.md
git commit -m "feat: export wowhead item ids to lua"
```
