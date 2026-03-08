-- UI module: window creation, grid rendering, and selection interactions.
local _, QD = ...
QD = QD or _G.QuickDisenchantNS
if not QD then
  return
end

-- Creates a standard framed window with title, scroll area, and empty text.
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

-- Lazily creates the main selection window and its action controls.
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

  scrollFrame:ClearAllPoints()
  scrollFrame:SetPoint("TOPLEFT", frame, "TOPLEFT", 12, -30)
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

  QD.mainUI.frame = frame
  QD.mainUI.titleText = titleText
  QD.mainUI.scrollFrame = scrollFrame
  QD.mainUI.contentFrame = contentFrame
  QD.mainUI.emptyText = emptyText
  QD.mainUI.gridPlusButton = plusButton
  QD.mainUI.disenchantButton = disenchantButton
end

-- Lazily creates the candidate list window.
function QD.ensureCandidateWindow()
  if QD.candidateUI.frame then
    return
  end

  local frame, titleText, scrollFrame, contentFrame, emptyText = QD.createWindowFrame("QuickDisenchantCandidateWindow")
  titleText:SetText("可添加装备")

  QD.candidateUI.frame = frame
  QD.candidateUI.titleText = titleText
  QD.candidateUI.scrollFrame = scrollFrame
  QD.candidateUI.contentFrame = contentFrame
  QD.candidateUI.emptyText = emptyText
end

-- Creates or returns a reusable grid icon button for an item cell.
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

-- Renders an item list into a target grid UI set.
function QD.renderGrid(uiSet, items, onClick, isDisabled)
  for index, item in ipairs(items) do
    local button = QD.ensureGridButton(uiSet, index, onClick)
    local column = (index - 1) % QD.COLUMNS
    local row = math.floor((index - 1) / QD.COLUMNS)
    local disabled = isDisabled and isDisabled(item) or false

    button:ClearAllPoints()
    button:SetPoint("TOPLEFT", uiSet.contentFrame, "TOPLEFT", column * (QD.ICON_SIZE + QD.ICON_GAP), -row * (QD.ICON_SIZE + QD.ICON_GAP))
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

  local rowCount = math.max(1, math.ceil(#items / QD.COLUMNS))
  local contentHeight = (rowCount * QD.ICON_SIZE) + ((rowCount - 1) * QD.ICON_GAP)
  uiSet.contentFrame:SetSize(QD.CONTENT_WIDTH, contentHeight)
  uiSet.emptyText:SetShown(#items == 0)
  uiSet.scrollFrame:SetVerticalScroll(0)
end

-- Removes an item from current selection when clicked in the main window.
function QD.onMainItemClick(self)
  if not self.itemKey or not QD.state.selectedKeys[self.itemKey] then
    return
  end

  QD.state.selectedKeys[self.itemKey] = nil
  QD.refreshWindows()
end

-- Adds an item into current selection when clicked in candidate window.
function QD.onCandidateItemClick(self)
  if not self.itemKey or self.isDisabled then
    return
  end

  if not QD.state.allItemsByKey[self.itemKey] then
    return
  end

  QD.state.selectedKeys[self.itemKey] = true
  QD.refreshWindows()
end

-- Renders main window title, grid, plus slot and action button state.
function QD.refreshMainWindow()
  QD.ensureMainWindow()

  local selectedItems = QD.getSelectedItems()
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
  QD.mainUI.scrollFrame:SetVerticalScroll(0)
  QD.updateDisenchantButtonAction()

  QD.mainUI.titleText:SetText(string.format("可分解装备 (%d)", #selectedItems))
end

-- Renders candidate window contents and selection counters.
function QD.refreshCandidateWindow()
  QD.ensureCandidateWindow()

  local total = #QD.state.allItems
  local selectedCount = 0
  for _, item in ipairs(QD.state.allItems) do
    if QD.state.selectedKeys[item.key] then
      selectedCount = selectedCount + 1
    end
  end

  QD.renderGrid(QD.candidateUI, QD.state.allItems, QD.onCandidateItemClick, function(item)
    return QD.state.selectedKeys[item.key] and true or false
  end)

  QD.candidateUI.titleText:SetText(string.format("可添加装备 (%d/%d)", total - selectedCount, total))
end

-- Refreshes any currently visible addon windows.
function QD.refreshWindows()
  if QD.mainUI.frame and QD.mainUI.frame:IsShown() then
    QD.refreshMainWindow()
  end

  if QD.candidateUI.frame and QD.candidateUI.frame:IsShown() then
    QD.refreshCandidateWindow()
  end
end

-- Toggles candidate window visibility and positions it beside the main window.
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
  QD.candidateUI.frame:Show()
end
