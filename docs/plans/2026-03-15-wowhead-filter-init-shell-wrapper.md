# Wowhead Filter Init Shell Wrapper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a shell wrapper in `crawler/bin/` that runs the existing two-step Filter.init toolchain with one command.

**Architecture:** Keep fetch and extract logic inside the existing Python script layer. The new shell wrapper will only normalize the working directory, define the default HTML path, call `scripts.fetch_filter_page`, then call `scripts.extract_filter_init` on the saved HTML.

**Tech Stack:** POSIX shell, Python 3, `unittest`

---

### Task 1: Lock wrapper behavior with failing tests

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add a test that asserts:

- `crawler/bin/fetch_filter_init.sh` exists and is executable
- it invokes `python3 -m scripts.fetch_filter_page <url> outputs/filter_pages/filter-page.html`
- it then invokes `python3 -m scripts.extract_filter_init outputs/filter_pages/filter-page.html`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: FAIL because the wrapper does not exist yet.

**Step 3: Write minimal implementation**

Create the wrapper with:

- shebang
- strict shell flags
- repo-relative `cd`
- fixed default HTML output path
- the two Python invocations in order

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts`

Expected: PASS

### Task 2: Update docs

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/docs/plans/2026-03-14-wowhead-crawler-design.md`

**Step 1: Document the wrapper**

Add `crawler/bin/fetch_filter_init.sh` to the directory and mention it as the one-command wrapper for the two-step filter extraction flow.

**Step 2: Run verification**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

### Task 3: Commit

**Files:**
- Verify all touched wrapper, tests, and docs

**Step 1: Commit**

```bash
git add crawler/bin/fetch_filter_init.sh crawler/tests/test_scripts.py docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-15-wowhead-filter-init-shell-wrapper.md
git commit -m "feat: add filter init shell wrapper"
```
