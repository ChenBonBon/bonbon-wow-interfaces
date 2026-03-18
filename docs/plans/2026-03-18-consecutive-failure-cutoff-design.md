# Consecutive Failure Cutoff Design

**Goal:** Stop a crawl early when the fetch pipeline hits 10 consecutive failed task completions, then persist a machine-readable run summary before exiting.

**Approach:** Implement the cutoff inside `crawler/core/fetcher.py` so every existing fetch entrypoint (`fetch_run`, `run_all`, `retry_failed_run`) shares the same protection. Keep the threshold fixed at 10, count failures in completion order, reset the streak on any successful task, and stop scheduling new tasks once the threshold is reached.

**Behavior:**
- Emit a timestamped `ABORT` log when the streak reaches the limit.
- Persist the partially updated `manifest.json` before exiting.
- Write `run-report.json` immediately from the current manifest state.
- Add explicit report fields:
  - `aborted_due_to_consecutive_failures`
  - `consecutive_failure_limit`
- Raise an exception so the outer script terminates and does not continue to aggregate/export.

**Tradeoff:** Because fetches run with concurrency `3`, at most a few already-started tasks may still finish after the streak threshold is hit if we allow in-flight work to drain cleanly. To make the cutoff deterministic and easy to report, the fetch loop should stop scheduling new tasks and then exit after the currently submitted tasks are resolved.
