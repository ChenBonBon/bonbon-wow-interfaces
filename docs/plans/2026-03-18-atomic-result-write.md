# 原子写入实现计划

1. 在 `crawler/tests/test_fetcher.py` 新增失败测试，验证 `manifest.json` 和 `items.by-task.json` 的写入会调用 `Path.replace()`。
2. 在 `crawler/core/fetcher.py` 中新增 `_atomic_write_text()` helper。
3. 将 `_write_manifest()` 和 `_write_items_by_task()` 改成通过 `_atomic_write_text()` 落盘。
4. 跑定向测试、`tests.test_fetcher` 和全量 `unittest discover`，确认无回归。
