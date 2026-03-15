# Wowhead Normalized Mappings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a normalizer that reads local Wowhead armor/weapon HTML + Filter.init JSON and writes a stable `normalized_mappings.json` intermediate artifact.

**Architecture:** Add a small core module that extracts `<select>` options from saved HTML and target query filters from saved JSON, then expose a script entrypoint to generate one normalized output file. Keep semantic keys in `crawler/core/mappings.py` untouched for now.

**Tech Stack:** Python 3, `json`, `html.parser`, `unittest`

---

### Task 1: Add failing tests for HTML select extraction

**Files:**
- Create: `crawler/tests/test_normalized_mappings.py`
- Modify: `crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Add tests covering:
- extracting `quality` options from saved HTML
- extracting `slot` options from saved HTML
- extracting `type` options from saved HTML

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_normalized_mappings -v`
Expected: FAIL because `crawler.core.normalized_mappings` does not exist yet.

**Step 3: Write minimal implementation**

Create `crawler/core/normalized_mappings.py` with:
- `extract_select_options(html_text, select_id)`

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_normalized_mappings -v`
Expected: PASS for select extraction tests.

**Step 5: Commit**

```bash
git add crawler/core/normalized_mappings.py crawler/tests/test_normalized_mappings.py
git commit -m "feat: add wowhead select option extraction"
```

### Task 2: Add failing tests for query filter extraction and normalized output

**Files:**
- Modify: `crawler/tests/test_normalized_mappings.py`

**Step 1: Write the failing test**

Add tests covering:
- extracting ids `8`, `161`, `195`
- rejecting inconsistent query filter definitions
- building combined normalized mappings with stable ordering

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_normalized_mappings -v`
Expected: FAIL because builder functions are missing.

**Step 3: Write minimal implementation**

Extend `crawler/core/normalized_mappings.py` with:
- `extract_query_filters(filter_init_data)`
- `build_normalized_mappings(...)`
- `write_normalized_mappings(output_path, mappings)`

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_normalized_mappings -v`
Expected: PASS for normalized output tests.

**Step 5: Commit**

```bash
git add crawler/core/normalized_mappings.py crawler/tests/test_normalized_mappings.py
git commit -m "feat: build normalized wowhead mappings"
```

### Task 3: Add script entrypoint and wrapper coverage

**Files:**
- Create: `crawler/scripts/generate_normalized_mappings.py`
- Modify: `crawler/tests/test_scripts.py`
- Modify: `docs/plans/2026-03-15-wowhead-normalized-mappings-design.md`

**Step 1: Write the failing test**

Add tests covering:
- script reads the four local input files
- script writes `outputs/filter_pages/normalized_mappings.json`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_scripts -v`
Expected: FAIL because the new script does not exist yet.

**Step 3: Write minimal implementation**

Create `crawler/scripts/generate_normalized_mappings.py` that:
- loads `armor.html`, `armor.filters.json`, `weapons.html`, `weapons.filters.json`
- builds normalized mappings
- writes `normalized_mappings.json`

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest crawler.tests.test_scripts -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add crawler/scripts/generate_normalized_mappings.py crawler/tests/test_scripts.py docs/plans/2026-03-15-wowhead-normalized-mappings-design.md docs/plans/2026-03-15-wowhead-normalized-mappings.md
git commit -m "feat: add normalized mappings generator"
```

### Task 4: Run full verification

**Files:**
- Verify only

**Step 1: Run the complete test suite**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: all tests pass.

**Step 2: Run the real generator against local saved files**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m scripts.generate_normalized_mappings`
Expected: writes `crawler/outputs/filter_pages/normalized_mappings.json`

**Step 3: Inspect generated output**

Check that the JSON contains:
- `categories`
- `qualities`
- `slots`
- `types`
- `query_filters`

**Step 4: Commit**

```bash
git add crawler/outputs/filter_pages/normalized_mappings.json
git commit -m "chore: generate normalized wowhead mappings"
```
