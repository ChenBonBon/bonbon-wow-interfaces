# QuickDisenchant Category Filters Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add shared category filters to QuickDisenchant so both windows can filter candidates by weapon/armor type while moving the layout to a 4x2 visible grid.

**Architecture:** Keep scan results in `QD.state.allItems` unchanged and add a view-layer filter key in runtime state. Both windows derive their displayed lists from the same filtered projection, so selection, candidate add/remove, and disenchant queue behavior continue to work without changing core queue logic.

**Tech Stack:** WoW addon Lua, existing QuickDisenchant module split (`Core.lua`, `Data.lua`, `UI.lua`, `Events.lua`)

---

### Task 1: Add shared filter state and filtering helpers

**Files:**
- Modify: `QuickDisenchant/Core.lua`
- Modify: `QuickDisenchant/Data.lua`

**Step 1: Write the failing test**

Because there is no Lua test harness in this repo, define a manual verification target before implementation:
- Expected: there is a single runtime filter key shared by main and candidate windows
- Expected: filter values support `all`, `weapon`, `cloth`, `leather`, `mail`, `plate`, `other`

**Step 2: Run test to verify it fails**

Run: manual code inspection
Expected: no `activeFilterKey` or item filter helper exists yet

**Step 3: Write minimal implementation**

In `QuickDisenchant/Core.lua`:
- extend `QD.state` with `activeFilterKey = "all"`
- ensure `/qd`-time reset can reuse this key

In `QuickDisenchant/Data.lua`:
- add helper to normalize category keys
- add helper to decide whether an item matches the active filter
- add helper returning filtered item lists for:
  - main selected items
  - candidate available items
- keep current scan and selection storage unchanged

**Step 4: Run verification**

Run: static diff review
Expected: new helpers only affect view filtering, not scan/disenchant safety logic

**Step 5: Commit**

```bash
git add QuickDisenchant/Core.lua QuickDisenchant/Data.lua
git commit -m "feat: add quickdisenchant filter state"
```

### Task 2: Resize the visible layout to 4x2

**Files:**
- Modify: `QuickDisenchant/Core.lua`
- Modify: `QuickDisenchant/UI.lua`

**Step 1: Write the failing test**

Manual expectation:
- windows should be wide enough for one-row filters
- visible grid should become 4 columns and 2 rows

**Step 2: Run test to verify it fails**

Run: inspect constants in `Core.lua`
Expected: still `3` columns and `3` visible rows

**Step 3: Write minimal implementation**

In `QuickDisenchant/Core.lua`:
- set `QD.COLUMNS = 4`
- set `QD.VISIBLE_ROWS = 2`
- rely on existing derived size constants to recalculate dimensions

In `QuickDisenchant/UI.lua`:
- verify existing layout math still uses derived constants
- only adjust anchor offsets if needed after the width/height change

**Step 4: Run verification**

Run: static diff review
Expected: layout constants update cleanly without unrelated UI changes

**Step 5: Commit**

```bash
git add QuickDisenchant/Core.lua QuickDisenchant/UI.lua
git commit -m "feat: resize quickdisenchant grid to 4x2"
```

### Task 3: Add filter buttons to both windows

**Files:**
- Modify: `QuickDisenchant/UI.lua`

**Step 1: Write the failing test**

Manual expectation:
- both windows show filter buttons
- filter buttons are single-select
- current selection is visually highlighted

**Step 2: Run test to verify it fails**

Run: inspect `ensureMainWindow()` and `ensureCandidateWindow()`
Expected: no filter controls exist yet

**Step 3: Write minimal implementation**

In `QuickDisenchant/UI.lua`:
- define filter metadata list once
- create reusable helper to build/update filter button rows
- add buttons under the title area in both windows
- wire buttons to:
  - update `QD.state.activeFilterKey`
  - refresh both windows
- adjust scroll frame anchors downward to make room for filter row

**Step 4: Run verification**

Run: static diff review
Expected: buttons are created once per window and refresh state without touching disenchant button wiring

**Step 5: Commit**

```bash
git add QuickDisenchant/UI.lua
git commit -m "feat: add quickdisenchant filter buttons"
```

### Task 4: Render windows from filtered projections

**Files:**
- Modify: `QuickDisenchant/UI.lua`
- Modify: `QuickDisenchant/Data.lua`

**Step 1: Write the failing test**

Manual expectation:
- switching filters changes the shown item count and icon list
- candidate window uses the same active filter as main window

**Step 2: Run test to verify it fails**

Run: inspect `refreshMainWindow()` and candidate refresh path
Expected: both still render from unfiltered lists

**Step 3: Write minimal implementation**

- update main window refresh to render filtered selected items
- update candidate window refresh to render filtered candidate items
- ensure title count uses filtered list length
- keep plus button placement based on filtered visible list

**Step 4: Run verification**

Run: static diff review
Expected: only view lists change; underlying selected key state remains global and intact

**Step 5: Commit**

```bash
git add QuickDisenchant/UI.lua QuickDisenchant/Data.lua
git commit -m "feat: render quickdisenchant windows with filters"
```

### Task 5: Reset filter on scan and verify manually

**Files:**
- Modify: `QuickDisenchant/Events.lua`
- Modify: `QuickDisenchant/Core.lua`
- Modify: `QuickDisenchant/UI.lua`

**Step 1: Write the failing test**

Manual expectation:
- `/qd` always opens with `全部`
- closing and reopening the plugin via `/qd` resets the filter

**Step 2: Run test to verify it fails**

Run: inspect `QD.runScan()`
Expected: no explicit filter reset exists yet

**Step 3: Write minimal implementation**

- reset `QD.state.activeFilterKey = "all"` during scan setup
- refresh windows after reset

**Step 4: Run verification**

Run: game manual test
Expected:
- `/reload`
- `/qd`
- filter row visible in both windows
- layout is 4x2
- switching filters updates both windows
- reopening `/qd` resets to `全部`

**Step 5: Commit**

```bash
git add QuickDisenchant/Events.lua QuickDisenchant/Core.lua QuickDisenchant/UI.lua
git commit -m "feat: reset quickdisenchant filters on scan"
```
