# Wowhead Failed Retry 设计

**目标：** 为单次运行增加一个专门的失败任务重跑入口，重试 `manifest.json` 中 `status: failed` 的任务后继续完成聚合与导出。

## 设计原则

- 不改变现有 `fetch_run` 的默认语义
- `fetch_run` 继续只处理 `planned`
- 失败任务重跑使用独立入口，语义清晰
- 核心逻辑尽量复用 `fetcher` 已有能力
- 重跑后的 `aggregate` 和 `export` 必须面向整个 run，而不是只看失败子集

## 核心设计

在 `crawler/core/fetcher.py` 中抽取一个内部执行函数，支持传入“允许处理的状态集合”。

在此基础上保留并新增：

- `fetch_manifest_results(manifest_path, fetch_url=None)`
  - 只处理 `planned`
- `retry_failed_manifest_results(manifest_path, fetch_url=None)`
  - 只处理 `failed`

## 状态流转

重跑逻辑只关注：

- `failed` -> `fetched`
- `failed` -> `failed`

不会改动：

- `planned`
- `fetched`

后续编排：

- retry fetch 之后，继续执行全量 `aggregate`
- 最后执行全量 `export`
- 如果 manifest 里仍然存在 `planned` 或 `failed`，导出阶段会抛异常终止

## 脚本入口

新增：

```text
crawler/scripts/retry_failed_run.py
```

调用方式：

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m scripts.retry_failed_run outputs/<run_id>/manifest.json
```

执行顺序：

1. 仅重跑 `failed`
2. 对整个 run 重新聚合 `items.unique.json`
3. 对整个 run 重新尝试 Lua 导出

## 测试策略

- 核心层验证只重跑 `failed`
- 成功时把 `failed` 改成 `fetched`
- 失败时保持 `failed`
- 不影响 `planned` 和 `fetched`
- 脚本入口实际可调用
- 仍有 `planned` 时会在导出阶段失败
- 全部转为 `fetched` 时会成功导出 Lua
