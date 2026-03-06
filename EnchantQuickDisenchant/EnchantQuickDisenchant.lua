local ADDON_PREFIX = "[EnchantQuickDisenchant]"
local MIDNIGHT_ENCHANTING_SPELL_ID = 7411
local DISENCHANT_SPELL_ID = 13262
local DISENCHANT_SPELL_NAME = (C_Spell and C_Spell.GetSpellName and C_Spell.GetSpellName(DISENCHANT_SPELL_ID)) or (GetSpellInfo and GetSpellInfo(DISENCHANT_SPELL_ID)) or "分解"

local QUALITY_UNCOMMON = (Enum and Enum.ItemQuality and Enum.ItemQuality.Uncommon) or 2
local QUALITY_EPIC = (Enum and Enum.ItemQuality and Enum.ItemQuality.Epic) or 4

local ITEM_CLASS_WEAPON = (Enum and Enum.ItemClass and Enum.ItemClass.Weapon) or 2
local ITEM_CLASS_ARMOR = (Enum and Enum.ItemClass and Enum.ItemClass.Armor) or 4

local COLUMNS = 3
local VISIBLE_ROWS = 3
local ICON_SIZE = 36
local ICON_GAP = 8
local PLUS_VISUAL_SIZE = ICON_SIZE - 6
local PLUS_DECOR_SIZE = ICON_SIZE + 4
local CONTENT_WIDTH = (COLUMNS * ICON_SIZE) + ((COLUMNS - 1) * ICON_GAP)
local VISIBLE_CONTENT_HEIGHT = (VISIBLE_ROWS * ICON_SIZE) + ((VISIBLE_ROWS - 1) * ICON_GAP)
local WINDOW_WIDTH = CONTENT_WIDTH + 56
local WINDOW_HEIGHT = VISIBLE_CONTENT_HEIGHT + 60
local DISENCHANT_RESOLVE_TIMEOUT_SECONDS = 1.5
local PRINT_DUMP_MAX_DEPTH = 4

local state = {
  allItems = {},
  allItemsByKey = {},
  selectedKeys = {},
  pendingDisenchant = nil,
}

local mainUI = {
  frame = nil,
  titleText = nil,
  scrollFrame = nil,
  contentFrame = nil,
  emptyText = nil,
  gridPlusButton = nil,
  disenchantButton = nil,
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
local resolvePendingDisenchant
local syncSelectionWithCurrentBags
local getQueueHeadItem
local updateDisenchantButtonAction
local isPendingItemUnchanged
local buildDisenchantFailureReason
local beginPendingDisenchant

local function dumpValue(value, depth, seen)
  local valueType = type(value)

  if valueType == "string" then
    return string.format("%q", value)
  end

  if valueType == "number" or valueType == "boolean" or valueType == "nil" then
    return tostring(value)
  end

  if valueType ~= "table" then
    return string.format("<%s:%s>", valueType, tostring(value))
  end

  if seen[value] then
    return "<cycle>"
  end

  if depth <= 0 then
    return "{...}"
  end

  seen[value] = true

  local keys = {}
  for key in pairs(value) do
    table.insert(keys, key)
  end

  table.sort(keys, function(a, b)
    local typeA = type(a)
    local typeB = type(b)
    if typeA ~= typeB then
      return typeA < typeB
    end

    if typeA == "number" or typeA == "string" then
      return a < b
    end

    return tostring(a) < tostring(b)
  end)

  local parts = {}
  for _, key in ipairs(keys) do
    local keyType = type(key)
    local keyText
    if keyType == "string" and key:match("^[_%a][_%w]*$") then
      keyText = key
    else
      keyText = "[" .. dumpValue(key, depth - 1, seen) .. "]"
    end

    local valueText = dumpValue(value[key], depth - 1, seen)
    table.insert(parts, string.format("%s=%s", keyText, valueText))
  end

  seen[value] = nil
  return "{" .. table.concat(parts, ", ") .. "}"
end

local function print_dump(...)
  local argCount = select("#", ...)
  if argCount == 0 then
    print(string.format("%s [dump] <no args>", ADDON_PREFIX))
    return
  end

  for i = 1, argCount do
    local value = select(i, ...)
    local text = dumpValue(value, PRINT_DUMP_MAX_DEPTH, {})
    print(string.format("%s [dump %d/%d] %s", ADDON_PREFIX, i, argCount, text))
  end
end

_G.print_dump = print_dump

local function registerEscClosableFrame(frame)
  if not frame or not frame.GetName or type(UISpecialFrames) ~= "table" then
    return
  end

  local frameName = frame:GetName()
  if not frameName then
    return
  end

  for _, existingName in ipairs(UISpecialFrames) do
    if existingName == frameName then
      return
    end
  end

  table.insert(UISpecialFrames, frameName)
end

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

local function hasDisenchantSpell()
  if C_SpellBook and C_SpellBook.IsSpellKnown then
    return C_SpellBook.IsSpellKnown(DISENCHANT_SPELL_ID) and true or false
  end

  if IsSpellKnownOrOverridesKnown then
    return IsSpellKnownOrOverridesKnown(DISENCHANT_SPELL_ID) and true or false
  end

  if IsSpellKnown then
    return IsSpellKnown(DISENCHANT_SPELL_ID) and true or false
  end

  if IsPlayerSpell then
    return IsPlayerSpell(DISENCHANT_SPELL_ID) and true or false
  end

  return false
end

local function isDisenchantSpellcastEvent(unit, spellID)
  return unit == "player" and spellID == DISENCHANT_SPELL_ID
end

beginPendingDisenchant = function(actionItem)
  if not actionItem then
    return
  end

  state.pendingDisenchant = {
    key = actionItem.key,
    bagID = actionItem.bagID,
    slotID = actionItem.slotID,
    itemLink = actionItem.itemLink,
    castState = "queued",
    castFailureEvent = nil,
    errorText = nil,
  }

  local pendingRef = state.pendingDisenchant
  C_Timer.After(DISENCHANT_RESOLVE_TIMEOUT_SECONDS, function()
    if state.pendingDisenchant == pendingRef then
      resolvePendingDisenchant()
    end
  end)
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
  registerEscClosableFrame(frame)
  frame:SetScript("OnHide", function()
    if candidateUI.frame then
      candidateUI.frame:Hide()
    end
  end)

  scrollFrame:ClearAllPoints()
  scrollFrame:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -30)
  scrollFrame:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -30, 40)

  local plusButton = CreateFrame("Button", nil, contentFrame)
  plusButton:SetSize(ICON_SIZE, ICON_SIZE)

  local plusNormal = plusButton:CreateTexture(nil, "ARTWORK")
  plusNormal:SetAtlas("itemupgrade_greenplusicon")
  plusNormal:SetPoint("CENTER")
  plusNormal:SetSize(PLUS_VISUAL_SIZE, PLUS_VISUAL_SIZE)

  local plusPushed = plusButton:CreateTexture(nil, "ARTWORK")
  plusPushed:SetAtlas("itemupgrade_greenplusicon_pressed")
  plusPushed:SetPoint("CENTER")
  plusPushed:SetSize(PLUS_VISUAL_SIZE, PLUS_VISUAL_SIZE)

  plusButton:SetNormalTexture(plusNormal)
  plusButton:SetPushedTexture(plusPushed)

  local plusGlow = plusButton:CreateTexture(nil, "OVERLAY")
  plusGlow:SetAtlas("itemupgrade_fx_slotinnerglow")
  plusGlow:SetPoint("CENTER")
  plusGlow:SetSize(PLUS_DECOR_SIZE, PLUS_DECOR_SIZE)
  plusGlow:SetAlpha(0.6)

  local plusBorder = plusButton:CreateTexture(nil, "OVERLAY", nil, 1)
  plusBorder:SetAtlas("itemupgrade_slotborder")
  plusBorder:SetPoint("CENTER")
  plusBorder:SetSize(PLUS_DECOR_SIZE, PLUS_DECOR_SIZE)

  plusButton:SetScript("OnEnter", function()
    plusGlow:SetAlpha(0.8)
  end)
  plusButton:SetScript("OnLeave", function()
    plusGlow:SetAlpha(0.6)
  end)
  plusButton:SetScript("OnClick", function()
    toggleCandidateWindow()
  end)
  plusButton:Hide()

  local disenchantButton = CreateFrame("Button", nil, frame, "SecureActionButtonTemplate,UIPanelButtonTemplate")
  disenchantButton:SetSize(82, 22)
  disenchantButton:SetText("分解")
  disenchantButton:SetPoint("BOTTOM", frame, "BOTTOM", 0, 12)
  disenchantButton:EnableMouse(true)
  if disenchantButton.SetMouseClickEnabled then
    disenchantButton:SetMouseClickEnabled(true)
  end
  if disenchantButton.RegisterForClicks then
    disenchantButton:RegisterForClicks("LeftButtonUp")
  end
  disenchantButton.mode = "empty"
  disenchantButton.actionItem = nil
  disenchantButton:SetScript("PreClick", function(self)
    if self.mode == "armed" and self.actionItem and not state.pendingDisenchant then
      beginPendingDisenchant(self.actionItem)
    end
  end)
  disenchantButton:SetScript("PostClick", function(self)
    if self.mode == "armed" and self.actionItem then
      refreshWindows()
      return
    end

    if self.mode == "missing_spell" then
      print(string.format("%s 未学习分解技能。", ADDON_PREFIX))
    elseif self.mode == "empty" then
      print(string.format("%s 当前无可分解装备。", ADDON_PREFIX))
    elseif self.mode == "busy" then
      print(string.format("%s 正在处理上一件，请稍候。", ADDON_PREFIX))
    elseif self.mode == "invalid_target" then
      syncSelectionWithCurrentBags()
      refreshWindows()
      print(string.format("%s 目标已失效，请重试。", ADDON_PREFIX))
    elseif self.mode == "combat" then
      print(string.format("%s 战斗中无法更新分解动作。", ADDON_PREFIX))
    else
      print(string.format("%s 分解失败，请确认距离、状态和技能可用。", ADDON_PREFIX))
    end
  end)

  mainUI.frame = frame
  mainUI.titleText = titleText
  mainUI.scrollFrame = scrollFrame
  mainUI.contentFrame = contentFrame
  mainUI.emptyText = emptyText
  mainUI.gridPlusButton = plusButton
  mainUI.disenchantButton = disenchantButton
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

syncSelectionWithCurrentBags = function()
  local items, itemsByKey = collectDisenchantableItems()
  local newSelectedKeys = {}

  for key in pairs(state.selectedKeys) do
    if itemsByKey[key] then
      newSelectedKeys[key] = true
    end
  end

  state.allItems = items
  state.allItemsByKey = itemsByKey
  state.selectedKeys = newSelectedKeys
end

getQueueHeadItem = function()
  local selectedItems = getSelectedItems()
  return selectedItems[1]
end

updateDisenchantButtonAction = function()
  if not mainUI.disenchantButton then
    return
  end

  local button = mainUI.disenchantButton
  local mode = "empty"
  local actionItem = nil

  if state.pendingDisenchant then
    mode = "busy"
  elseif not hasDisenchantSpell() then
    mode = "missing_spell"
  else
    actionItem = getQueueHeadItem()
    if not actionItem then
      mode = "empty"
    else
      local itemInfo = C_Container.GetContainerItemInfo(actionItem.bagID, actionItem.slotID)
      if itemInfo and itemInfo.hyperlink == actionItem.itemLink then
        mode = "armed"
      else
        mode = "invalid_target"
        actionItem = nil
      end
    end
  end

  button.mode = mode
  button.actionItem = actionItem

  if not (InCombatLockdown and InCombatLockdown()) then
    if mode == "armed" and actionItem then
      local macrotext = string.format("/cast %s\n/use %d %d", DISENCHANT_SPELL_NAME, actionItem.bagID, actionItem.slotID)
      button:SetAttribute("type", "macro")
      button:SetAttribute("macrotext", macrotext)
    else
      button:SetAttribute("type", nil)
      button:SetAttribute("macrotext", nil)
    end
  elseif mode ~= "armed" then
    button.mode = "combat"
  end

  if mode == "busy" then
    button:SetText("处理中")
  else
    button:SetText("分解")
  end

  button:SetEnabled(mode == "armed")
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

resolvePendingDisenchant = function()
  local pending = state.pendingDisenchant
  if not pending then
    return
  end

  state.pendingDisenchant = nil

  local isSameItem = isPendingItemUnchanged(pending)

  if isSameItem then
    print(string.format("%s 分解失败：%s", ADDON_PREFIX, buildDisenchantFailureReason(pending)))
    refreshWindows()
    return
  end

  state.selectedKeys[pending.key] = nil
  refreshWindows()
  print(string.format("%s 已尝试分解：%s", ADDON_PREFIX, pending.itemLink or "物品"))
end

isPendingItemUnchanged = function(pending)
  if not pending then
    return false
  end

  local currentInfo = C_Container.GetContainerItemInfo(pending.bagID, pending.slotID)
  return currentInfo and currentInfo.hyperlink == pending.itemLink
end

buildDisenchantFailureReason = function(pending)
  if pending.errorText and pending.errorText ~= "" then
    return pending.errorText
  end

  if pending.castFailureEvent == "UNIT_SPELLCAST_FAILED" then
    return "施法失败。"
  end

  if pending.castFailureEvent == "UNIT_SPELLCAST_FAILED_QUIET" then
    return "施法条件不满足。"
  end

  if pending.castFailureEvent == "UNIT_SPELLCAST_INTERRUPTED" then
    return "施法被打断。"
  end

  if pending.castState == "casting" then
    return string.format("施法尚未完成（%.1f 秒内无结果）。", DISENCHANT_RESOLVE_TIMEOUT_SECONDS)
  end

  if pending.castState == "succeeded" then
    return "施法完成但目标物品未变化，可能该装备当前不可分解。"
  end

  if pending.castState == "stopped" then
    return "施法已停止。"
  end

  return "未进入可用的分解施法状态。"
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
  updateDisenchantButtonAction()

  mainUI.titleText:SetText(string.format("可分解装备 (%d)", #selectedItems))
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
  state.pendingDisenchant = nil
  resetSelectionToAllItems()

  ensureMainWindow()
  refreshMainWindow()
  mainUI.frame:Show()

  if candidateUI.frame then
    candidateUI.frame:Hide()
  end
end

local eventFrame = CreateFrame("Frame")
eventFrame:RegisterEvent("BAG_UPDATE_DELAYED")
eventFrame:RegisterEvent("UI_ERROR_MESSAGE")
eventFrame:RegisterEvent("UNIT_SPELLCAST_START")
eventFrame:RegisterEvent("UNIT_SPELLCAST_STOP")
eventFrame:RegisterEvent("UNIT_SPELLCAST_SUCCEEDED")
eventFrame:RegisterEvent("UNIT_SPELLCAST_FAILED")
eventFrame:RegisterEvent("UNIT_SPELLCAST_FAILED_QUIET")
eventFrame:RegisterEvent("UNIT_SPELLCAST_INTERRUPTED")
eventFrame:SetScript("OnEvent", function(_, event, ...)
  local pending = state.pendingDisenchant
  if not pending then
    return
  end

  if event == "BAG_UPDATE_DELAYED" then
    local unchanged = isPendingItemUnchanged(pending)
    if not unchanged then
      resolvePendingDisenchant()
      return
    end

    if pending.errorText or pending.castFailureEvent then
      resolvePendingDisenchant()
    end
    return
  end

  if event == "UI_ERROR_MESSAGE" then
    local _, errorText = ...
    if type(errorText) == "string" and errorText ~= "" then
      pending.errorText = errorText
    end
    return
  end

  local unit, _, spellID = ...
  if not isDisenchantSpellcastEvent(unit, spellID) then
    return
  end

  if event == "UNIT_SPELLCAST_START" then
    pending.castState = "casting"
    pending.castFailureEvent = nil
    pending.errorText = nil
    return
  end

  if event == "UNIT_SPELLCAST_SUCCEEDED" then
    pending.castState = "succeeded"
    return
  end

  if event == "UNIT_SPELLCAST_STOP" then
    if pending.castState ~= "succeeded" then
      pending.castState = "stopped"
    end
    return
  end

  if event == "UNIT_SPELLCAST_FAILED" or event == "UNIT_SPELLCAST_FAILED_QUIET" or event == "UNIT_SPELLCAST_INTERRUPTED" then
    pending.castState = "failed"
    pending.castFailureEvent = event
    resolvePendingDisenchant()
    return
  end
end)

SLASH_EQD1 = "/eqd"
SlashCmdList["EQD"] = function()
  runScan()
end
