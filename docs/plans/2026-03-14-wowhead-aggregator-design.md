# Wowhead Aggregator 设计

**目标：** 为单次抓取结果增加一个极简汇总器，按 `itemId` 去重，输出唯一物品列表。

## 范围

输入：

- `crawler/outputs/<run_id>/manifest.json`
- 同目录下各个 `fetched` 任务的 `<task_id>.json`

输出：

- `crawler/outputs/<run_id>/items.unique.json`

第一版只做：

- 读取 manifest
- 只处理 `status: fetched` 的任务
- 读取每个任务结果文件中的 `items`
- 按 `itemId` 去重
- 保留每个 `itemId` 的第一条 `{itemId, name}`
- 写出唯一物品列表

明确不做：

- 保留分类上下文
- 冲突对账
- 多视图输出

## 输出格式

```json
[
  {
    "itemId": 2620,
    "name": "Augural Shroud"
  },
  {
    "itemId": 2621,
    "name": "Cowl of Necromancy"
  }
]
```

## 去重规则

- 唯一键：`itemId`
- 如果同一个 `itemId` 出现多次：
  - 只保留第一次出现的记录
  - 后续重复项跳过

这样生成的总表最适合插件做“是否命中可分解物品集合”的判断。

## 模块设计

新增：

```text
crawler/core/aggregator.py
```

建议接口：

1. `build_unique_items(manifest_path)`
- 返回唯一 item 列表

2. `write_unique_items(manifest_path)`
- 写出 `items.unique.json`

## 脚本入口

同时增加薄脚本：

```text
crawler/scripts/aggregate_run.py
```

调用方式：

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m scripts.aggregate_run outputs/<run_id>/manifest.json
```

## 测试策略

- 只汇总 `fetched` 任务
- 同一个 `itemId` 只保留一条
- 写出 `items.unique.json`
- 脚本入口能调用成功
