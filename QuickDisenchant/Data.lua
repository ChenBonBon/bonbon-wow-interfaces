-- 数据模块：法术检测、背包扫描、选择集辅助与失败原因分类。
local _, QD = ...
QD = QD or _G.QuickDisenchantNS
if not QD then
  return
end

-- 将窗口注册到 UISpecialFrames，使 ESC 可关闭窗口。
function QD.registerEscClosableFrame(frame)
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

-- 判断角色是否已学习分解技能。
function QD.hasDisenchantSpell()
  if C_SpellBook and C_SpellBook.IsSpellKnown then
    return C_SpellBook.IsSpellKnown(QD.DISENCHANT_SPELL_ID) and true or false
  end

  if IsSpellKnownOrOverridesKnown then
    return IsSpellKnownOrOverridesKnown(QD.DISENCHANT_SPELL_ID) and true or false
  end

  if IsSpellKnown then
    return IsSpellKnown(QD.DISENCHANT_SPELL_ID) and true or false
  end

  if IsPlayerSpell then
    return IsPlayerSpell(QD.DISENCHANT_SPELL_ID) and true or false
  end

  return false
end

-- 判断是否为玩家分解施法相关事件。
function QD.isDisenchantSpellcastEvent(unit, spellID)
  return unit == "player" and spellID == QD.DISENCHANT_SPELL_ID
end

-- 获取需要扫描的最高背包索引。
function QD.getBagRangeEnd()
  return NUM_TOTAL_EQUIPPED_BAG_SLOTS or NUM_BAG_SLOTS or 4
end

-- 基于背包格子获取物品 GUID（优先使用 C_Item.GetItemGUID）。
function QD.getBagSlotItemGUID(bagID, slotID)
  if not C_Item or not C_Item.GetItemGUID then
    return nil
  end

  if ItemLocation and ItemLocation.CreateFromBagAndSlot then
    local itemLocation = ItemLocation:CreateFromBagAndSlot(bagID, slotID)
    if itemLocation and itemLocation.IsValid and itemLocation:IsValid() then
      local itemGUID = C_Item.GetItemGUID(itemLocation)
      if itemGUID and itemGUID ~= "" then
        return itemGUID
      end
    end
  end

  return nil
end

-- 静态规则：判断物品是否符合分解候选条件。
function QD.isDisenchantableByRules(itemLink, quality)
  if not itemLink or not IsEquippableItem(itemLink) then
    return false
  end

  if quality < QD.QUALITY_UNCOMMON or quality > QD.QUALITY_EPIC then
    return false
  end

  local _, _, _, itemEquipLoc, _, itemClassID = C_Item.GetItemInfoInstant(itemLink)
  if not itemEquipLoc or itemEquipLoc == "" then
    return false
  end

  if itemClassID ~= QD.ITEM_CLASS_ARMOR and itemClassID ~= QD.ITEM_CLASS_WEAPON and itemClassID ~= QD.ITEM_CLASS_PROFESSION then
    return false
  end

  return true
end

-- 扫描当前背包，返回可分解列表和按 key 索引的映射。
function QD.collectDisenchantableItems()
  local items = {}
  local itemsByKey = {}

  for bagID = 0, QD.getBagRangeEnd() do
    local slots = C_Container.GetContainerNumSlots(bagID) or 0

    for slotID = 1, slots do
      local itemInfo = C_Container.GetContainerItemInfo(bagID, slotID)
      if itemInfo and itemInfo.hyperlink then
        local quality = itemInfo.quality or 0
        if QD.isDisenchantableByRules(itemInfo.hyperlink, quality) then
          local itemID = itemInfo.itemID
          if not itemID and C_Item and C_Item.GetItemInfoInstant then
            itemID = C_Item.GetItemInfoInstant(itemInfo.hyperlink)
          end

          local key = string.format("%d:%d", bagID, slotID)
          local itemData = {
            key = key,
            bagID = bagID,
            slotID = slotID,
            itemID = itemID,
            itemGUID = QD.getBagSlotItemGUID(bagID, slotID),
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

-- 判断指定物品是否命中白名单。
function QD.isItemWhitelisted(item)
  if not item or not item.itemGUID then
    return false
  end

  return QD.state.whitelistByGUID[item.itemGUID] and true or false
end

-- 切换某件物品的白名单状态，返回切换后是否在白名单中。
function QD.toggleWhitelistForItem(item)
  if not item or not item.itemGUID then
    return false
  end

  if QD.state.whitelistByGUID[item.itemGUID] then
    QD.state.whitelistByGUID[item.itemGUID] = nil
    return false
  end

  QD.state.whitelistByGUID[item.itemGUID] = true
  return true
end

-- 按 allItems 顺序返回当前已选中的物品列表。
function QD.getSelectedItems()
  local selectedItems = {}

  for _, item in ipairs(QD.state.allItems) do
    if QD.state.selectedKeys[item.key] then
      table.insert(selectedItems, item)
    end
  end

  return selectedItems
end

-- 重新扫描背包，并仅保留仍然有效的已选 key。
function QD.syncSelectionWithCurrentBags()
  local items, itemsByKey = QD.collectDisenchantableItems()
  local newSelectedKeys = {}

  for key in pairs(QD.state.selectedKeys) do
    local item = itemsByKey[key]
    if item and not QD.isItemWhitelisted(item) then
      newSelectedKeys[key] = true
    end
  end

  QD.state.allItems = items
  QD.state.allItemsByKey = itemsByKey
  QD.state.selectedKeys = newSelectedKeys
end

-- 返回当前单步分解队列的队首物品。
function QD.getQueueHeadItem()
  local selectedItems = QD.getSelectedItems()
  return selectedItems[1]
end

-- 将当前扫描到的物品全部标记为已选中。
function QD.resetSelectionToAllItems()
  QD.state.selectedKeys = {}

  for _, item in ipairs(QD.state.allItems) do
    if not QD.isItemWhitelisted(item) then
      QD.state.selectedKeys[item.key] = true
    end
  end
end

-- 判断待处理物品在原背包格子里是否仍未变化。
function QD.isPendingItemUnchanged(pending)
  if not pending then
    return false
  end

  local currentInfo = C_Container.GetContainerItemInfo(pending.bagID, pending.slotID)
  return currentInfo and currentInfo.hyperlink == pending.itemLink
end

-- 根据本地化错误文案识别“附魔技能不足”失败。
function QD.isDisenchantSkillInsufficientFailure(pending)
  if not pending or type(pending.errorText) ~= "string" or pending.errorText == "" then
    return false
  end

  local errorText = pending.errorText
  local skillPatterns = {
    "附魔技能不足",
    "附魔技能太低",
    "附魔等级不足",
    "附魔等级太低",
    "需要更高的附魔",
    "不足以分解",
  }

  for _, pattern in ipairs(skillPatterns) do
    if string.find(errorText, pattern, 1, true) then
      return true
    end
  end

  return false
end

-- 基于施法状态与错误文案生成面向用户的失败原因。
function QD.buildDisenchantFailureReason(pending)
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
    return string.format("施法尚未完成（%.1f 秒内无结果）。", QD.DISENCHANT_RESOLVE_TIMEOUT_SECONDS)
  end

  if pending.castState == "succeeded" then
    return "施法完成但目标物品未变化，可能该装备当前不可分解。"
  end

  if pending.castState == "stopped" then
    return "施法已停止。"
  end

  return "未进入可用的分解施法状态。"
end
