# Wowhead Scripts 设计

**目标：** 为 crawler 增加一层很薄的脚本入口，方便手动执行和定时任务调用，同时保持 `core` 模块只负责核心逻辑。

## 设计原则

- `core.runner` 和 `core.fetcher` 继续保留核心职责
- 脚本层不承载业务逻辑
- 脚本层只负责读取参数并调用核心函数
- 通过 `python3 -m scripts.<name>` 调用，避免把逻辑散落到 shell 脚本

## 目录结构

```text
crawler/
  scripts/
    __init__.py
    generate_run.py
    fetch_run.py
```

## 脚本职责

### generate_run.py

负责：

- 接收任务文件路径
- 可选接收输出目录
- 调用 `core.runner.write_run_manifest()`
- 打印最终 `manifest.json` 路径

### fetch_run.py

负责：

- 接收 `manifest.json` 路径
- 调用 `core.fetcher.fetch_manifest_results()`
- 打印已处理的 manifest 路径

## 调用方式

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m scripts.generate_run tasks/wowhead_items.example.json
python3 -m scripts.fetch_run outputs/<run_id>/manifest.json
```

## 测试策略

优先测试脚本入口函数，而不是通过真实 subprocess：

- `generate_run` 能创建 manifest
- `fetch_run` 能消费 manifest 并写出结果文件
- 脚本只做转发，不重复核心逻辑测试
