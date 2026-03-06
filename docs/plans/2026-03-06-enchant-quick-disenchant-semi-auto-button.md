# Enchant Quick Disenchant Semi-Auto Button Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a bottom `分解` button that semi-automates disenchanting one selected item per click with robust feedback.

**Architecture:** Keep current selection/candidate model and add one action button in main window. Clicking triggers protected action attempt on queue head (`selectedItems[1]`), then resolves result by checking bag state in `BAG_UPDATE_DELAYED` (or timeout fallback).

**Tech Stack:** WoW Lua API (`CastSpellByName`/`CastSpellByID`, `C_Container.UseContainerItem`, `C_Timer.After`, `BAG_UPDATE_DELAYED`, `UIPanelButtonTemplate`).

---

### Task 1: Define failing behavior checks (manual RED)

**Files:**
- Test: in-game `/eqd` flow

**Step 1: Write the failing test**
Current failure: no bottom disenchant button and no one-click-one-item processing path.

**Step 2: Run test to verify it fails**
Run: `/eqd` and inspect main window.
Expected: `分解` button absent.

**Step 3: Write minimal implementation**
N/A for observation-only task.

**Step 4: Run test to verify it passes**
Deferred to Task 4.

**Step 5: Commit**
No commit for this observation-only task.

### Task 2: Add main window `分解` button and queue-head selection

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: button exists but does not target first selected item consistently.

**Step 2: Run test to verify it fails**
Run: manual click behavior inspection.
Expected: queue-head logic missing.

**Step 3: Write minimal implementation**
- Add bottom button in main window
- Add helper to fetch queue head from current selected order
- Guard empty queue and missing spell conditions with hints

**Step 4: Run test to verify it passes**
Run: `/eqd`, click button.
Expected: button action targets only current first item.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: add main window disenchant action button"
```

### Task 3: Implement attempt + pending resolution

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: failed attempt still removes item, or no feedback path exists.

**Step 2: Run test to verify it fails**
Run: create a failure condition and click button.
Expected: incorrect state handling before implementation.

**Step 3: Write minimal implementation**
- Create `pendingDisenchant` state
- Attempt cast + use item
- Resolve result on `BAG_UPDATE_DELAYED` or timeout
- Success removes key from `selectedKeys`; failure keeps it

**Step 4: Run test to verify it passes**
Run: success and failure scenarios.
Expected: one item per click, correct success/failure retention, feedback shown.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: process one disenchant target per click with feedback"
```

### Task 4: Sync refresh and edge-case hardening

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: pending state gets stuck or candidate/main views desync.

**Step 2: Run test to verify it fails**
Run: repeated button clicks and bag changes.
Expected: stale state in edge path before hardening.

**Step 3: Write minimal implementation**
- prevent reentry while pending
- always clear pending on resolve/timeout
- refresh both windows after success

**Step 4: Run test to verify it passes**
Run: multiple click cycles.
Expected: stable pending lifecycle and synchronized windows.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "fix: harden semi-auto disenchant pending lifecycle"
```
