# Wowhead Runner 设计

**目标：** 为爬虫增加一个“预执行”runner，用于读取任务配置、生成 URL 计划，并把结果写入单次运行目录中的 `manifest.json`。

## 范围

本阶段只做任务规划，不做真实抓取：

- 读取任务 JSON
- 过滤 `enabled: true` 的任务
- 归一化并校验任务
- 生成 `filter_path`、`path`、`query_string`、`url`
- 生成运行目录
- 写入 `manifest.json`

明确不做：

- HTTP 请求
- HTML 抓取
- 页面解析
- 重试与限速

## 模块设计

新增模块：

```text
crawler/core/runner.py
```

建议暴露三层接口：

1. `load_tasks(task_file_path)`
- 负责读取任务文件

2. `build_run_manifest(task_file_path, generated_at=None)`
- 负责把任务转换为 manifest 结构
- 不写文件，便于测试

3. `write_run_manifest(task_file_path, outputs_dir=None, generated_at=None)`
- 负责创建运行目录并写入 `manifest.json`

CLI 入口只做参数解析，然后调用 `write_run_manifest()`。

## 输出结构

输出目录按单次运行批次组织：

```text
crawler/outputs/<run_id>/manifest.json
```

其中：

- `run_id` 格式为 `YYYY-MM-DDTHH-MM-SS`
- `generated_at` 使用 ISO 8601，带时区

## Manifest 结构

```json
{
  "run_id": "2026-03-14T15-30-00",
  "generated_at": "2026-03-14T15:30:00+08:00",
  "task_file": "tasks/wowhead_items.example.json",
  "task_count": 3,
  "tasks": [
    {
      "task_id": "uncommon-head-cloth",
      "enabled": true,
      "status": "planned",
      "quality": "uncommon",
      "category": "armor",
      "slot": "head",
      "type": "cloth",
      "query_filters": {
        "available_to_players": "yes",
        "can_be_worn": "yes"
      },
      "filter_path": "quality:2/slot:1/type:1",
      "path": "items/armor/quality:2/slot:1/type:1",
      "query_string": "filter=161:195;1:1;0:0",
      "url": "https://www.wowhead.com/items/armor/quality:2/slot:1/type:1?filter=161:195;1:1;0:0"
    }
  ]
}
```

其中 `status` 固定为 `planned`，为后续真实抓取预留状态位。

## 命令行设计

第一版命令保持简单：

```bash
cd /Users/bonbon/Documents/Code/bonbon-wow-interfaces/crawler
python3 -m core.runner --task-file tasks/wowhead_items.example.json
```

第一版只支持：

- `--task-file`

输出目录默认写到：

```text
crawler/outputs/
```

## 测试策略

优先测试纯函数和文件输出：

- 能读取任务文件
- 只保留 `enabled: true` 的任务
- 生成的任务包含 URL 相关字段
- `task_count` 正确
- 会创建运行目录
- 会写出 `manifest.json`

测试中通过固定时间注入，避免时间相关断言不稳定。
