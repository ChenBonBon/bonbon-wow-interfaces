# run-report 原子写入实现计划

1. 在 `crawler/tests/test_run_report.py` 新增失败测试，验证 `write_run_report()` 通过 `Path.replace()` 落盘。
2. 在 `crawler/core/run_report.py` 中新增 `_atomic_write_text()`。
3. 将 `write_run_report()` 改为通过 `_atomic_write_text()` 写出 `run-report.json`。
4. 跑定向测试、`tests.test_run_report` 和全量 `unittest discover`，确认无回归。
