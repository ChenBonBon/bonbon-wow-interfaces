# QuickDisenchant Wowhead 不可分解黑名单过滤设计

## 背景

QuickDisenchant 当前扫描背包时，主要依赖游戏内静态规则判断候选：

- 可装备
- 品质在绿到紫之间
- 物品大类属于护甲、武器或专业装备

现在插件已经会加载 [NonDisenchantableByWowhead.lua](../../QuickDisenchant/NonDisenchantableByWowhead.lua)，其中包含 Wowhead 标记为不可分解的 `itemID` 集合，但扫描逻辑还没有真正使用这份数据。因此这些物品仍可能出现在 `mainUI` 和 `candidateUI` 中。

## 目标

在扫描背包时直接排除 Wowhead 明确标记为不可分解的物品，使它们：

- 不进入 `allItems`
- 不进入 `selectedKeys`
- 不出现在 `mainUI`
- 不出现在 `candidateUI`
- 不参与白名单和后续分解队列

## 方案

采用“扫描阶段过滤”的方式：

1. 在数据模块新增一个小型判断函数，负责检查 `itemID` 是否命中 `QD.WOWHEAD_NON_DISENCHANTABLE_ITEM_IDS`
2. 在 `collectDisenchantableItems()` 中，先通过现有游戏内规则判断
3. 一旦发现 `itemID` 命中 Wowhead 不可分解黑名单，就直接跳过该物品，不再构造 `itemData`

## 为什么不在 UI 层过滤

如果只在 UI 刷新时过滤：

- 内部状态里仍会保留这些物品
- 选中集、白名单和分解队列都需要额外处理
- 逻辑会变得分散

扫描阶段过滤能让后续所有模块自然保持一致，是更干净的接入点。

## 边界

- 本次不增加聊天提示
- 本次不改 UI 文案
- 如果某个物品没有 `itemID`，继续按现有逻辑处理，不因为缺失 `itemID` 而误过滤

## 验证

新增最小回归测试，验证：

- 命中 `QD.WOWHEAD_NON_DISENCHANTABLE_ITEM_IDS` 的物品不会被 `collectDisenchantableItems()` 返回
- 未命中的物品仍会被正常保留
