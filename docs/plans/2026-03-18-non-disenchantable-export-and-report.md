# Non-Disenchantable Export And Run Report Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the exported Lua artifact to reflect non-disenchantable data and add a run report script that writes per-run statistics to a JSON file.

**Architecture:** Keep the existing generate/fetch/aggregate/export flow, but rename the Lua output target and table symbol to non-disenchantable semantics. Add a separate reporting module and script that consumes `manifest.json` plus per-task result files to write a JSON report in the run directory.

**Tech Stack:** Python 3, unittest, shell wrappers, WoW Lua data file

---

### Task 1: Add failing tests for renamed Lua export and run reporting

**Files:**
- Modify: `crawler/tests/test_lua_exporter.py`
- Modify: `crawler/tests/test_scripts.py`
- Create: `crawler/tests/test_run_report.py`

**Step 1: Write failing tests**
- Expect the default Lua output path/name to become `NonDisenchantableByWowhead.lua`.
- Expect the rendered Lua table name to use non-disenchantable semantics.
- Add tests for a report writer that outputs JSON with task counts, unique item count, failed task ids, and empty-result task ids.
- Add script-level tests for a new report entry point.

**Step 2: Run focused tests to verify they fail**
Run: `cd crawler && python3 -m unittest tests.test_lua_exporter tests.test_scripts tests.test_run_report`
Expected: FAIL because the exporter still uses the old name and the report script does not exist yet.

### Task 2: Implement renamed export target and run report generator

**Files:**
- Modify: `crawler/core/lua_exporter.py`
- Modify: `crawler/scripts/export_lua.py`
- Create: `crawler/core/run_report.py`
- Create: `crawler/scripts/report_run.py`
- Create: `crawler/bin/report_run.sh`
- Modify: `QuickDisenchant/QuickDisenchant.toc`
- Rename: `QuickDisenchant/DisenchantableByWowhead.lua` -> `QuickDisenchant/NonDisenchantableByWowhead.lua`
- Modify: `crawler/README.md`

**Step 1: Write minimal implementation**
- Rename the default Lua output file.
- Rename the Lua global table to reflect non-disenchantable ids.
- Add a report generator that reads `manifest.json`, counts task states, counts unique items from `items.unique.json`, and lists fetched tasks with zero items.
- Make the report script write JSON to the run directory by default and print only the output path.
- Update the TOC and README references.

**Step 2: Run focused tests to verify they pass**
Run: `cd crawler && python3 -m unittest tests.test_lua_exporter tests.test_scripts tests.test_run_report`
Expected: PASS.

### Task 3: Run regression tests

**Files:**
- Verify only

**Step 1: Run full crawler tests**
Run: `cd crawler && python3 -m unittest discover -s tests -p 'test_*.py'`
Expected: PASS.

### Task 4: Commit

**Step 1: Commit after verification**
```bash
git add crawler/core/lua_exporter.py crawler/core/run_report.py crawler/scripts/export_lua.py crawler/scripts/report_run.py crawler/bin/report_run.sh crawler/tests/test_lua_exporter.py crawler/tests/test_scripts.py crawler/tests/test_run_report.py crawler/README.md QuickDisenchant/QuickDisenchant.toc QuickDisenchant/NonDisenchantableByWowhead.lua docs/plans/2026-03-18-non-disenchantable-export-and-report.md
git commit -m "feat: add non-disenchantable export report"
```
