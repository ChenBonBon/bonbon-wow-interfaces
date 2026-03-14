# Wowhead 爬虫设计

**目标：** 在 `crawler/` 下搭建一个可扩展的 Wowhead 抓取框架，优先保证配置可读、维护成本低，并支持后续并发执行与失败重跑。

## 核心原则

- 采用“通用爬虫 + 任务配置”的方案，不为每个筛选组合创建独立脚本。
- 任务配置全部使用语义化字符串，不直接暴露 Wowhead 的数字参数。
- 站点参数映射集中放在映射模块中，便于后续调整抓取规则。
- 第一阶段先实现映射层、任务配置样例和测试，不急着写完整抓取逻辑。

## 目录设计

```text
crawler/
  bin/
    run_all.sh
    retry_failed.sh
  pyproject.toml
  core/
    __init__.py
    aggregator.py
    fetcher.py
    lua_exporter.py
    mappings.py
    runner.py
    url_builder.py
  outputs/
    <run_id>/
      manifest.json
      <task_id>.json
      items.unique.json
  scripts/
    __init__.py
    aggregate_run.py
    export_lua.py
    generate_run.py
    fetch_run.py
    run_all.py
    retry_failed_run.py
  tasks/
    wowhead_items.example.json
  tests/
    test_aggregator.py
    test_fetcher.py
    test_mappings.py
    test_runner.py
    test_url_builder.py
```

当前阶段先实现 `mappings.py`、`url_builder.py`、`runner.py` 和 `fetcher.py`，更完整的抓取增强能力在后续阶段补齐。

## 任务配置格式

任务配置统一使用语义化字段：

```json
{
  "task_id": "uncommon-head-cloth",
  "enabled": true,
  "quality": "uncommon",
  "category": "armor",
  "slot": "head",
  "type": "cloth"
}
```

字段约束如下：

- `task_id`：字符串，任务唯一标识
- `enabled`：布尔值，控制任务是否参与执行
- `quality`：`uncommon` / `rare` / `epic`
- `category`：`weapon` / `armor`
- `slot`：语义化部位名，例如 `head`
- `type`：对应 `category` 下的具体类型，例如 `cloth` 或 `dagger`
- `query_filters`：可选对象，使用语义化查询筛选，例如 `available_to_players: "yes"`

示例：

```json
{
  "task_id": "uncommon-head-cloth",
  "enabled": true,
  "quality": "uncommon",
  "category": "armor",
  "slot": "head",
  "type": "cloth",
  "query_filters": {
    "available_to_players": "yes",
    "can_be_worn": "yes"
  }
}
```

## 映射模块设计

`crawler/core/mappings.py` 负责两层内容：

1. 语义层常量
- `QUALITIES`
- `CATEGORIES`
- `SLOTS`
- `CATEGORY_TYPES`
- `QUERY_FILTERS`

每个可参与站点筛选的语义项都包含：

- `label`：中文展示名称
- `wowhead.path`：仅 `category` 使用，对应 Wowhead 的路径段，例如 `weapons`
- `wowhead.facet`：对应 Wowhead 的筛选字段名，例如 `quality`
- `wowhead.value`：对应 Wowhead 的筛选值，例如 `2`

`QUERY_FILTERS` 采用三态语义值：

- `yes`
- `no`
- `any`

其中 `any` 或字段未填写时，不参与 URL 的查询参数拼接。

2. 纯函数接口
- `validate_task(task)`
- `normalize_task(task)`
- `build_task_slug(task)`
- `describe_task(task)`
- `get_category_type_meta(category, type_name)`

`crawler/core/url_builder.py` 负责把任务转换为：

- `filter_path`：例如 `quality:2/slot:1/type:1`
- `path`：例如 `items/armor/quality:2/slot:1/type:1`
- `query_string`：例如 `filter=161:195;1:1;0:0`
- `url`：例如 `https://www.wowhead.com/items/armor/quality:2/slot:1/type:1`

URL 生成规则固定为：

- `category` 决定 `items/{category_path}`
- `quality`、`slot`、`type` 按固定顺序拼接为筛选段
- `query_filters` 按固定顺序生成 `filter=` 查询参数
- 如果存在 `query_string`，最终 URL 形如 `path?query_string`

`crawler/core/runner.py` 负责：

- 读取任务文件
- 过滤 `enabled: true`
- 生成单次运行清单
- 写入 `outputs/<run_id>/manifest.json`

manifest 中每个任务当前固定使用：

- `status: "planned"`

`crawler/core/fetcher.py` 负责：

- 读取 `manifest.json`
- 抓取 `status: "planned"` 的任务页面
- 从页面中的 `listviewitems` 提取 item 数据
- 写入每任务一个结果文件
- 把任务状态更新为：
  - `planned`
  - `fetched`
  - `failed`

推荐执行入口为脚本层：

- `./bin/run_all.sh`
- `./bin/retry_failed.sh`
- `python3 -m scripts.aggregate_run`
- `python3 -m scripts.export_lua`
- `python3 -m scripts.generate_run`
- `python3 -m scripts.fetch_run`
- `python3 -m scripts.run_all`
- `python3 -m scripts.retry_failed_run`

脚本层只负责参数转发，不承载业务逻辑。

其中 `crawler/bin/` 下的 shell wrapper 只负责：

- 切换到 `crawler/` 目录
- 调用对应的 Python 脚本入口
- 透传原始命令行参数

其中 `./bin/run_all.sh` 额外提供：

- 无参数时默认使用 `tasks/wowhead_items.json`
- 显式传参时优先使用你提供的任务文件与输出目录

其中：

- `fetch_run` 只处理 `planned`
- `run_all` 默认执行 `generate -> fetch -> aggregate -> export`
- `retry_failed_run` 先处理 `failed`，再执行全量 `aggregate -> export`

`crawler/core/aggregator.py` 负责：

- 读取 `manifest.json`
- 只汇总 `status: "fetched"` 的任务结果
- 按 `itemId` 去重
- 写出极简唯一物品表 `items.unique.json`

`items.unique.json` 的结构为：

```json
[
  {
    "itemId": 2620,
    "name": "Augural Shroud"
  }
]
```

`crawler/core/lua_exporter.py` 负责：

- 读取 `manifest.json`
- 校验所有任务都已 `fetched`
- 再读取同目录下的 `items.unique.json`
- 导出为插件可直接加载的 Lua 数据文件

目标文件为：

- `QuickDisenchant/DisenchantableByWowhead.lua`

## 中文标签规范

所有 `label` 统一改为中文，便于后续日志、调试和结果展示复用。例如：

- `uncommon` -> `绿色`
- `weapon` -> `武器`
- `dagger` -> `匕首`
- `cloth` -> `布甲`
- `head` -> `头部`

## 输出与执行策略

后续抓取阶段将按“单次运行批次”输出：

```text
crawler/
  outputs/
    2026-03-14T10-30-00/
      manifest.json
      uncommon-head-cloth.json
```

每个任务结果文件第一版结构为：

```json
{
  "task_id": "uncommon-head-cloth",
  "url": "https://www.wowhead.com/...",
  "items": [
    {
      "itemId": 2620,
      "name": "Augural Shroud"
    }
  ]
}
```

失败处理先采用任务级重试：

- 每个任务重试 3 次
- 使用简单退避
- 支持后续按 `manifest.json` 只重跑失败任务

## 第一阶段实现范围

本次实现只覆盖：

- `crawler` 最小 Python 工程骨架
- 映射模块
- URL 生成模块
- 任务预执行 runner
- manifest 驱动 fetcher
- 极简唯一物品汇总器
- Lua 数据导出器
- 薄脚本入口
- 样例任务配置文件
- 针对映射模块、URL 生成器、runner、fetcher、汇总器和脚本层的 `unittest` 测试

抓取器、解析器和调度增强能力留到下一阶段。
