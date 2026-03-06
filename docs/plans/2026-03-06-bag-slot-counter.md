# Bag Slot Counter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a minimal WoW addon for CN Retail 120001 that prints total bag slots and total free bag slots once on login.

**Architecture:** Register `PLAYER_LOGIN` on a frame. On event fire, iterate all equipped bag container IDs, aggregate slot counts using `C_Container` APIs, and print one chat message. Keep implementation single-file for maintainability and low risk.

**Tech Stack:** WoW Lua API, `.toc` addon metadata, event-driven frame scripting.

---

### Task 1: Scaffold Addon Files

**Files:**
- Create: `BagSlotCounter/BagSlotCounter.toc`
- Create: `BagSlotCounter/BagSlotCounter.lua`

**Step 1: Write the failing test**
Define manual failing behavior expectation: addon folder missing means addon cannot load.

**Step 2: Run test to verify it fails**
Run in game addon list check.
Expected: addon not present before files are created.

**Step 3: Write minimal implementation**
Create `.toc` with Interface `120001` and load `BagSlotCounter.lua`.

**Step 4: Run test to verify it passes**
Run in game addon list check again.
Expected: addon appears and is loadable.

**Step 5: Commit**
`git add BagSlotCounter/BagSlotCounter.toc BagSlotCounter/BagSlotCounter.lua`
`git commit -m "feat: scaffold bag slot counter addon"`

### Task 2: Implement Slot Aggregation and Chat Output

**Files:**
- Modify: `BagSlotCounter/BagSlotCounter.lua`

**Step 1: Write the failing test**
Define manual failing behavior expectation: login prints nothing or incorrect totals.

**Step 2: Run test to verify it fails**
Login in game before logic is implemented.
Expected: no valid slot totals in chat.

**Step 3: Write minimal implementation**
Implement event handler using:
- `C_Container.GetContainerNumSlots`
- `C_Container.GetContainerNumFreeSlots`
- loop bag IDs `0..NUM_TOTAL_EQUIPPED_BAG_SLOTS`
- `print` output with total and free counts.

**Step 4: Run test to verify it passes**
Login in game with bags equipped.
Expected: one chat line with numeric totals, no Lua error.

**Step 5: Commit**
`git add BagSlotCounter/BagSlotCounter.lua`
`git commit -m "feat: print total and free bag slots on login"`

### Task 3: Basic Robustness Validation

**Files:**
- Modify: `BagSlotCounter/BagSlotCounter.lua` (only if needed)

**Step 1: Write the failing test**
Define manual failing behavior expectation: nil API result triggers Lua error.

**Step 2: Run test to verify it fails**
Simulate edge condition by code inspection and static check.
Expected: potential arithmetic on nil if guards are missing.

**Step 3: Write minimal implementation**
Add nil-safe numeric fallback (`or 0`) to both slot and free-slot reads.

**Step 4: Run test to verify it passes**
Login and inspect chat output.
Expected: no Lua errors and numeric output always prints.

**Step 5: Commit**
`git add BagSlotCounter/BagSlotCounter.lua`
`git commit -m "fix: guard bag API values with safe numeric fallback"`
