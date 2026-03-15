# Wowhead Normalized Mappings 设计

**目标：** 从本地保存的 Wowhead `armor/weapons` HTML 与 `Filter.init` JSON 中提取稳定的中间层数据，生成 `normalized_mappings.json`，为后续更新 `crawler/core/mappings.py` 提供可靠输入。

## 背景

我们已经确认：

- `query_filters` 的定义来自 `*.filters.json` 中的 `filters`
- `quality`、`slot`、`type` 的候选值并不完整地保存在 `Filter.init` JSON 中
- 页面 HTML 的 `<select id="filter-facet-quality|slot|type">` 才包含当前页面真实可选项与对应 value

因此，中间层不能只依赖 `Filter.init` JSON，而是要组合两种原始来源：

- `armor.html` / `weapons.html`
- `armor.filters.json` / `weapons.filters.json`

## 设计原则

- 不直接覆盖 `crawler/core/mappings.py`
- 先生成稳定、可复查的 `normalized_mappings.json`
- 原始抓取结果与归一化结果分层存放
- 只提取当前确定可靠的数据，不强行自动化所有语义命名

## 数据来源与提取规则

### 1. qualities

来源：HTML 中 `#filter-facet-quality` 的 `<option>` 列表。

规则：
- 读取 `value` 和可见文本
- 只保留映射层当前关心的品质：
  - `2 -> Uncommon`
  - `3 -> Rare`
  - `4 -> Epic`
- 中间层保存原始英文标签和值，不在这一步引入中文标签

### 2. slots

来源：HTML 中 `#filter-facet-slot` 的 `<option>` 列表。

规则：
- 分别从 `armor.html` 与 `weapons.html` 提取
- 合并为一个去重列表
- 以 `value` 为唯一键
- 保留原始英文标签和值
- 不在这一步决定最终语义 key，例如 `main_hand`、`off_hand`

### 3. types

来源：HTML 中 `#filter-facet-type` 的 `<option>` 列表。

规则：
- 从 `armor.html` 提取 `armor` 类型集合
- 从 `weapons.html` 提取 `weapon` 类型集合
- 以 `value` 为唯一键
- 保留原始英文标签和值
- 按 category 分组输出

### 4. query_filters

来源：`*.filters.json` 的 `filters` 列表。

第一版只提取当前已经确认使用的筛选器：

- `Disenchantable` -> `id: 8`
- `Available to players` -> `id: 161`
- `Can be worn/equipped` -> `id: 195`

规则：
- 保留原始英文名称与 filter id
- 同时提取其可用取值，例如 `Yes/No`
- 若 `armor` 与 `weapons` 两份 JSON 中结果不一致，直接报错

## normalized_mappings.json 结构

```json
{
  "categories": {
    "armor": {"path": "armor"},
    "weapon": {"path": "weapons"}
  },
  "qualities": [
    {"value": 2, "label": "Uncommon"},
    {"value": 3, "label": "Rare"},
    {"value": 4, "label": "Epic"}
  ],
  "slots": [
    {"value": 1, "label": "Head"},
    {"value": 21, "label": "Main Hand"}
  ],
  "types": {
    "armor": [
      {"value": 1, "label": "Cloth Armor"}
    ],
    "weapon": [
      {"value": 15, "label": "Daggers"}
    ]
  },
  "query_filters": [
    {
      "id": 8,
      "label": "Disenchantable",
      "values": [
        {"value": 1, "label": "Yes"},
        {"value": 2, "label": "No"}
      ]
    }
  ]
}
```

## 模块设计

新增模块建议：

```text
crawler/core/normalized_mappings.py
crawler/scripts/generate_normalized_mappings.py
```

核心接口：

1. `extract_select_options(html_text, select_id)`
- 从 HTML 提取指定 `<select>` 下的所有 `<option>`

2. `extract_query_filters(filter_init_data)`
- 从 `filters` 中提取目标 query filters

3. `build_normalized_mappings(armor_html, armor_filters, weapons_html, weapons_filters)`
- 组合生成完整 normalized 结构

4. `write_normalized_mappings(output_path, mappings)`
- 写出 JSON 文件

## 输出位置

默认输出：

- `crawler/outputs/filter_pages/normalized_mappings.json`

## 错误处理

第一版直接报错的场景：

- HTML 中缺少 `quality` / `slot` / `type` 的 `<select>`
- `Filter.init` JSON 缺少目标 query filter
- `armor` 与 `weapons` 中同一 query filter 定义不一致
- `<option>` 无法提取到 `value` 或文本

## 非目标

第一版明确不做：

- 直接生成或覆盖 `crawler/core/mappings.py`
- 自动决定我们自己的语义 key，如 `main_hand`、`dagger`
- 自动生成中文标签
- 自动处理所有 Wowhead filter，只处理当前确定使用的子集

## 测试策略

优先覆盖：

- 能从样例 HTML 提取 `quality` / `slot` / `type` 选项
- 能从 `filters.json` 提取目标 query filters
- 能合并 armor + weapons 结果并去重
- 输出 JSON 结构稳定、排序稳定
- 输入不一致时会报错
