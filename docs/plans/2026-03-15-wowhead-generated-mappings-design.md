# Wowhead Generated Mappings 设计

**目标：** 不再手工维护 `crawler/core/mappings.py` 中的大部分语义 key，而是以 Wowhead 页面实际提供的 label/value 为单一数据源，基于 `normalized_mappings.json` 自动生成映射定义。

## 设计结论

本次采用：**直接用 normalized label 生成 key**。

也就是说：

- `Main Hand` 会生成 `main_hand`
- `Cloth Armor` 会生成 `cloth_armor`
- `Daggers` 会生成 `daggers`
- `Available to players` 会生成 `available_to_players`

后续我们的代码和任务文件都以这些自动生成的 key 为准，不再优先维持旧的手工命名。

## 为什么这样做

旧方案的问题是：

- 语义 key 由我们手工命名，容易带入主观判断
- 新增或变更 Wowhead 选项时，需要人工做别名映射
- `mappings.py` 和实际页面定义可能逐渐漂移

新方案的好处是：

- Wowhead label/value 是唯一真源
- 同步逻辑更简单
- 遇到新字段时，自动生成即可，不需要先发明命名
- 数据更新更适合脚本化和定时同步

## 影响范围

这个变化不会只影响 `mappings.py`，还会影响所有引用这些 key 的代码。

### 1. `crawler/core/mappings.py`

将改为“生成产物”思路：

- `QUALITIES`
- `SLOTS`
- `CATEGORY_TYPES`
- `QUERY_FILTERS`

主要从 `normalized_mappings.json` 自动生成。

保留手工维护的部分：

- `QUERY_FILTER_VALUE_MAP`
- `CATEGORIES`
- `QUERY_FILTER_ORDER`
- 与 task 校验、slug、描述相关的辅助函数

### 2. 任务文件

现有任务文件中的 key 需要迁移为新命名。

例如：

- `type: dagger` -> `type: daggers`
- `type: cloth` -> `type: cloth_armor`
- `type: staff` -> `type: staves`
- `type: miscellaneous_weapon` -> `type: miscellaneous_weapons`

slot 也可能受影响，例如：

- `cloak` 仍可能改成 `back`
- `finger` 会更接近 `finger`
- `off_hand` 与 `held_in_off_hand` 将变成两个不同 key

### 3. URL 生成与校验逻辑

`url_builder.py` 的核心结构不变。

变化点在于：

- 它读取的 key 会变成新生成的 key
- 对应的 `facet/value` 仍然来自 `mappings.py`

### 4. 测试

所有断言旧 key 的测试都需要同步迁移。

## key 生成规则

为了保证生成稳定、可预测，key 规则固定如下：

1. 取 normalized label 的英文文本
2. 转小写
3. 去掉括号内容外层标点
4. 将空格和连字符统一转为下划线
5. 去掉 `/`、`,` 等分隔符，改为下划线
6. 连续下划线压缩为单个 `_`
7. 去掉首尾 `_`

示例：

- `Main Hand` -> `main_hand`
- `Two-Hand` -> `two_hand`
- `Cloth Armor` -> `cloth_armor`
- `Miscellaneous (Weapons)` -> `miscellaneous_weapons`
- `Can be worn/equipped` -> `can_be_worn_equipped`
- `Available to players` -> `available_to_players`
- `Held In Off-hand` -> `held_in_off_hand`

## 兼容策略

第一版不保留旧 key 兼容层。

也就是说：

- 不在 `mappings.py` 中同时保留 `dagger` 和 `daggers`
- 不做运行时 alias fallback
- 直接迁移任务文件和测试到新 key

这样可以避免长期双轨维护。

## 生成策略

建议新增一个生成器模块，例如：

```text
crawler/core/mappings_generator.py
crawler/scripts/generate_mappings.py
```

输入：

- `crawler/outputs/filter_pages/normalized_mappings.json`

输出：

- 刷新 `crawler/core/mappings.py`

### 生成内容

#### `QUALITIES`

从 `normalized_mappings.json["qualities"]` 生成。

中文 label 仍然手工映射：

- `Uncommon` -> `绿色`
- `Rare` -> `蓝色`
- `Epic` -> `紫色`

#### `SLOTS`

从 `normalized_mappings.json["slots"]` 生成。

中文 label 可以先沿用英文 label，或通过一个小型翻译表转中文。

#### `CATEGORY_TYPES`

从：

- `normalized_mappings.json["types"]["armor"]`
- `normalized_mappings.json["types"]["weapon"]`

生成。

#### `QUERY_FILTERS`

从 `normalized_mappings.json["query_filters"]` 生成 key 和 `wowhead.id`。

值映射仍然继续使用：

- `Yes -> yes -> 1`
- `No -> no -> 2`
- `Any` 仍由任务层表示为未设置/`any`

## 非目标

第一版明确不做：

- 自动迁移历史 run 输出文件
- 为旧 key 提供兼容 alias
- 自动翻译所有英文 label 到完美中文
- 修改 QuickDisenchant 插件逻辑

## 风险

### 1. 命名变化较大

现有任务文件和测试会出现较大变更。

### 2. 个别 label 可能不适合作为最终业务命名

例如：

- `Can be worn/equipped`
- `Miscellaneous (Weapons)`
- `Held In Off-hand`

但这是当前方案的有意选择：优先忠实反映 Wowhead 原始定义，而不是人工润色。

### 3. 中英文 label 混用

如果我们保留中文展示，仍需要一个小型翻译表。这层是展示问题，不影响 key 和 wowhead value。

## 测试策略

至少覆盖：

- label 到 key 的规范化规则
- 从 `normalized_mappings.json` 生成稳定的 mappings 代码
- 重新加载生成后的 `mappings.py` 并验证：
  - `QUALITIES`
  - `SLOTS`
  - `CATEGORY_TYPES`
  - `QUERY_FILTERS`
- 更新任务文件后，`runner/url_builder` 仍能通过测试
