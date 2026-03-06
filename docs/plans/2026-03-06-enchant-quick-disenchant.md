# Enchant Quick Disenchant Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone CN Retail 120001 addon that only outputs on login for enchanting characters, including bag totals and disenchantable equipment counts split by quality.

**Architecture:** Create a new addon folder with a `.toc` and single Lua runtime file. On `PLAYER_LOGIN`, gate execution by enchanting profession presence, then iterate current bag containers, aggregate total/free slots, detect disenchantable equipment via tooltip text scan, and print a compact summary plus quality breakdown.

**Tech Stack:** WoW Lua API (`Frame` events, `C_Container`, `C_TooltipInfo` fallback with `GameTooltip`, `GetProfessions`, `GetProfessionInfo`), addon `.toc` metadata.

---

### Task 1: Scaffold standalone addon files

**Files:**
- Create: `EnchantQuickDisenchant/EnchantQuickDisenchant.toc`
- Create: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define manual failure condition: addon folder and metadata file do not exist, so addon cannot load in the in-game addons list.

**Step 2: Run test to verify it fails**
Run: in-game addon list inspection before files are created.
Expected: addon `EnchantQuickDisenchant` is missing.

**Step 3: Write minimal implementation**
Create `.toc` with interface `120001` and load `EnchantQuickDisenchant.lua`.

**Step 4: Run test to verify it passes**
Run: in-game addon list inspection.
Expected: addon appears as loadable.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.toc EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: scaffold EnchantQuickDisenchant addon"
```

### Task 2: Implement profession-gated bag and disenchant counters

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define manual failure condition: on login, addon either always prints (without enchanting) or fails to print correct counts and quality groups for disenchantable items.

**Step 2: Run test to verify it fails**
Run: login test in-game with expected scenario.
Expected: incorrect or missing behavior before implementation.

**Step 3: Write minimal implementation**
Implement in one pass:
- enchanting gate via `GetProfessions()` + `GetProfessionInfo(index)` and `skillLine == 333`
- bag totals via `C_Container.GetContainerNumSlots` and `C_Container.GetContainerNumFreeSlots`
- slot iteration via `C_Container.GetContainerItemInfo`
- quality filter `>= Uncommon`
- tooltip text scan for `"可分解"`
- grouped counts for green/blue/purple/orange
- login print output (summary + optional quality detail)

**Step 4: Run test to verify it passes**
Run: login in-game with enchanting and without enchanting.
Expected: no-enchanting silent; enchanting prints summary and valid quality split.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "feat: add enchanting-gated disenchant count output"
```

### Task 3: Hardening and fallback behavior

**Files:**
- Modify: `EnchantQuickDisenchant/EnchantQuickDisenchant.lua`

**Step 1: Write the failing test**
Define manual failure condition: nil API values or unavailable tooltip path causes Lua errors.

**Step 2: Run test to verify it fails**
Run: static inspection + in-game edge-case login.
Expected: potential nil arithmetic/string access before guards.

**Step 3: Write minimal implementation**
Add nil-safe defaults (`or 0`, `or false`, empty string guards), and fallback from `C_TooltipInfo` path to hidden `GameTooltip` scan path.

**Step 4: Run test to verify it passes**
Run: login and verify chat output + no Lua errors.
Expected: stable output with graceful degradation.

**Step 5: Commit**
```bash
git add EnchantQuickDisenchant/EnchantQuickDisenchant.lua
git commit -m "fix: harden tooltip and nil handling for disenchant scan"
```
