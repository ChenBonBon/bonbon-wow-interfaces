# Wowhead Crawler Mappings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the first crawler slice by adding a Python skeleton, a semantic mappings module, an example task config, and tests for task validation and description behavior.

**Architecture:** Keep crawler task configuration fully semantic and isolate all category/type metadata in a single mappings module. Start with tests that define the expected task shape and helper behavior, then implement the smallest possible Python package to satisfy them.

**Tech Stack:** Python 3, unittest, JSON task configuration

---

### Task 1: Add the Python crawler skeleton

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/pyproject.toml`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/__init__.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/__init__.py`

**Step 1: Write the failing test**

Create a test file that imports `core.mappings` and expects import to fail before the package exists.

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: import failure because `core.mappings` does not exist yet.

**Step 3: Write minimal implementation**

Add `pyproject.toml` with a minimal `pytest` dependency declaration and create empty package marker files.

**Step 4: Run test to verify it still fails for the right reason**

Run the same command and confirm the failure is now specifically about the missing `mappings.py`.

**Step 5: Commit**

```bash
git add crawler/pyproject.toml crawler/core/__init__.py crawler/tests/__init__.py
git commit -m "feat: add crawler python skeleton"
```

### Task 2: Define tests for semantic mappings behavior

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`

**Step 1: Write the failing test**

Write tests that assert:

- `describe_task()` returns Chinese labels
- `build_task_slug()` uses semantic identifiers
- `validate_task()` rejects category/type mismatches
- `normalize_task()` fills a missing `enabled` field with `True`
- `get_category_type_meta()` returns metadata for a valid pair
- category metadata exposes Wowhead `path`
- quality, slot, and type metadata expose Wowhead `facet/value`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.mappings` is missing or incomplete.

**Step 3: Write minimal implementation**

Add only the code needed for the tests to import and begin exercising the expected interface.

**Step 4: Run test to verify progress**

Run the same command and confirm failures now point to specific missing behavior.

**Step 5: Commit**

```bash
git add crawler/tests/test_mappings.py crawler/core/mappings.py
git commit -m "test: define crawler mappings behavior"
```

### Task 2.5: Add URL builder behavior

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/url_builder.py`
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`

**Step 1: Write the failing test**

Write tests that assert:

- an armor task produces `filter_path`, `path`, and `url`
- a weapon task produces `filter_path`, `path`, and `url`
- filter segment order is fixed as `quality/slot/type`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because `core.url_builder` does not exist yet.

**Step 3: Write minimal implementation**

Implement a pure helper that validates the task and returns:

- `filter_path`
- `path`
- `url`

**Step 4: Run test to verify it passes**

Run the same command and confirm the URL builder tests pass.

### Task 2.6: Add semantic query filter support

**Files:**
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/url_builder.py`
- Modify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_url_builder.py`

**Step 1: Write the failing test**

Write tests that assert:

- `query_filters` uses semantic filter names
- each query filter exposes a Wowhead filter id
- values use `yes/no/any`
- URL builder outputs `query_string` and appends it only when active filters exist

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because query filter metadata and serialization do not exist yet.

**Step 3: Write minimal implementation**

Add:

- `QUERY_FILTERS`
- stable query filter ordering
- `normalize_task()` default for `query_filters`
- `validate_task()` rules for query filter keys and values
- URL builder query string serialization

**Step 4: Run test to verify it passes**

Run the same command and confirm all tests pass.

### Task 3: Implement the mappings module

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`

**Step 1: Write the failing test**

Extend the tests if needed so that all expected labels and category/type combinations are explicitly covered.

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL on missing validation or formatting rules.

**Step 3: Write minimal implementation**

Implement:

- semantic constants with Chinese labels
- validation helpers
- normalization helper
- task slug builder
- Chinese task description formatter

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 5: Commit**

```bash
git add crawler/core/mappings.py crawler/tests/test_mappings.py
git commit -m "feat: add crawler semantic mappings"
```

### Task 4: Add an example task configuration

**Files:**
- Create: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.example.json`

**Step 1: Write the failing test**

Add a test that loads the example JSON and validates every task using `validate_task()`.

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: FAIL because the example file does not exist yet.

**Step 3: Write minimal implementation**

Create the example JSON with a few representative tasks across armor and weapon categories.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 5: Commit**

```bash
git add crawler/tasks/wowhead_items.example.json crawler/tests/test_mappings.py
git commit -m "feat: add crawler example tasks"
```

### Task 5: Verify the slice end-to-end

**Files:**
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/pyproject.toml`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/core/mappings.py`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tasks/wowhead_items.example.json`
- Verify: `/Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler/tests/test_mappings.py`

**Step 1: Run the focused tests**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m pytest tests/test_mappings.py -q`

Expected: PASS

**Step 2: Run a broader test sweep**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: PASS

**Step 3: Review the example config**

Ensure each task only uses semantic strings and Chinese labels remain inside the mappings module.

**Step 4: Commit**

```bash
git add crawler docs/plans/2026-03-14-wowhead-crawler-design.md docs/plans/2026-03-14-wowhead-crawler-mappings.md
git commit -m "feat: add crawler mappings foundation"
```
