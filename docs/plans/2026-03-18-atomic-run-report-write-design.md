# run-report 原子写入设计

## 背景

抓取运行过程中我们已经将以下文件改为原子写入：

- `manifest.json`
- `items.by-task.json`

但 `run-report.json` 仍然是直接覆盖写。这样在熔断或手动执行 `report_run.sh` 时，仍然可能出现中途读到半截 JSON 的风险。

## 目标

让 `run-report.json` 也采用与其他运行产物一致的写入策略：

- 先写临时文件
- 再通过 `replace()` 原子替换目标文件

## 方案

在 `crawler/core/run_report.py` 中新增本地 helper：

- `_atomic_write_text(file_path, content)`

并让 `write_run_report()` 统一通过该 helper 落盘。

## 设计考虑

这里不抽公共 util，保持改动面小：

- `fetcher.py` 和 `run_report.py` 各自维护同样的小型 helper
- 先完成行为一致性
- 如果后续还有更多运行产物需要原子写入，再统一抽公共模块

## 验证

新增测试，确认 `write_run_report()` 会调用 `Path.replace()`，并且最终输出文件内容正确。
