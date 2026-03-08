-- Events module: scan entrypoint, event-driven pending tracking, and slash command binding.
local _, QD = ...
QD = QD or _G.QuickDisenchantNS
if not QD then
  return
end

-- Runs a fresh bag scan, resets selection to all candidates, and opens main window.
function QD.runScan()
  local items, itemsByKey = QD.collectDisenchantableItems()
  QD.state.allItems = items
  QD.state.allItemsByKey = itemsByKey
  QD.state.pendingDisenchant = nil
  QD.resetSelectionToAllItems()

  QD.ensureMainWindow()
  QD.refreshMainWindow()
  QD.mainUI.frame:Show()

  if QD.candidateUI.frame then
    QD.candidateUI.frame:Hide()
  end
end

-- Handles bag/spell/error events used to resolve pending disenchant actions.
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

-- Registers slash command to trigger manual scan and open addon UI.
SLASH_QD1 = "/qd"
SlashCmdList["QD"] = function()
  QD.runScan()
end
