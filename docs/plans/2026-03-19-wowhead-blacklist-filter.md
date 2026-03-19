# QuickDisenchant Wowhead 不可分解黑名单过滤实现计划

### Task 1: 为扫描逻辑补回归测试

**Files:**
- Modify: `QuickDisenchant/Tests.lua` 或当前测试所在位置（如果项目已有 Lua 侧测试入口则复用；若没有，则以最小可验证方式补充）
- Modify: `docs/plans/2026-03-19-wowhead-blacklist-filter-design.md`

**Step 1: 写失败测试**
- 构造一个命中 `QD.WOWHEAD_NON_DISENCHANTABLE_ITEM_IDS` 的物品
- 验证 `collectDisenchantableItems()` 不返回它

**Step 2: 运行或静态核对测试前置条件**
- 确认测试在现有结构下会失败，原因是扫描逻辑尚未使用 Wowhead 黑名单

### Task 2: 在扫描阶段接入 Wowhead 黑名单

**Files:**
- Modify: `QuickDisenchant/Data.lua`

**Step 1: 新增小型辅助函数**
- 根据 `itemID` 判断是否命中 `QD.WOWHEAD_NON_DISENCHANTABLE_ITEM_IDS`

**Step 2: 修改 `collectDisenchantableItems()`**
- 在构造 `itemData` 前执行黑名单判断
- 命中则直接跳过

**Step 3: 保持其他逻辑不变**
- 不改 UI
- 不改白名单逻辑
- 不改分解逻辑

### Task 3: 验证并提交

**Step 1: 运行相关验证**
- 如果有 Lua 测试入口则执行
- 如果没有，至少做静态检查并记录限制

**Step 2: 检查 diff**
- 确认只改动扫描过滤相关文件和文档

**Step 3: 提交**
- 使用清晰的 commit message
