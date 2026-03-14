# Run-All Export Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `run_all` finish with Lua export, and make `retry_failed_run` continue through aggregate and export after retrying failed fetch tasks.

**Architecture:** Keep orchestration in the script layer. `run_all` will execute `generate -> fetch(planned) -> aggregate(all fetched) -> export(all fetched)`. `retry_failed_run` will execute `retry_fetch(failed) -> aggregate(all fetched) -> export(all fetched)`. Export remains the gate that aborts if the manifest is still incomplete.

**Tech Stack:** Python 3, `unittest`, existing crawler script layer

---

### Task 1: Lock orchestration changes with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add tests that assert:

- `run_all()` writes `DisenchantableByWowhead.lua` when every task fetch succeeds
- `run_all()` raises when export sees incomplete manifest
- `retry_failed_run()` retries failed fetches, then rewrites `items.unique.json`, then exports Lua

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: FAIL because the current script orchestration stops before export.

**Step 3: Write minimal implementation**

Update only the thin script adapters needed to satisfy the new orchestration.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: PASS

### Task 2: Update script docs to reflect full completion flow

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-run-all-design.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-run-all.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-retry-failed-design.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-retry-failed.md`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Write the docs change**

Document that:

- `run_all` now ends with export
- `retry_failed_run` now ends with aggregate and export
- export still aborts on incomplete manifest

**Step 2: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

### Task 3: Commit

**Files:**
- Verify and stage all touched script, test, and doc files

**Step 1: Commit**

```bash
git add crawler/scripts/run_all.py crawler/scripts/retry_failed_run.py crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-run-all-design.md docs/plans/2026-03-14-wowhead-run-all.md docs/plans/2026-03-14-wowhead-retry-failed-design.md docs/plans/2026-03-14-wowhead-retry-failed.md docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-run-all-export.md
git commit -m "feat: export lua from crawler orchestration"
```
