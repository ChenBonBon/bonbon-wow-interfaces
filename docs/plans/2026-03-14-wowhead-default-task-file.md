# Wowhead Default Task File Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `crawler/bin/run_all.sh` use `tasks/wowhead_items.json` by default while still allowing callers to override the task file explicitly.

**Architecture:** Keep the defaulting logic only in the shell wrapper. When no positional arguments are provided, `run_all.sh` injects `tasks/wowhead_items.json` before forwarding to `python3 -m scripts.run_all`. If arguments are provided, it forwards them unchanged.

**Tech Stack:** POSIX shell, Python 3, `unittest`

---

### Task 1: Lock default task behavior with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add tests that assert:

- `run_all.sh` calls `python3 -m scripts.run_all tasks/wowhead_items.json` when no args are provided
- `run_all.sh` forwards explicit arguments unchanged when args are provided

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: FAIL because `run_all.sh` currently forwards arguments without injecting a default task file.

**Step 3: Write minimal implementation**

Add a simple shell conditional around `"$#"` and prepend the default task path only when the wrapper is called with no args.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: PASS

### Task 2: Update docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-bin-wrappers.md`

**Step 1: Document the default**

Document that:

- `./bin/run_all.sh` defaults to `tasks/wowhead_items.json`
- passing arguments still overrides the default

**Step 2: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

### Task 3: Commit

**Files:**
- Verify all touched wrapper, test, and doc files

**Step 1: Commit**

```bash
git add crawler/bin/run_all.sh crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-bin-wrappers.md docs/plans/2026-03-14-wowhead-default-task-file.md
git commit -m "feat: add default crawler task file"
```
