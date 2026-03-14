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
  pyproject.toml
  core/
    __init__.py
    mappings.py
  tasks/
    wowhead_items.example.json
  tests/
    test_mappings.py
```

第一阶段只实现 `mappings.py`，其余抓取、解析、输出模块在后续阶段补齐。

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

## 映射模块设计

`crawler/core/mappings.py` 负责两层内容：

1. 语义层常量
- `QUALITIES`
- `CATEGORIES`
- `SLOTS`
- `CATEGORY_TYPES`

每个可参与站点筛选的语义项都包含：

- `label`：中文展示名称
- `wowhead.facet`：对应 Wowhead 的筛选字段名，例如 `quality`
- `wowhead.value`：对应 Wowhead 的筛选值，例如 `2`

2. 纯函数接口
- `validate_task(task)`
- `normalize_task(task)`
- `build_task_slug(task)`
- `describe_task(task)`
- `get_category_type_meta(category, type_name)`

模块暂时不绑定具体 Wowhead URL 规则，先把语义层稳定下来。

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

失败处理先采用任务级重试：

- 每个任务重试 3 次
- 使用简单退避
- 支持后续按 `manifest.json` 只重跑失败任务

## 第一阶段实现范围

本次实现只覆盖：

- `crawler` 最小 Python 工程骨架
- 映射模块
- 样例任务配置文件
- 针对映射模块的 `unittest` 测试

抓取器、URL 生成器、调度器和输出写入模块留到下一阶段。
