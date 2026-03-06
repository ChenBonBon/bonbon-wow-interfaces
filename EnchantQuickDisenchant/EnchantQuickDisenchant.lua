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

local state = {
  allItems = {},
  allItemsByKey = {},
  selectedKeys = {},
}

local mainUI = {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  gridPlusButton = nil,
  itemButtons = {},
}

local candidateUI = {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  itemButtons = {},
}

local refreshWindows
local toggleCandidateWindow

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
  local itemsByKey = {}

  for bagID = 0, getBagRangeEnd() do
    local slots = C_Container.GetContainerNumSlots(bagID) or 0

    for slotID = 1, slots do
      local itemInfo = C_Container.GetContainerItemInfo(bagID, slotID)
      if itemInfo and itemInfo.hyperlink then
        local quality = itemInfo.quality or 0
        if isDisenchantableByRules(itemInfo.hyperlink, quality) then
          local key = string.format("%d:%d", bagID, slotID)
          local itemData = {
            key = key,
            bagID = bagID,
            slotID = slotID,
            itemLink = itemInfo.hyperlink,
            iconFileID = itemInfo.iconFileID,
            quality = quality,
          }
          table.insert(items, itemData)
          itemsByKey[key] = itemData
        end
      end
    end
  end

  table.sort(items, function(a, b)
    if a.quality ~= b.quality then
      return a.quality > b.quality
    end

    return tostring(a.itemLink) < tostring(b.itemLink)
  end)

  return items, itemsByKey
end

local function createWindowFrame(frameName)
  local frame = CreateFrame("Frame", frameName, UIParent, "BackdropTemplate")
  frame:SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)
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

  local scrollFrame = CreateFrame("ScrollFrame", nil, frame, "UIPanelScrollFrameTemplate")
  scrollFrame:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -30)
  scrollFrame:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -30, 12)

  local contentFrame = CreateFrame("Frame", nil, scrollFrame)
  contentFrame:SetSize(CONTENT_WIDTH, VISIBLE_CONTENT_HEIGHT)
  scrollFrame:SetScrollChild(contentFrame)

  local emptyText = contentFrame:CreateFontString(nil, "OVERLAY", "GameFontDisable")
  emptyText:SetPoint("CENTER", contentFrame, "CENTER", 0, 0)
  emptyText:SetText("未找到可分解装备")

  return frame, titleText, scrollFrame, contentFrame, emptyText
end

local function ensureMainWindow()
  if mainUI.frame then
    return
  end

  local frame, titleText, scrollFrame, contentFrame, emptyText = createWindowFrame("EnchantQuickDisenchantWindow")
  frame:SetPoint("CENTER")
  frame:SetScript("OnHide", function()
    if candidateUI.frame then
      candidateUI.frame:Hide()
    end
  end)

  local plusButton = CreateFrame("Button", nil, contentFrame, "UIPanelButtonTemplate")
  plusButton:SetSize(20, 20)
  plusButton:SetText("+")
  plusButton:SetScript("OnClick", function()
    toggleCandidateWindow()
  end)
  plusButton:Hide()

  mainUI.frame = frame
  mainUI.titleText = titleText
  mainUI.scrollFrame = scrollFrame
  mainUI.contentFrame = contentFrame
  mainUI.emptyText = emptyText
  mainUI.gridPlusButton = plusButton
end

local function ensureCandidateWindow()
  if candidateUI.frame then
    return
  end

  local frame, titleText, scrollFrame, contentFrame, emptyText = createWindowFrame("EnchantQuickDisenchantCandidateWindow")
  titleText:SetText("可添加装备")

  candidateUI.frame = frame
  candidateUI.titleText = titleText
  candidateUI.scrollFrame = scrollFrame
  candidateUI.contentFrame = contentFrame
  candidateUI.emptyText = emptyText
end

local function ensureGridButton(uiSet, index, onClick)
  if uiSet.itemButtons[index] then
    return uiSet.itemButtons[index]
  end

  local button = CreateFrame("Button", nil, uiSet.contentFrame)
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
  button.border = border

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

  button:SetScript("OnClick", function(self, mouseButton)
    onClick(self, mouseButton)
  end)

  uiSet.itemButtons[index] = button
  return button
end

local function getSelectedItems()
  local selectedItems = {}

  for _, item in ipairs(state.allItems) do
    if state.selectedKeys[item.key] then
      table.insert(selectedItems, item)
    end
  end

  return selectedItems
end

local function renderGrid(uiSet, items, onClick, isDisabled)
  for index, item in ipairs(items) do
    local button = ensureGridButton(uiSet, index, onClick)
    local column = (index - 1) % COLUMNS
    local row = math.floor((index - 1) / COLUMNS)
    local disabled = isDisabled and isDisabled(item) or false

    button:ClearAllPoints()
    button:SetPoint("TOPLEFT", uiSet.contentFrame, "TOPLEFT", column * (ICON_SIZE + ICON_GAP), -row * (ICON_SIZE + ICON_GAP))
    button.icon:SetTexture(item.iconFileID or 134400)
    button.icon:SetDesaturated(disabled)
    button.icon:SetAlpha(disabled and 0.35 or 1)
    button.border:SetAlpha(disabled and 0.12 or 0.3)
    button.itemKey = item.key
    button.itemLink = item.itemLink
    button.isDisabled = disabled
    button:Show()
  end

  for index = #items + 1, #uiSet.itemButtons do
    local button = uiSet.itemButtons[index]
    button.itemKey = nil
    button.itemLink = nil
    button.isDisabled = false
    button:Hide()
  end

  local rowCount = math.max(1, math.ceil(#items / COLUMNS))
  local contentHeight = (rowCount * ICON_SIZE) + ((rowCount - 1) * ICON_GAP)
  uiSet.contentFrame:SetSize(CONTENT_WIDTH, contentHeight)
  uiSet.emptyText:SetShown(#items == 0)
  uiSet.scrollFrame:SetVerticalScroll(0)
end

local function onMainItemClick(self)
  if not self.itemKey or not state.selectedKeys[self.itemKey] then
    return
  end

  state.selectedKeys[self.itemKey] = nil
  refreshWindows()
end

local function onCandidateItemClick(self)
  if not self.itemKey or self.isDisabled then
    return
  end

  if not state.allItemsByKey[self.itemKey] then
    return
  end

  state.selectedKeys[self.itemKey] = true
  refreshWindows()
end

local function refreshMainWindow()
  ensureMainWindow()

  local selectedItems = getSelectedItems()
  renderGrid(mainUI, selectedItems, onMainItemClick)

  local plusIndex = #selectedItems + 1
  local plusColumn = (plusIndex - 1) % COLUMNS
  local plusRow = math.floor((plusIndex - 1) / COLUMNS)
  mainUI.gridPlusButton:ClearAllPoints()
  mainUI.gridPlusButton:SetPoint("TOPLEFT", mainUI.contentFrame, "TOPLEFT", plusColumn * (ICON_SIZE + ICON_GAP), -plusRow * (ICON_SIZE + ICON_GAP))
  mainUI.gridPlusButton:Show()

  local slotCount = #selectedItems + 1
  local rowCount = math.max(1, math.ceil(slotCount / COLUMNS))
  local contentHeight = (rowCount * ICON_SIZE) + ((rowCount - 1) * ICON_GAP)
  mainUI.contentFrame:SetSize(CONTENT_WIDTH, contentHeight)
  mainUI.emptyText:SetShown(#selectedItems == 0)
  mainUI.scrollFrame:SetVerticalScroll(0)

  mainUI.titleText:SetText(string.format("附魔快速分解 (%d)", #selectedItems))
end

local function refreshCandidateWindow()
  ensureCandidateWindow()

  local total = #state.allItems
  local selectedCount = 0
  for _, item in ipairs(state.allItems) do
    if state.selectedKeys[item.key] then
      selectedCount = selectedCount + 1
    end
  end

  renderGrid(candidateUI, state.allItems, onCandidateItemClick, function(item)
    return state.selectedKeys[item.key] and true or false
  end)

  candidateUI.titleText:SetText(string.format("可添加装备 (%d/%d)", total - selectedCount, total))
end

refreshWindows = function()
  if mainUI.frame and mainUI.frame:IsShown() then
    refreshMainWindow()
  end

  if candidateUI.frame and candidateUI.frame:IsShown() then
    refreshCandidateWindow()
  end
end

toggleCandidateWindow = function()
  if not mainUI.frame or not mainUI.frame:IsShown() then
    return
  end

  ensureCandidateWindow()

  if candidateUI.frame:IsShown() then
    candidateUI.frame:Hide()
    return
  end

  candidateUI.frame:ClearAllPoints()
  candidateUI.frame:SetPoint("TOPLEFT", mainUI.frame, "TOPRIGHT", 12, 0)
  refreshCandidateWindow()
  candidateUI.frame:Show()
end

local function resetSelectionToAllItems()
  state.selectedKeys = {}

  for _, item in ipairs(state.allItems) do
    state.selectedKeys[item.key] = true
  end
end

local function runScan()
  if not hasCurrentVersionEnchanting() then
    print(string.format("%s 未学习至暗之夜附魔。", ADDON_PREFIX))
    return
  end

  local items, itemsByKey = collectDisenchantableItems()
  state.allItems = items
  state.allItemsByKey = itemsByKey
  resetSelectionToAllItems()

  ensureMainWindow()
  refreshMainWindow()
  mainUI.frame:Show()

  if candidateUI.frame then
    candidateUI.frame:Hide()
  end
end

SLASH_EQD1 = "/eqd"
SlashCmdList["EQD"] = function()
  runScan()
end
