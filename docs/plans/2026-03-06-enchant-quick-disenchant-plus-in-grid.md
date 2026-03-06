# Enchant Quick Disenchant Plus-In-Grid Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Render the `+` action button as the `(n+1)`th slot in the main 3-column grid instead of the header area.

**Architecture:** Keep current selection/candidate state model. Remove header plus button, introduce one dedicated in-grid plus button that is positioned using the same index math as normal item cells. Main-window content height includes the extra plus slot.

**Tech Stack:** WoW Lua API (`CreateFrame`, `UIPanelButtonTemplate`), existing grid rendering helpers.

---

### Task 1: Define failing behavior check (manual RED)

**Files:**
- Test: in-game `/eqd` interaction

**Step 1: Write the failing test**
Define failure in current build: plus remains in header instead of grid slot `n+1`.

**Step 2: Run test to verify it fails**
Run: `/eqd` and manipulate selection counts.
Expected: FAIL against new placement rule.

**Step 3: Write minimal implementation**
N/A for observation-only task.

**Step 4: Run test to verify it passes**
Deferred to Task 3 after implementation.

**Step 5: Commit**
No commit for this observation-only task.

### Task 2: Refactor main window controls

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: no reusable plus control exists for in-grid placement.

**Step 2: Run test to verify it fails**
Run: static inspection and in-game check.
Expected: plus still tied to header.

**Step 3: Write minimal implementation**
- remove header `plusButton`
- create dedicated `gridPlusButton` with click handler for candidate toggle

**Step 4: Run test to verify it passes**
Run: `/eqd`.
Expected: plus control available for grid rendering.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "refactor: replace header plus button with grid plus control"
```

### Task 3: Place plus at n+1 and update content height

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: plus does not move to `n+1` when selected count changes.

**Step 2: Run test to verify it fails**
Run: remove/add items and observe plus slot.
Expected: incorrect placement before update.

**Step 3: Write minimal implementation**
- compute plus index as `#selectedItems + 1`
- position plus with same grid formula
- include plus slot in main content height calculation

**Step 4: Run test to verify it passes**
Run: verify `n=0`, `n=8`, `n=10` placement examples.
Expected: plus always at slot `n+1`.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: render plus button at n+1 grid slot"
```

### Task 4: Regression checks for candidate interactions

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua` (if needed)

**Step 1: Write the failing test**
Define failure: plus click no longer toggles candidate window after relocation.

**Step 2: Run test to verify it fails**
Run: click plus repeatedly and perform remove/add operations.
Expected: mismatch if wiring broken.

**Step 3: Write minimal implementation**
Adjust event wiring/refresh path if any regression appears.

**Step 4: Run test to verify it passes**
Run: end-to-end scenario with remove/add and candidate toggling.
Expected: behavior unchanged except placement.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "fix: preserve candidate toggle behavior after plus relocation"
```
