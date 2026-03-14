# Wowhead Run-All 设计

**目标：** 增加一个总入口脚本，默认串联执行 `generate -> fetch -> aggregate -> export` 四步。

## 设计原则

- 总入口脚本只做编排，不承载业务逻辑
- 继续复用现有脚本层：
  - `generate_run`
  - `fetch_run`
  - `aggregate_run`
  - `export_lua`
- `retry_failed_run` 仍保持独立，不进入默认流程

## 执行流程

输入：

- 任务文件路径

执行顺序：

1. 生成运行清单
2. 抓取 `planned` 任务
3. 聚合唯一 `itemId`
4. 导出 Lua 数据文件

输出：

- `outputs/<run_id>/manifest.json`
- `outputs/<run_id>/<task_id>.json`
- `outputs/<run_id>/items.unique.json`
- `QuickDisenchant/DisenchantableByWowhead.lua` 或显式传入的输出路径

## 脚本入口

新增：

```text
crawler/scripts/run_all.py
```

调用方式：

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m scripts.run_all tasks/wowhead_items.example.json
```

## 返回值

脚本内部 `run()` 建议返回本次运行的 `manifest.json` 路径，便于后续工具链继续串联。

## 测试策略

- 端到端验证四步都被执行
- 最终能看到：
  - manifest 文件
  - 抓取结果文件
  - `items.unique.json`
  - Lua 导出文件
