-- 界面模块：负责窗口创建、宫格渲染与选择交互。
local _, QD = ...
QD = QD or _G.QuickDisenchantNS
if not QD then
  return
end

local FILTER_DEFINITIONS = {
  { key = "all", label = "全部" },
  { key = "weapon", label = "武器" },
  { key = "cloth", label = "布甲" },
  { key = "leather", label = "皮甲" },
  { key = "mail", label = "锁甲" },
  { key = "plate", label = "板甲" },
  { key = "other", label = "其他" },
}

local FILTER_BUTTON_GAP = 2
local FILTER_BUTTON_HEIGHT = 20
local FILTER_FRAME_TOP_OFFSET = -28
local FILTER_FRAME_HEIGHT = 22
local FILTER_SCROLL_TOP_OFFSET = -58

-- 规范化按钮所属的分类键，避免后续状态比较分散。
function QD.getCategoryFilterDefinitions()
  return FILTER_DEFINITIONS
end

-- 创建或更新窗口顶部的分类筛选按钮。
function QD.ensureFilterButtonRow(uiSet)
  if not uiSet or not uiSet.frame then
    return
  end

  if uiSet.filterFrame then
    return
  end

  local filterFrame = CreateFrame("Frame", nil, uiSet.frame)
  filterFrame:SetPoint("TOPLEFT", uiSet.frame, "TOPLEFT", 12, FILTER_FRAME_TOP_OFFSET)
  filterFrame:SetPoint("TOPRIGHT", uiSet.frame, "TOPRIGHT", -12, FILTER_FRAME_TOP_OFFSET)
  filterFrame:SetHeight(FILTER_FRAME_HEIGHT)

  local filterButtons = {}
  local buttonWidth = math.floor(((uiSet.frame:GetWidth() or QD.WINDOW_WIDTH) - 24 - ((#FILTER_DEFINITIONS - 1) * FILTER_BUTTON_GAP)) / #FILTER_DEFINITIONS)
  if buttonWidth < 24 then
    buttonWidth = 24
  end

  for index, filterDef in ipairs(FILTER_DEFINITIONS) do
    local button = CreateFrame("Button", nil, filterFrame, "UIPanelButtonTemplate")
    button:SetSize(buttonWidth, FILTER_BUTTON_HEIGHT)
    button:SetPoint("LEFT", filterFrame, "LEFT", (index - 1) * (buttonWidth + FILTER_BUTTON_GAP), 0)
    button:SetText(filterDef.label)
    button:SetNormalFontObject("GameFontNormalSmall")
    button:SetHighlightFontObject("GameFontHighlightSmall")
    button:SetDisabledFontObject("GameFontDisableSmall")
    button.baseLabel = filterDef.label

    button.filterKey = filterDef.key
    button:SetScript("OnClick", function(self)
      QD.state.activeFilterKey = self.filterKey
      QD.refreshWindows()
    end)

    filterButtons[index] = button
  end

  uiSet.filterFrame = filterFrame
  uiSet.filterButtons = filterButtons
  QD.updateFilterButtonRow(uiSet)
end

-- 按当前 activeFilterKey 刷新按钮高亮。
function QD.updateFilterButtonRow(uiSet)
  if not uiSet or not uiSet.filterButtons then
    return
  end

  local activeFilterKey = QD.normalizeActiveFilterKey and QD.normalizeActiveFilterKey(QD.state and QD.state.activeFilterKey) or "all"
  local categoryCounts = QD.getCategoryFilterCounts and QD.getCategoryFilterCounts() or {}
  for _, button in ipairs(uiSet.filterButtons) do
    local isActive = button.filterKey == activeFilterKey
    local count = categoryCounts[button.filterKey] or 0
    button:SetText(string.format("%s(%d)", button.baseLabel or "", count))
    local fontString = button.GetFontString and button:GetFontString() or nil
    if isActive then
      if button.SetButtonState then
        button:SetButtonState("PUSHED", true)
      end
      button:LockHighlight()
      if fontString then
        fontString:SetTextColor(1, 0.95, 0.75)
        fontString:ClearAllPoints()
        fontString:SetPoint("CENTER", button, "CENTER", 0, -1)
      end
    else
      if button.SetButtonState then
        button:SetButtonState("NORMAL")
      end
      button:UnlockHighlight()
      if fontString then
        fontString:SetTextColor(0.95, 0.82, 0.45)
        fontString:ClearAllPoints()
        fontString:SetPoint("CENTER", button, "CENTER", 0, 0)
      end
    end
  end
end

-- 创建标准窗口框体（标题、滚动区域与空状态文本）。
function QD.createWindowFrame(frameName)
  local frame = CreateFrame("Frame", frameName, UIParent, "BackdropTemplate")
  frame:SetSize(QD.WINDOW_WIDTH, QD.WINDOW_HEIGHT)
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
  contentFrame:SetSize(QD.CONTENT_WIDTH, QD.VISIBLE_CONTENT_HEIGHT)
  scrollFrame:SetScrollChild(contentFrame)

  local emptyText = contentFrame:CreateFontString(nil, "OVERLAY", "GameFontDisable")
  emptyText:SetPoint("CENTER", contentFrame, "CENTER", 0, 0)
  emptyText:SetText("未找到可分解装备")

  return frame, titleText, scrollFrame, contentFrame, emptyText
end

-- 延迟创建主选择窗口及其操作控件。
function QD.ensureMainWindow()
  if QD.mainUI.frame then
    return
  end

  local frame, titleText, scrollFrame, contentFrame, emptyText = QD.createWindowFrame("QuickDisenchantWindow")
  frame:SetPoint("CENTER")
  QD.registerEscClosableFrame(frame)
  frame:SetScript("OnHide", function()
    if QD.candidateUI.frame then
      QD.candidateUI.frame:Hide()
    end
  end)

  QD.mainUI.frame = frame
  QD.ensureFilterButtonRow(QD.mainUI)
  scrollFrame:ClearAllPoints()
  scrollFrame:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, FILTER_SCROLL_TOP_OFFSET)
  scrollFrame:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -30, 40)

  local plusButton = CreateFrame("Button", nil, contentFrame)
  plusButton:SetSize(QD.ICON_SIZE, QD.ICON_SIZE)

  local plusNormal = plusButton:CreateTexture(nil, "ARTWORK")
  plusNormal:SetAtlas("itemupgrade_greenplusicon")
  plusNormal:SetPoint("CENTER")
  plusNormal:SetSize(QD.PLUS_VISUAL_SIZE, QD.PLUS_VISUAL_SIZE)

  local plusPushed = plusButton:CreateTexture(nil, "ARTWORK")
  plusPushed:SetAtlas("itemupgrade_greenplusicon_pressed")
  plusPushed:SetPoint("CENTER")
  plusPushed:SetSize(QD.PLUS_VISUAL_SIZE, QD.PLUS_VISUAL_SIZE)

  plusButton:SetNormalTexture(plusNormal)
  plusButton:SetPushedTexture(plusPushed)

  local plusGlow = plusButton:CreateTexture(nil, "OVERLAY")
  plusGlow:SetAtlas("itemupgrade_fx_slotinnerglow")
  plusGlow:SetPoint("CENTER")
  plusGlow:SetSize(QD.PLUS_DECOR_SIZE, QD.PLUS_DECOR_SIZE)
  plusGlow:SetAlpha(0.6)

  local plusBorder = plusButton:CreateTexture(nil, "OVERLAY", nil, 1)
  plusBorder:SetAtlas("itemupgrade_slotborder")
  plusBorder:SetPoint("CENTER")
  plusBorder:SetSize(QD.PLUS_DECOR_SIZE, QD.PLUS_DECOR_SIZE)

  plusButton:SetScript("OnEnter", function()
    plusGlow:SetAlpha(0.8)
  end)
  plusButton:SetScript("OnLeave", function()
    plusGlow:SetAlpha(0.6)
  end)
  plusButton:SetScript("OnClick", function()
    QD.toggleCandidateWindow()
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
    if self.mode == "armed" and self.actionItem and not QD.state.pendingDisenchant then
      QD.beginPendingDisenchant(self.actionItem)
    end
  end)
  disenchantButton:SetScript("PostClick", function(self)
    if self.mode == "armed" and self.actionItem then
      QD.refreshWindows()
      return
    end

    if self.mode == "missing_spell" then
      print(string.format("%s 未学习分解技能。", QD.ADDON_PREFIX))
    elseif self.mode == "empty" then
      print(string.format("%s 当前无可分解装备。", QD.ADDON_PREFIX))
    elseif self.mode == "busy" then
      print(string.format("%s 正在处理上一件，请稍候。", QD.ADDON_PREFIX))
    elseif self.mode == "invalid_target" then
      QD.syncSelectionWithCurrentBags()
      QD.refreshWindows()
      print(string.format("%s 目标已失效，请重试。", QD.ADDON_PREFIX))
    elseif self.mode == "combat" then
      print(string.format("%s 战斗中无法更新分解动作。", QD.ADDON_PREFIX))
    else
      print(string.format("%s 分解失败，请确认距离、状态和技能可用。", QD.ADDON_PREFIX))
    end
  end)

  QD.mainUI.titleText = titleText
  QD.mainUI.scrollFrame = scrollFrame
  QD.mainUI.contentFrame = contentFrame
  QD.mainUI.emptyText = emptyText
  QD.mainUI.gridPlusButton = plusButton
  QD.mainUI.disenchantButton = disenchantButton
end

-- 延迟创建候选列表窗口。
function QD.ensureCandidateWindow()
  if QD.candidateUI.frame then
    return
  end

  local frame, titleText, scrollFrame, contentFrame, emptyText = QD.createWindowFrame("QuickDisenchantCandidateWindow")
  titleText:SetText("可添加装备")

  QD.candidateUI.frame = frame
  QD.ensureFilterButtonRow(QD.candidateUI)
  scrollFrame:ClearAllPoints()
  scrollFrame:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, FILTER_SCROLL_TOP_OFFSET)
  scrollFrame:SetPoint("BOTTOMRIGHT", frame, "BOTTOMRIGHT", -30, 12)

  QD.candidateUI.titleText = titleText
  QD.candidateUI.scrollFrame = scrollFrame
  QD.candidateUI.contentFrame = contentFrame
  QD.candidateUI.emptyText = emptyText
end

-- 创建（或复用）宫格物品按钮。
function QD.ensureGridButton(uiSet, index, onClick)
  if uiSet.itemButtons[index] then
    return uiSet.itemButtons[index]
  end

  local button = CreateFrame("Button", nil, uiSet.contentFrame)
  button:SetSize(QD.ICON_SIZE, QD.ICON_SIZE)

  local icon = button:CreateTexture(nil, "ARTWORK")
  icon:SetAllPoints(button)
  button.icon = icon

  local border = button:CreateTexture(nil, "OVERLAY")
  border:SetTexture("Interface/Buttons/UI-ActionButton-Border")
  border:SetBlendMode("ADD")
  border:SetAlpha(0.3)
  border:SetPoint("CENTER")
  border:SetSize(QD.ICON_SIZE + 20, QD.ICON_SIZE + 20)
  button.border = border

  -- 白名单锁图标：在候选窗口里用于直观标记“已锁定/白名单”物品。
  local lockIcon = button:CreateTexture(nil, "OVERLAY", nil, 2)
  lockIcon:SetTexture("Interface/Buttons/LockButton-Locked-Up")
  lockIcon:SetSize(14, 14)
  lockIcon:SetPoint("TOPRIGHT", button, "TOPRIGHT", -1, -1)
  lockIcon:Hide()
  button.lockIcon = lockIcon

  button:SetScript("OnEnter", function(self)
    if not self.itemLink then
      return
    end

    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    GameTooltip:SetHyperlink(self.itemLink)
    if self.isWhitelisted then
      GameTooltip:AddLine("白名单：右键可移除", 0.3, 1, 0.3)
    end
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

-- 将滚动位置限制在当前可滚动范围内，并应用目标位置。
function QD.applyClampedScroll(uiSet, targetScroll)
  if not uiSet or not uiSet.scrollFrame or not uiSet.scrollFrame.SetVerticalScroll then
    return
  end

  local maxScroll = 0
  if uiSet.scrollFrame.GetVerticalScrollRange then
    maxScroll = uiSet.scrollFrame:GetVerticalScrollRange() or 0
  end
  if maxScroll < 0 then
    maxScroll = 0
  end

  local scroll = targetScroll or 0
  if scroll < 0 then
    scroll = 0
  elseif scroll > maxScroll then
    scroll = maxScroll
  end

  uiSet.scrollFrame:SetVerticalScroll(scroll)
end

-- 将物品列表渲染到指定宫格 UI 集合。
function QD.renderGrid(uiSet, items, onClick, isDisabled, isWhitelisted)
  local previousScroll = 0
  if uiSet.scrollFrame and uiSet.scrollFrame.GetVerticalScroll then
    previousScroll = uiSet.scrollFrame:GetVerticalScroll() or 0
  end

  for index, item in ipairs(items) do
    local button = QD.ensureGridButton(uiSet, index, onClick)
    local column = (index - 1) % QD.COLUMNS
    local row = math.floor((index - 1) / QD.COLUMNS)
    local disabled = isDisabled and isDisabled(item) or false
    local whitelisted = isWhitelisted and isWhitelisted(item) or false

    button:ClearAllPoints()
    button:SetPoint("TOPLEFT", uiSet.contentFrame, "TOPLEFT", column * (QD.ICON_SIZE + QD.ICON_GAP), -row * (QD.ICON_SIZE + QD.ICON_GAP))
    button.icon:SetTexture(item.iconFileID or 134400)
    button.icon:SetDesaturated(disabled)
    button.icon:SetAlpha(disabled and 0.35 or 1)
    if whitelisted then
      button.border:SetVertexColor(0.2, 1, 0.2)
      button.border:SetAlpha(0.45)
    else
      button.border:SetVertexColor(1, 1, 1)
      button.border:SetAlpha(disabled and 0.12 or 0.3)
    end
    button.itemKey = item.key
    button.itemLink = item.itemLink
    button.isDisabled = disabled
    button.isWhitelisted = whitelisted
    button.lockIcon:SetShown(whitelisted)
    if button.RegisterForClicks then
      if uiSet == QD.candidateUI then
        button:RegisterForClicks("LeftButtonUp", "RightButtonUp")
      else
        button:RegisterForClicks("LeftButtonUp")
      end
    end
    button:Show()
  end

  for index = #items + 1, #uiSet.itemButtons do
    local button = uiSet.itemButtons[index]
    button.itemKey = nil
    button.itemLink = nil
    button.isDisabled = false
    button.isWhitelisted = false
    button.border:SetVertexColor(1, 1, 1)
    button.lockIcon:Hide()
    button:Hide()
  end

  local rowCount = math.max(1, math.ceil(#items / QD.COLUMNS))
  local contentHeight = (rowCount * QD.ICON_SIZE) + ((rowCount - 1) * QD.ICON_GAP)
  uiSet.contentFrame:SetSize(QD.CONTENT_WIDTH, contentHeight)
  uiSet.emptyText:SetShown(#items == 0)
  QD.applyClampedScroll(uiSet, previousScroll)
end

-- 在主窗口点击物品时，将其从已选列表移除。
function QD.onMainItemClick(self)
  if not self.itemKey or not QD.state.selectedKeys[self.itemKey] then
    return
  end

  QD.state.selectedKeys[self.itemKey] = nil
  QD.refreshWindows()
end

-- 在候选窗口点击物品时，左键加入已选；右键切换白名单。
function QD.onCandidateItemClick(self, mouseButton)
  if not self.itemKey then
    return
  end

  local item = QD.state.allItemsByKey[self.itemKey]
  if not item then
    return
  end

  if mouseButton == "RightButton" then
    if (not item.itemGUID or item.itemGUID == "") and QD.getBagSlotItemGUID then
      item.itemGUID = QD.getBagSlotItemGUID(item.bagID, item.slotID)
    end

    if not item.itemGUID or item.itemGUID == "" then
      print(string.format("%s 该物品缺少 GUID，无法加入白名单。", QD.ADDON_PREFIX))
      return
    end

    local isNowWhitelisted = QD.toggleWhitelistForItem(item)
    if isNowWhitelisted then
      QD.state.selectedKeys[item.key] = nil
      print(string.format("%s 已加入白名单：%s", QD.ADDON_PREFIX, item.itemLink or "物品"))
    else
      print(string.format("%s 已移出白名单：%s", QD.ADDON_PREFIX, item.itemLink or "物品"))
    end
    QD.refreshWindows()
    return
  end

  if self.isDisabled then
    if self.isWhitelisted then
      print(string.format("%s 白名单物品不可添加，右键可移出白名单。", QD.ADDON_PREFIX))
    end
    return
  end

  QD.state.selectedKeys[self.itemKey] = true
  QD.refreshWindows()
end

-- 刷新主窗口：标题、宫格、加号槽位与分解按钮状态。
function QD.refreshMainWindow()
  QD.ensureMainWindow()
  QD.updateFilterButtonRow(QD.mainUI)

  local selectedItems = QD.getFilteredSelectedItems()
  QD.renderGrid(QD.mainUI, selectedItems, QD.onMainItemClick)

  local plusIndex = #selectedItems + 1
  local plusColumn = (plusIndex - 1) % QD.COLUMNS
  local plusRow = math.floor((plusIndex - 1) / QD.COLUMNS)
  QD.mainUI.gridPlusButton:ClearAllPoints()
  QD.mainUI.gridPlusButton:SetPoint("TOPLEFT", QD.mainUI.contentFrame, "TOPLEFT", plusColumn * (QD.ICON_SIZE + QD.ICON_GAP), -plusRow * (QD.ICON_SIZE + QD.ICON_GAP))
  QD.mainUI.gridPlusButton:Show()

  local slotCount = #selectedItems + 1
  local rowCount = math.max(1, math.ceil(slotCount / QD.COLUMNS))
  local contentHeight = (rowCount * QD.ICON_SIZE) + ((rowCount - 1) * QD.ICON_GAP)
  QD.mainUI.contentFrame:SetSize(QD.CONTENT_WIDTH, contentHeight)
  QD.mainUI.emptyText:SetShown(#selectedItems == 0)
  QD.applyClampedScroll(QD.mainUI, QD.mainUI.scrollFrame:GetVerticalScroll() or 0)
  QD.updateDisenchantButtonAction()

  QD.mainUI.titleText:SetText(string.format("可分解装备 (%d)", #selectedItems))
end

-- 刷新候选窗口内容与计数信息。
function QD.refreshCandidateWindow()
  QD.ensureCandidateWindow()
  QD.updateFilterButtonRow(QD.candidateUI)

  local filteredItems = QD.getFilteredAllItems()
  local total = #filteredItems
  local selectedCount = 0
  local whitelistCount = 0
  for _, item in ipairs(filteredItems) do
    if QD.state.selectedKeys[item.key] then
      selectedCount = selectedCount + 1
    end
    if QD.isItemWhitelisted(item) then
      whitelistCount = whitelistCount + 1
    end
  end

  QD.renderGrid(QD.candidateUI, filteredItems, QD.onCandidateItemClick, function(item)
    return (QD.state.selectedKeys[item.key] or QD.isItemWhitelisted(item)) and true or false
  end, function(item)
    return QD.isItemWhitelisted(item)
  end)

  local availableCount = total - selectedCount - whitelistCount
  if availableCount < 0 then
    availableCount = 0
  end
  QD.candidateUI.titleText:SetText(string.format("可添加装备 (%d/%d) 白名单:%d", availableCount, total, whitelistCount))
end

-- 刷新当前可见的插件窗口。
function QD.refreshWindows()
  QD.updateFilterButtonRow(QD.mainUI)
  QD.updateFilterButtonRow(QD.candidateUI)

  if QD.mainUI.frame and QD.mainUI.frame:IsShown() then
    QD.refreshMainWindow()
  end

  if QD.candidateUI.frame and QD.candidateUI.frame:IsShown() then
    QD.refreshCandidateWindow()
  end
end

-- 切换候选窗口显示，并将其定位到主窗口右侧。
function QD.toggleCandidateWindow()
  if not QD.mainUI.frame or not QD.mainUI.frame:IsShown() then
    return
  end

  QD.ensureCandidateWindow()

  if QD.candidateUI.frame:IsShown() then
    QD.candidateUI.frame:Hide()
    return
  end

  QD.candidateUI.frame:ClearAllPoints()
  QD.candidateUI.frame:SetPoint("TOPLEFT", QD.mainUI.frame, "TOPRIGHT", 12, 0)
  QD.refreshCandidateWindow()
  QD.applyClampedScroll(QD.candidateUI, 0)
  QD.candidateUI.frame:Show()
end
