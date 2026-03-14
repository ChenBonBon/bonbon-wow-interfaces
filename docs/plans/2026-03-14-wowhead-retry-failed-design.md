# Wowhead Failed Retry 设计

**目标：** 为单次运行增加一个专门的失败任务重跑入口，只重试 `manifest.json` 中 `status: failed` 的任务。

## 设计原则

- 不改变现有 `fetch_run` 的默认语义
- `fetch_run` 继续只处理 `planned`
- 失败任务重跑使用独立入口，语义清晰
- 核心逻辑尽量复用 `fetcher` 已有能力

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

## 测试策略

- 核心层验证只重跑 `failed`
- 成功时把 `failed` 改成 `fetched`
- 失败时保持 `failed`
- 不影响 `planned` 和 `fetched`
- 脚本入口实际可调用
