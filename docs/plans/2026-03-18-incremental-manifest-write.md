# Manifest 增量回写实现计划

1. 在 `crawler/tests/test_fetcher.py` 新增失败测试，覆盖运行中途 `manifest.json` 的状态可见性。
2. 在 `crawler/core/fetcher.py` 中将 `manifest.json` 回写从“抓取结束后统一执行”改为“每个任务完成后立即执行”。
3. 跑定向测试，确认新增测试从红转绿。
4. 跑 `tests.test_fetcher` 和全量 `unittest discover`，确认没有回归。
