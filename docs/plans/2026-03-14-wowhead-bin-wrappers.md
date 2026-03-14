# Wowhead Bin Wrappers Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add thin shell wrappers under `crawler/bin/` for the two common crawler entrypoints.

**Architecture:** Keep all business logic in the existing Python script layer. The new shell scripts only normalize the working directory to `crawler/` and forward all arguments to `python3 -m scripts.run_all` or `python3 -m scripts.retry_failed_run`.

**Tech Stack:** POSIX shell, Python 3, `unittest`

---

### Task 1: Lock wrapper behavior with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add tests that assert:

- `crawler/bin/run_all.sh` exists
- `crawler/bin/retry_failed.sh` exists
- both files are executable
- running either script without arguments surfaces the underlying Python usage message

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: FAIL because the shell wrappers do not exist yet.

**Step 3: Write minimal implementation**

Create the two shell wrappers with only:

- shebang
- strict shell flags
- repo-relative `cd`
- `python3 -m scripts... "$@"`

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: PASS

### Task 2: Update docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Document bin wrappers**

Add `crawler/bin/` to the directory design and mention the two wrapper scripts as the recommended short commands.

**Step 2: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

### Task 3: Commit

**Files:**
- Verify all touched wrapper, test, and doc files

**Step 1: Commit**

```bash
git add crawler/bin/run_all.sh crawler/bin/retry_failed.sh crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-bin-wrappers.md
git commit -m "feat: add crawler shell wrappers"
```
