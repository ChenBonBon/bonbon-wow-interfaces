-- 核心模块：定义插件命名空间、常量和共享状态容器。
local _, QD = ...
QD = QD or {}
_G.QuickDisenchantNS = QD

-- 插件聊天前缀，用于所有面向用户的输出。
QD.ADDON_PREFIX = "[QuickDisenchant]"

-- 安全宏分解流程使用的法术标识。
QD.DISENCHANT_SPELL_ID = 13262
QD.DISENCHANT_SPELL_NAME = (C_Spell and C_Spell.GetSpellName and C_Spell.GetSpellName(QD.DISENCHANT_SPELL_ID)) or (GetSpellInfo and GetSpellInfo(QD.DISENCHANT_SPELL_ID)) or "分解"

-- 可分解候选过滤使用的装备品质范围。
QD.QUALITY_UNCOMMON = (Enum and Enum.ItemQuality and Enum.ItemQuality.Uncommon) or 2
QD.QUALITY_EPIC = (Enum and Enum.ItemQuality and Enum.ItemQuality.Epic) or 4

-- 可分解候选允许的物品大类。
QD.ITEM_CLASS_WEAPON = (Enum and Enum.ItemClass and Enum.ItemClass.Weapon) or 2
QD.ITEM_CLASS_ARMOR = (Enum and Enum.ItemClass and Enum.ItemClass.Armor) or 4

-- 宫格与窗口布局配置。
QD.COLUMNS = 3
QD.VISIBLE_ROWS = 3
QD.ICON_SIZE = 36
QD.ICON_GAP = 8
QD.PLUS_VISUAL_SIZE = QD.ICON_SIZE - 6
QD.PLUS_DECOR_SIZE = QD.ICON_SIZE + 4
QD.CONTENT_WIDTH = (QD.COLUMNS * QD.ICON_SIZE) + ((QD.COLUMNS - 1) * QD.ICON_GAP)
QD.VISIBLE_CONTENT_HEIGHT = (QD.VISIBLE_ROWS * QD.ICON_SIZE) + ((QD.VISIBLE_ROWS - 1) * QD.ICON_GAP)
QD.WINDOW_WIDTH = QD.CONTENT_WIDTH + 56
QD.WINDOW_HEIGHT = QD.VISIBLE_CONTENT_HEIGHT + 60

-- 待处理分解结算的超时兜底秒数。
QD.DISENCHANT_RESOLVE_TIMEOUT_SECONDS = 3.0

-- 运行时数据：扫描结果、选中集合与当前待处理分解状态。
QD.state = QD.state or {
  allItems = {},
  allItemsByKey = {},
  selectedKeys = {},
  whitelistByGUID = {},
  pendingDisenchant = nil,
}
QD.state.whitelistByGUID = QD.state.whitelistByGUID or {}

-- 主窗口引用集合。
QD.mainUI = QD.mainUI or {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  gridPlusButton = nil,
  disenchantButton = nil,
  itemButtons = {},
}

-- 候选窗口引用集合。
QD.candidateUI = QD.candidateUI or {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  itemButtons = {},
}
