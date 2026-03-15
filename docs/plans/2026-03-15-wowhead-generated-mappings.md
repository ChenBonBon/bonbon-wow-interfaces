# Wowhead Generated Mappings Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate `crawler/core/mappings.py` directly from `normalized_mappings.json`, then migrate tests and task files to the new auto-generated key names.

**Architecture:** Add a generator that normalizes Wowhead labels into deterministic keys and rewrites the mapping dictionaries in `crawler/core/mappings.py`. Then update dependent task files, URL generation tests, and runner tests to use the new keys.

**Tech Stack:** Python 3, `json`, `re`, `unittest`

---

### Task 1: Add failing tests for label-to-key normalization

**Files:**
- Create: `crawler/tests/test_mappings_generator.py`

**Step 1: Write the failing test**

Add tests covering:
- `Main Hand -> main_hand`
- `Cloth Armor -> cloth_armor`
- `Miscellaneous (Weapons) -> miscellaneous_weapons`
- `Can be worn/equipped -> can_be_worn_equipped`

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings_generator -v`
Expected: FAIL because generator module does not exist yet.

**Step 3: Write minimal implementation**

Create `crawler/core/mappings_generator.py` with a `normalize_label_to_key()` helper.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings_generator -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add crawler/core/mappings_generator.py crawler/tests/test_mappings_generator.py
git commit -m "feat: add wowhead mapping key normalization"
```

### Task 2: Add failing tests for mappings code generation

**Files:**
- Modify: `crawler/tests/test_mappings_generator.py`

**Step 1: Write the failing test**

Add tests covering:
- generating `QUALITIES`
- generating `SLOTS`
- generating `CATEGORY_TYPES`
- generating `QUERY_FILTERS`
- generated code includes expected keys and values

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings_generator -v`
Expected: FAIL because generation helpers are missing.

**Step 3: Write minimal implementation**

Extend `crawler/core/mappings_generator.py` with:
- code generation helpers
- `render_mappings_module(normalized_data)`
- `write_mappings_module(output_path, normalized_data)`

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings_generator -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add crawler/core/mappings_generator.py crawler/tests/test_mappings_generator.py
git commit -m "feat: generate mappings module from wowhead data"
```

### Task 3: Add generator script and refresh mappings.py

**Files:**
- Create: `crawler/scripts/generate_mappings.py`
- Modify: `crawler/tests/test_scripts.py`
- Modify: `crawler/core/mappings.py`

**Step 1: Write the failing test**

Add tests covering:
- script reads `outputs/filter_pages/normalized_mappings.json`
- script rewrites `crawler/core/mappings.py`
- generated module can be imported and exposes expected dictionaries

**Step 2: Run test to verify it fails**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts -v`
Expected: FAIL because the new script does not exist yet.

**Step 3: Write minimal implementation**

Create `crawler/scripts/generate_mappings.py` and use it to regenerate `crawler/core/mappings.py`.

**Step 4: Run test to verify it passes**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_scripts -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add crawler/scripts/generate_mappings.py crawler/tests/test_scripts.py crawler/core/mappings.py
git commit -m "feat: generate crawler mappings from normalized wowhead data"
```

### Task 4: Migrate task files and dependent tests to new keys

**Files:**
- Modify: `crawler/tasks/wowhead_items.example.json`
- Modify: `crawler/tasks/wowhead_items.json`
- Modify: `crawler/tests/test_mappings.py`
- Modify: `crawler/tests/test_runner.py`
- Modify: `crawler/tests/test_url_builder.py`
- Modify: `crawler/tests/test_scripts.py`

**Step 1: Write the failing test**

Update tests to expect new keys, such as:
- `daggers`
- `cloth_armor`
- `staves`
- `can_be_worn_equipped`

**Step 2: Run tests to verify they fail for the right reason**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings tests.test_runner tests.test_url_builder tests.test_scripts -v`
Expected: FAIL because task files and fixtures still use old keys.

**Step 3: Write minimal implementation**

Migrate task files and fixtures to generated key names.

**Step 4: Run tests to verify they pass**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest tests.test_mappings tests.test_runner tests.test_url_builder tests.test_scripts -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add crawler/tasks/wowhead_items.example.json crawler/tasks/wowhead_items.json crawler/tests/test_mappings.py crawler/tests/test_runner.py crawler/tests/test_url_builder.py crawler/tests/test_scripts.py
git commit -m "refactor: migrate crawler tasks to generated wowhead keys"
```

### Task 5: Run full verification

**Files:**
- Verify only

**Step 1: Regenerate normalized mappings if needed**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m scripts.generate_normalized_mappings`
Expected: updates local `outputs/filter_pages/normalized_mappings.json`

**Step 2: Regenerate mappings.py**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m scripts.generate_mappings`
Expected: rewrites `crawler/core/mappings.py`

**Step 3: Run the full crawler test suite**

Run: `cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: all tests pass.

**Step 4: Commit**

```bash
git add crawler/core/mappings.py
git commit -m "chore: regenerate crawler mappings"
```
