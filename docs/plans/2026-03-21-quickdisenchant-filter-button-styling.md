# QuickDisenchant Filter Button Styling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make QuickDisenchant category filter buttons show candidate counts and use a clearer pressed/unpressed toggle style.

**Architecture:** Keep the existing category filter keys and shared window state unchanged. Add lightweight count helpers derived from `QD.state.allItems`, then update the existing filter button row renderer so button labels include counts and selected buttons render with a pressed visual treatment.

**Tech Stack:** WoW addon Lua, existing QuickDisenchant module split (`Data.lua`, `UI.lua`)

---

### Task 1: Add category count helpers

**Files:**
- Modify: `QuickDisenchant/Data.lua`

**Step 1: Write the failing test**

Manual expectation:
- there is currently no helper that returns counts for all category filters
- UI would need to recompute counts itself

**Step 2: Run test to verify it fails**

Run: inspect `QuickDisenchant/Data.lua`
Expected: no helper exists for `all / weapon / cloth / leather / mail / plate / other` counts

**Step 3: Write minimal implementation**

- add a helper that walks `QD.state.allItems`
- return a table keyed by filter key
- include:
  - `all`
  - `weapon`
  - `cloth`
  - `leather`
  - `mail`
  - `plate`
  - `other`

**Step 4: Run verification**

Run: static diff review
Expected: helper is read-only and based only on existing category classification logic

**Step 5: Commit**

```bash
git add QuickDisenchant/Data.lua
git commit -m "feat: add quickdisenchant filter counts"
```

### Task 2: Update filter buttons to show counts and stronger toggle styling

**Files:**
- Modify: `QuickDisenchant/UI.lua`

**Step 1: Write the failing test**

Manual expectation:
- buttons still show plain labels
- selected and unselected styles are mostly color-only and do not feel like a pressed toggle

**Step 2: Run test to verify it fails**

Run: inspect `ensureFilterButtonRow()` and `updateFilterButtonRow()`
Expected: labels do not include counts and button states do not shift text for pressed feedback

**Step 3: Write minimal implementation**

- when refreshing the button row, fetch category counts
- render labels as `分类(数量)`
- strengthen inactive style to feel raised
- strengthen active style to feel pressed
- move active text slightly downward to reinforce the pressed state

**Step 4: Run verification**

Run: static diff review
Expected: button updates remain purely presentational and do not alter filter state semantics

**Step 5: Commit**

```bash
git add QuickDisenchant/UI.lua
git commit -m "feat: style quickdisenchant filter buttons"
```

### Task 3: Final verification

**Files:**
- Verify: `QuickDisenchant/Data.lua`
- Verify: `QuickDisenchant/UI.lua`

**Step 1: Run verification**

Run: static review plus in-game manual verification

Expected in game:
- `/reload`
- `/qd`
- each button shows `分类(数量)`
- counts reflect all candidate items in the bag for that category
- selected button looks pressed
- unselected buttons look raised
- opening the candidate window preserves the same labels and visual states

**Step 2: Commit**

```bash
git add QuickDisenchant/Data.lua QuickDisenchant/UI.lua
git commit -m "feat: polish quickdisenchant filter buttons"
```
