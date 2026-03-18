# Manifest 增量回写设计

## 背景

当前 `items.by-task.json` 已经支持在抓取过程中实时更新，但 `manifest.json` 仍然只会在抓取阶段结束后统一回写。用户在运行 `run_all.sh` 时虽然能看到控制台日志，却无法通过 `manifest.json` 实时观察任务状态变化。

## 目标

让 `manifest.json` 在抓取过程中也实时反映任务状态：

- 某个任务成功时，立刻更新为 `fetched`
- 某个任务失败时，立刻更新为 `failed` 并附带 `error_message`
- 尚未处理的任务保持 `planned`

这样用户在运行过程中就可以直接打开 `manifest.json` 查看最新进度。

## 方案

沿用 `items.by-task.json` 的增量写入思路，在每个任务完成后立即执行两步：

1. 刷新 `items.by-task.json`
2. 刷新 `manifest.json`

写入顺序保持为：先结果文件，再 manifest。这样当用户同时查看两个文件时，`manifest` 中显示某任务已完成时，对应结果也已经落盘。

## 边界

- 失败任务不写入 `items.by-task.json`
- 熔断时也保留当前已写入的 `manifest.json` 和 `items.by-task.json`
- 不改变现有聚合、统计、导出逻辑，只调整写入时机

## 验证

新增回归测试，验证在第二个任务仍未完成时：

- `manifest.json` 已经存在最新状态
- 第一个任务状态为 `fetched`
- 第二个任务状态仍为 `planned`
