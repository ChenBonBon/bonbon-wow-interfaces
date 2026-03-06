# Enchant Quick Disenchant Native Plus and ESC Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update plus-slot visuals to Blizzard native item-upgrade style, rename main title to `可分解装备`, and support `Esc` key closing of addon windows.

**Architecture:** Keep current state and dual-window interaction flow. Replace plus button skin with atlas-driven textures and add special-frame registration for ESC handling. Candidate close remains piggybacked on main frame `OnHide`.

**Tech Stack:** WoW Lua UI API (`SetNormalAtlas`, textures with `SetAtlas`, `UISpecialFrames`, frame show/hide lifecycle).

---

### Task 1: Define failing behavior checks (manual RED)

**Files:**
- Test: in-game `/eqd` and ESC behavior

**Step 1: Write the failing test**
Current failures:
- plus icon style not matching native item-upgrade visuals
- main title is not `可分解装备`
- ESC does not close addon windows

**Step 2: Run test to verify it fails**
Run: `/eqd`, inspect UI, press ESC.
Expected: FAIL against target requirements.

**Step 3: Write minimal implementation**
N/A for observation-only task.

**Step 4: Run test to verify it passes**
Deferred to Task 3.

**Step 5: Commit**
No commit for this observation-only task.

### Task 2: Style plus slot with native item-upgrade atlases

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: plus still uses generic button template visuals.

**Step 2: Run test to verify it fails**
Run: `/eqd` and inspect plus appearance.
Expected: non-native style.

**Step 3: Write minimal implementation**
- apply `itemupgrade_greenplusicon` / `_pressed` atlases
- add slot border and inner-glow atlas textures

**Step 4: Run test to verify it passes**
Run: `/eqd`.
Expected: plus slot visually resembles item-upgrade style.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: apply native item-upgrade style to plus slot"
```

### Task 3: Update title and ESC close behavior

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define failure: title text and ESC close behavior mismatched.

**Step 2: Run test to verify it fails**
Run: `/eqd`, press ESC.
Expected: title/ESC behavior incorrect before change.

**Step 3: Write minimal implementation**
- set main title to `可分解装备 (%d)`
- register main frame name in `UISpecialFrames`

**Step 4: Run test to verify it passes**
Run: `/eqd`, open candidate, press ESC.
Expected: both windows close and title is updated.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: rename title and close windows on ESC"
```
