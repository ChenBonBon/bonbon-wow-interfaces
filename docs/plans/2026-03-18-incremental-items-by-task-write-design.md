# Incremental `items.by-task.json` Write Design

**Goal:** Make the run-scoped result file visible and continuously updated while `run_all` is still in progress.

**Approach:** Keep `items.by-task.json` as the single result file, but flush it after every task completion instead of only at the end of the fetch phase. Because task completions are already processed in the main thread, we can update the in-memory result map and write the file immediately without introducing extra locking around file IO.

**Behavior:**
- On each successful task completion, write the updated `items.by-task.json` immediately.
- On each failed task completion, remove any stale entry for that task and rewrite the file immediately.
- The file should exist during a long-running crawl as soon as the first successful task finishes.
- If no task has succeeded yet, the file may still be absent.
