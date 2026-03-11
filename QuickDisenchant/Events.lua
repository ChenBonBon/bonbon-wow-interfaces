-- 事件模块：扫描入口、事件驱动的待分解追踪与斜杠命令绑定。
local _, QD = ...
QD = QD or _G.QuickDisenchantNS
if not QD then
  return
end

-- 执行一次全量背包扫描，重置选中项并打开主窗口。
function QD.runScan()
  if QD.bindSavedVariables then
    QD.bindSavedVariables()
  end

  if not QD.hasDisenchantSpell or not QD.hasDisenchantSpell() then
    if QD.mainUI.frame then
      QD.mainUI.frame:Hide()
    end
    if QD.candidateUI.frame then
      QD.candidateUI.frame:Hide()
    end
    print(string.format("%s 未学习分解技能。", QD.ADDON_PREFIX))
    return
  end

  local items, itemsByKey = QD.collectDisenchantableItems()
  QD.state.allItems = items
  QD.state.allItemsByKey = itemsByKey
  QD.state.pendingDisenchant = nil
  QD.resetSelectionToAllItems()

  QD.ensureMainWindow()
  QD.refreshMainWindow()
  QD.applyClampedScroll(QD.mainUI, 0)
  QD.mainUI.frame:Show()

  if QD.candidateUI.frame then
    QD.candidateUI.frame:Hide()
  end
end

-- 插件加载完成后重绑定持久化白名单，避免读取到初始化空表。
local addonLoadedFrame = CreateFrame("Frame")
addonLoadedFrame:RegisterEvent("ADDON_LOADED")
addonLoadedFrame:SetScript("OnEvent", function(_, _, addonName)
  if addonName ~= QD.ADDON_NAME then
    return
  end

  if QD.bindSavedVariables then
    QD.bindSavedVariables()
  end
end)

-- 处理用于分解结算的背包/施法/错误事件。
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
  local pending = QD.state.pendingDisenchant
  if not pending then
    return
  end

  if event == "BAG_UPDATE_DELAYED" then
    local unchanged = QD.isPendingItemUnchanged(pending)
    if not unchanged then
      QD.resolvePendingDisenchant()
      return
    end

    if pending.errorText or pending.castFailureEvent then
      QD.resolvePendingDisenchant()
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
  if not QD.isDisenchantSpellcastEvent(unit, spellID) then
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
    QD.resolvePendingDisenchant()
    return
  end
end)

-- 注册手动扫描命令并打开插件窗口。
SLASH_QD1 = "/qd"
SlashCmdList["QD"] = function()
  QD.runScan()
end
