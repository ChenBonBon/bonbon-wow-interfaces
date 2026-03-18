# Single Run Result File Design

**Goal:** Replace per-task result JSON files with a single run-scoped result file while preserving task-level item data.

**Approach:** Store all fetched task results in one `items.by-task.json` file inside the run directory. Each task keeps its own item list under its `task_id`, so reporting and aggregation can still answer task-level questions without generating thousands of small files.

**Behavior:**
- Remove creation of `<task_id>.json` result files.
- Write all fetched results to `outputs/<run_id>/items.by-task.json`.
- Keep `items.unique.json` and `run-report.json` as derived outputs.
- `run_report` uses `items.by-task.json` to detect empty fetched tasks.
- `aggregator` uses `items.by-task.json` to build `items.unique.json`.

**Why this shape:** It cuts filesystem noise dramatically while keeping the current task-based reporting model intact.
