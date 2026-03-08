-- Core module: defines addon namespace, constants, and shared state containers.
local _, QD = ...
QD = QD or {}
_G.QuickDisenchantNS = QD

-- Addon chat prefix used for all user-facing log messages.
QD.ADDON_PREFIX = "[QuickDisenchant]"

-- Spell identity used by secure macro flow.
QD.DISENCHANT_SPELL_ID = 13262
QD.DISENCHANT_SPELL_NAME = (C_Spell and C_Spell.GetSpellName and C_Spell.GetSpellName(QD.DISENCHANT_SPELL_ID)) or (GetSpellInfo and GetSpellInfo(QD.DISENCHANT_SPELL_ID)) or "分解"

-- Item quality bounds for disenchant candidate filtering.
QD.QUALITY_UNCOMMON = (Enum and Enum.ItemQuality and Enum.ItemQuality.Uncommon) or 2
QD.QUALITY_EPIC = (Enum and Enum.ItemQuality and Enum.ItemQuality.Epic) or 4

-- Allowed item classes for disenchant candidates.
QD.ITEM_CLASS_WEAPON = (Enum and Enum.ItemClass and Enum.ItemClass.Weapon) or 2
QD.ITEM_CLASS_ARMOR = (Enum and Enum.ItemClass and Enum.ItemClass.Armor) or 4

-- Grid and layout configuration.
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

-- Timeout fallback for pending disenchant resolution.
QD.DISENCHANT_RESOLVE_TIMEOUT_SECONDS = 3.0

-- Runtime data for all scanned/selected items and current pending operation.
QD.state = QD.state or {
  allItems = {},
  allItemsByKey = {},
  selectedKeys = {},
  pendingDisenchant = nil,
}

-- Primary window references.
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

-- Candidate window references.
QD.candidateUI = QD.candidateUI or {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  itemButtons = {},
}
