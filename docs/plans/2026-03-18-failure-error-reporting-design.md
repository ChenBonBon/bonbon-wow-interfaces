# Failure Error Reporting Design

**Goal:** Persist per-task failure reasons so aborted or partially failed crawl runs can be diagnosed from files instead of only console output.

**Approach:** Store `error_message` on failed tasks directly in `manifest.json`, clear it on successful retries, and surface the same detail in `run-report.json` as structured `failed_tasks` entries. This keeps the error source of truth close to task state and lets existing reporting reuse manifest data without scraping console logs.

**Behavior:**
- On task failure, save `str(exception)` to `task["error_message"]`.
- On task success, remove any stale `error_message` field.
- `run-report.json` keeps `failed_task_ids` for compatibility and adds:
  - `failed_tasks: [{"task_id": ..., "error_message": ...}]`
- Consecutive-failure abort reports automatically include these detailed reasons because they are built from the current manifest state.
