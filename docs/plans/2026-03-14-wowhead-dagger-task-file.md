# Wowhead Dagger Task File Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the default task file with only the three `main_hand + dagger` weapon tasks for `uncommon`, `rare`, and `epic`.

**Architecture:** Keep the task schema unchanged. Update `crawler/tasks/wowhead_items.json` so it contains only three weapon tasks with shared query filters: `available_to_players=yes`, `can_be_worn=yes`, and `disenchantable=no`.

**Tech Stack:** JSON, Python 3, `unittest`

---

### Task 1: Lock the desired task file content with a failing test

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`

**Step 1: Write the failing test**

Add a test that asserts `crawler/tasks/wowhead_items.json`:

- contains exactly 3 tasks
- task ids are:
  - `uncommon-main-hand-dagger`
  - `rare-main-hand-dagger`
  - `epic-main-hand-dagger`
- every task is valid under `validate_task()`
- every task uses:
  - `category = weapon`
  - `slot = main_hand`
  - `type = dagger`
  - `query_filters = {"available_to_players": "yes", "can_be_worn": "yes", "disenchantable": "no"}`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings`

Expected: FAIL because the current default task file still contains mixed sample tasks.

**Step 3: Write minimal implementation**

Replace `crawler/tasks/wowhead_items.json` with the three agreed dagger tasks.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings`

Expected: PASS

### Task 2: Run full verification and commit

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.json`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`

**Step 1: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 2: Commit**

```bash
git add crawler/tasks/wowhead_items.json crawler/tests/test_mappings.py docs/plans/2026-03-14-wowhead-dagger-task-file.md
git commit -m "chore: seed default dagger crawler tasks"
```
