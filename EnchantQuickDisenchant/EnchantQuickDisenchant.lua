local ADDON_PREFIX = "[EnchantQuickDisenchant]"
local MIDNIGHT_ENCHANTING_SPELL_ID = 7411

local QUALITY_UNCOMMON = (Enum and Enum.ItemQuality and Enum.ItemQuality.Uncommon) or 2
local QUALITY_EPIC = (Enum and Enum.ItemQuality and Enum.ItemQuality.Epic) or 4

local ITEM_CLASS_WEAPON = (Enum and Enum.ItemClass and Enum.ItemClass.Weapon) or 2
local ITEM_CLASS_ARMOR = (Enum and Enum.ItemClass and Enum.ItemClass.Armor) or 4

local COLUMNS = 3
local VISIBLE_ROWS = 3
local ICON_SIZE = 36
local ICON_GAP = 8
local CONTENT_WIDTH = (COLUMNS * ICON_SIZE) + ((COLUMNS - 1) * ICON_GAP)
local VISIBLE_CONTENT_HEIGHT = (VISIBLE_ROWS * ICON_SIZE) + ((VISIBLE_ROWS - 1) * ICON_GAP)
local WINDOW_WIDTH = CONTENT_WIDTH + 56
local WINDOW_HEIGHT = VISIBLE_CONTENT_HEIGHT + 60

local ui = {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  itemButtons = {},
}

local function hasCurrentVersionEnchanting()
  if C_SpellBook and C_SpellBook.IsSpellKnown then
    return C_SpellBook.IsSpellKnown(MIDNIGHT_ENCHANTING_SPELL_ID) and true or false
  end

  if IsSpellKnownOrOverridesKnown then
    return IsSpellKnownOrOverridesKnown(MIDNIGHT_ENCHANTING_SPELL_ID) and true or false
  end

  if IsSpellKnown then
    return IsSpellKnown(MIDNIGHT_ENCHANTING_SPELL_ID) and true or false
  end

  if IsPlayerSpell then
    return IsPlayerSpell(MIDNIGHT_ENCHANTING_SPELL_ID) and true or false
  end

  return false
end

local function getBagRangeEnd()
  return NUM_TOTAL_EQUIPPED_BAG_SLOTS or NUM_BAG_SLOTS or 4
end

local function isDisenchantableByRules(itemLink, quality)
  if not itemLink or not IsEquippableItem(itemLink) then
    return false
  end

  if quality < QUALITY_UNCOMMON or quality > QUALITY_EPIC then
    return false
  end

  local _, _, _, itemEquipLoc, _, itemClassID = C_Item.GetItemInfoInstant(itemLink)
  if not itemEquipLoc or itemEquipLoc == "" then
    return false
  end

  if itemClassID ~= ITEM_CLASS_ARMOR and itemClassID ~= ITEM_CLASS_WEAPON then
    return false
  end

  return true
end

local function collectDisenchantableItems()
  local items = {}

  for bagID = 0, getBagRangeEnd() do
    local slots = C_Container.GetContainerNumSlots(bagID) or 0

    for slotID = 1, slots do
      local itemInfo = C_Container.GetContainerItemInfo(bagID, slotID)
      if itemInfo and itemInfo.hyperlink then
        local quality = itemInfo.quality or 0
        if isDisenchantableByRules(itemInfo.hyperlink, quality) then
          table.insert(items, {
            itemLink = itemInfo.hyperlink,
            iconFileID = itemInfo.iconFileID,
            quality = quality,
          })
        end
      end
    end
  end

  table.sort(items, function(a, b)
    if a.quality ~= b.quality then
      return a.quality > b.quality
    end

    return a.itemLink < b.itemLink
  end)

  return items
end

local function ensureWindow()
  if ui.frame then
    return
  end

  local frame = CreateFrame("Frame", "EnchantQuickDisenchantWindow", UIParent, "BackdropTemplate")
  frame:SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)
  frame:SetPoint("CENTER")
  frame:SetFrameStrata("MEDIUM")
  frame:SetMovable(true)
  frame:EnableMouse(true)
  frame:RegisterForDrag("LeftButton")
  frame:SetScript("OnDragStart", frame.StartMoving)
  frame:SetScript("OnDragStop", frame.StopMovingOrSizing)
  frame:SetClampedToScreen(true)
  frame:Hide()

  if frame.SetBackdrop then
    frame:SetBackdrop({
      bgFile = "Interface/Tooltips/UI-Tooltip-Background",
      edgeFile = "Interface/Tooltips/UI-Tooltip-Border",
      tile = true,
      tileSize = 8,
      edgeSize = 12,
      insets = { left = 2, right = 2, top = 2, bottom = 2 },
    })
    frame:SetBackdropColor(0.08, 0.08, 0.08, 0.95)
  end

  local closeButton = CreateFrame("Button", nil, frame, "UIPanelCloseButton")
  closeButton:SetPoint("TOPRIGHT", frame, "TOPRIGHT", -4, -4)

  local titleText = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  titleText:SetPoint("TOP", frame, "TOP", 0, -10)
  titleText:SetText("附魔快速分解")

  local scrollFrame = CreateFrame("ScrollFrame", nil, frame, "UIPanelScrollFrameTemplate")
  scrollFrame:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -30)
  scrollFrame:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -30, 12)

  local contentFrame = CreateFrame("Frame", nil, scrollFrame)
  contentFrame:SetSize(CONTENT_WIDTH, VISIBLE_CONTENT_HEIGHT)
  scrollFrame:SetScrollChild(contentFrame)

  local emptyText = contentFrame:CreateFontString(nil, "OVERLAY", "GameFontDisable")
  emptyText:SetPoint("CENTER", contentFrame, "CENTER", 0, 0)
  emptyText:SetText("未找到可分解装备")

  ui.frame = frame
  ui.titleText = titleText
  ui.scrollFrame = scrollFrame
  ui.contentFrame = contentFrame
  ui.emptyText = emptyText
end

local function ensureItemButton(index)
  if ui.itemButtons[index] then
    return ui.itemButtons[index]
  end

  local button = CreateFrame("Button", nil, ui.contentFrame)
  button:SetSize(ICON_SIZE, ICON_SIZE)

  local icon = button:CreateTexture(nil, "ARTWORK")
  icon:SetAllPoints(button)
  button.icon = icon

  local border = button:CreateTexture(nil, "OVERLAY")
  border:SetTexture("Interface/Buttons/UI-ActionButton-Border")
  border:SetBlendMode("ADD")
  border:SetAlpha(0.3)
  border:SetPoint("CENTER")
  border:SetSize(ICON_SIZE + 20, ICON_SIZE + 20)

  button:SetScript("OnEnter", function(self)
    if not self.itemLink then
      return
    end

    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    GameTooltip:SetHyperlink(self.itemLink)
    GameTooltip:Show()
  end)

  button:SetScript("OnLeave", function()
    GameTooltip:Hide()
  end)

  ui.itemButtons[index] = button
  return button
end

local function renderItems(items)
  ensureWindow()

  for index, item in ipairs(items) do
    local button = ensureItemButton(index)
    local column = (index - 1) % COLUMNS
    local row = math.floor((index - 1) / COLUMNS)

    button:ClearAllPoints()
    button:SetPoint("TOPLEFT", ui.contentFrame, "TOPLEFT", column * (ICON_SIZE + ICON_GAP), -row * (ICON_SIZE + ICON_GAP))
    button.icon:SetTexture(item.iconFileID or 134400)
    button.itemLink = item.itemLink
    button:Show()
  end

  for index = #items + 1, #ui.itemButtons do
    local button = ui.itemButtons[index]
    button.itemLink = nil
    button:Hide()
  end

  local rowCount = math.max(1, math.ceil(#items / COLUMNS))
  local contentHeight = (rowCount * ICON_SIZE) + ((rowCount - 1) * ICON_GAP)
  ui.contentFrame:SetSize(CONTENT_WIDTH, contentHeight)
  ui.emptyText:SetShown(#items == 0)

  ui.titleText:SetText(string.format("附魔快速分解 (%d)", #items))
  ui.scrollFrame:SetVerticalScroll(0)
  ui.frame:Show()
end

local function runScan()
  if not hasCurrentVersionEnchanting() then
    print(string.format("%s 未学习至暗之夜附魔。", ADDON_PREFIX))
    return
  end

  local items = collectDisenchantableItems()
  renderItems(items)
end

SLASH_EQD1 = "/eqd"
SlashCmdList["EQD"] = function()
  runScan()
end
