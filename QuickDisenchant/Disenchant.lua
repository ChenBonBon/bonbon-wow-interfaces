-- 分解模块：处理待分解生命周期、安全宏配置与结果结算。
local _, QD = ...
QD = QD or _G.QuickDisenchantNS
if not QD then
  return
end

-- 开始一次待处理分解，并注册超时兜底结算。
function QD.beginPendingDisenchant(actionItem)
  if not actionItem then
    return
  end

  print(string.format("%s 正在分解：%s", QD.ADDON_PREFIX, actionItem.itemLink or "物品"))

  QD.state.pendingDisenchant = {
    key = actionItem.key,
    bagID = actionItem.bagID,
    slotID = actionItem.slotID,
    itemLink = actionItem.itemLink,
    castState = "queued",
    castFailureEvent = nil,
    errorText = nil,
  }

  local pendingRef = QD.state.pendingDisenchant
  C_Timer.After(QD.DISENCHANT_RESOLVE_TIMEOUT_SECONDS, function()
    if QD.state.pendingDisenchant == pendingRef then
      QD.resolvePendingDisenchant()
    end
  end)
end

-- 结算待处理分解结果（成功/失败）并同步更新选择列表。
function QD.resolvePendingDisenchant()
  local pending = QD.state.pendingDisenchant
  if not pending then
    return
  end

  QD.state.pendingDisenchant = nil

  local isSameItem = QD.isPendingItemUnchanged(pending)
  if isSameItem then
    if QD.isDisenchantSkillInsufficientFailure(pending) then
      QD.state.selectedKeys[pending.key] = nil
      QD.syncSelectionWithCurrentBags()
      QD.refreshWindows()
      print(string.format("%s 分解失败：附魔技能不足，已从列表移除：%s", QD.ADDON_PREFIX, pending.itemLink or "物品"))
      return
    end

    print(string.format("%s 分解失败：%s", QD.ADDON_PREFIX, QD.buildDisenchantFailureReason(pending)))
    QD.refreshWindows()
    return
  end

  QD.state.selectedKeys[pending.key] = nil
  QD.syncSelectionWithCurrentBags()
  QD.refreshWindows()
  print(string.format("%s 已尝试分解：%s", QD.ADDON_PREFIX, pending.itemLink or "物品"))
end

-- 刷新安全分解按钮的模式、宏属性和可用状态。
function QD.updateDisenchantButtonAction()
  if not QD.mainUI.disenchantButton then
    return
  end

  local button = QD.mainUI.disenchantButton
  local mode = "empty"
  local actionItem = nil

  if QD.state.pendingDisenchant then
    mode = "busy"
  elseif not QD.hasDisenchantSpell() then
    mode = "missing_spell"
  else
    actionItem = QD.getQueueHeadItem()
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
      local macrotext = string.format("/cast %s\n/use %d %d", QD.DISENCHANT_SPELL_NAME, actionItem.bagID, actionItem.slotID)

      button:SetAttribute("useOnKeyDown", false)
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
