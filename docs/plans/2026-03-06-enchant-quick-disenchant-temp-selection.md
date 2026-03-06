# Enchant Quick Disenchant Temporary Selection Interaction Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add temporary remove/add interactions with a right-side candidate window while keeping `/eqd` as the only trigger.

**Architecture:** Introduce session state tables (`allItems`, `selectedKeys`) and split rendering into two synchronized windows: selected-items main window and all-items candidate window. Main-window click removes from selection, candidate-window click adds back. Both windows are refreshed from the same source-of-truth state.

**Tech Stack:** WoW Lua API (`CreateFrame`, `UIPanelScrollFrameTemplate`, `SlashCmdList`, `GameTooltip`), table-based in-memory state.

---

### Task 1: Define failing behavior checks (manual RED)

**Files:**
- Test: in-game `/eqd` manual validation

**Step 1: Write the failing test**
Define failures in current build:
- no `+` button for candidate window
- no temporary remove/add interactions
- no disabled-state candidate list

**Step 2: Run test to verify it fails**
Run: execute `/eqd` and attempt requested interactions.
Expected: FAIL against new interaction requirements.

**Step 3: Write minimal implementation**
N/A for this observation-only task.

**Step 4: Run test to verify it passes**
Deferred to Task 4 after implementation.

**Step 5: Commit**
No commit for this observation-only task.

### Task 2: Refactor state and item identity

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: no stable selected/unselected state can be toggled per item.

**Step 2: Run test to verify it fails**
Run: static inspection and in-game interaction attempt.
Expected: state model missing.

**Step 3: Write minimal implementation**
Add:
- `allItems`, `allItemsByKey`, `selectedKeys`
- key generation from `bagID:slotID`
- selection reset to all selected on `/eqd`

**Step 4: Run test to verify it passes**
Run: `/eqd` and verify main list reflects selected state source.
Expected: all items selected initially.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "refactor: add session selection state for /eqd items"
```

### Task 3: Implement dual-window interactions

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: no `+` button, no right window, no click-to-remove/add.

**Step 2: Run test to verify it fails**
Run: `/eqd` with interaction attempts.
Expected: requested behavior absent.

**Step 3: Write minimal implementation**
Implement:
- `+` button in main window
- right candidate window anchored to main window
- main icon left/right click removes from selected
- candidate icon click adds back when not selected
- selected candidate icons desaturated + disabled

**Step 4: Run test to verify it passes**
Run: `/eqd` then remove/add operations.
Expected: two windows synchronized per interaction.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: add candidate window and temporary remove/add interactions"
```

### Task 4: Synchronization and close behavior hardening

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: closing main window leaves candidate window open, or stale states remain.

**Step 2: Run test to verify it fails**
Run: open both windows then close main; repeat `/eqd`.
Expected: mismatch before hardening.

**Step 3: Write minimal implementation**
Add:
- main `OnHide` closes candidate window
- full refresh of both windows after selection mutation
- `/eqd` reset behavior to all-selected

**Step 4: Run test to verify it passes**
Run: complete manual flow from requirements.
Expected: all interactions and close behavior correct.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "fix: synchronize candidate window state and close behavior"
```
