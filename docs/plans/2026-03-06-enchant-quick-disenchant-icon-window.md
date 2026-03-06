# Enchant Quick Disenchant Icon Window Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace chat summary output with a slash-command-driven icon window that lists all disenchantable bag equipment in a 3-column scrollable grid.

**Architecture:** Keep scan logic in one Lua file and add a lightweight reusable UI layer (main frame + scroll frame + icon buttons). `/eqd` performs spell gate and scan, then renders the icon grid. UI elements are initialized once and reused on each command run.

**Tech Stack:** WoW Lua API (`SlashCmdList`, `CreateFrame`, `UIPanelScrollFrameTemplate`, `GameTooltip`, `C_Container`, `C_Item`, `IsSpellKnown*`).

---

### Task 1: Define failing behavior checks (manual RED)

**Files:**
- Test: in-game `/eqd` manual behavior against current build

**Step 1: Write the failing test**
Define failures for current implementation:
- `/eqd` still prints bag totals and quality split to chat
- no 3x3 icon window is shown

**Step 2: Run test to verify it fails**
Run: execute `/eqd` in-game on enchanting character.
Expected: FAIL against new requirement (chat summary exists, no grid window).

**Step 3: Write minimal implementation**
N/A for this task.

**Step 4: Run test to verify it passes**
Deferred to Task 3/4 after implementation.

**Step 5: Commit**
No commit for this observation-only task.

### Task 2: Build reusable window and icon-grid rendering

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: creating UI does not show 3-column layout, scroll, or tooltip.

**Step 2: Run test to verify it fails**
Run: execute `/eqd` before UI code exists.
Expected: no icon grid shown.

**Step 3: Write minimal implementation**
Implement:
- one-time `ensureWindow()` frame creation
- scroll frame/content frame
- dynamic icon buttons
- tooltip handlers (`OnEnter`/`OnLeave`)
- empty-state text

**Step 4: Run test to verify it passes**
Run: `/eqd` with known disenchantable items.
Expected: 3-column icon grid appears; hover shows tooltip.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: add scrollable 3-column icon window for /eqd"
```

### Task 3: Wire command flow and remove chat summary output

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: `/eqd` still prints slot/quality summary or auto opens without command.

**Step 2: Run test to verify it fails**
Run: execute `/eqd` and login behavior checks.
Expected: summary text still appears before refactor.

**Step 3: Write minimal implementation**
Refactor `runScan()`:
- retain spell gate and not-learned hint
- remove bag total/quality chat summary lines
- scan items and call render function
- show window only on successful command run

**Step 4: Run test to verify it passes**
Run: `/eqd` with and without spell 7411.
Expected:
- without spell: hint only, no window
- with spell: window opens and refreshes, no summary chat lines

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "refactor: show disenchant items in window and remove summary output"
```

### Task 4: Regression and refresh correctness

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua` (if required)

**Step 1: Write the failing test**
Define failure: stale icons remain after inventory shrinks, or scroll content height incorrect.

**Step 2: Run test to verify it fails**
Run: `/eqd`, change bag items, `/eqd` again.
Expected: stale icon bug before cleanup logic.

**Step 3: Write minimal implementation**
Hide unused buttons, recompute content height each render, refresh title count.

**Step 4: Run test to verify it passes**
Run: repeated `/eqd` after inventory changes.
Expected: icons and scrolling fully match current bag state.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "fix: refresh icon grid state and scroll metrics correctly"
```
