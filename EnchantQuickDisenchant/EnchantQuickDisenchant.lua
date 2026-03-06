local ADDON_PREFIX = "[EnchantQuickDisenchant]"
local MIDNIGHT_ENCHANTING_SKILL_LINE_ID = 2909
local ENCHANTING_PROFESSION_SKILL_LINE_ID = 333
local ENCHANTING_PROFESSION_ENUM_ID = Enum and Enum.Profession and Enum.Profession.Enchanting or nil

local QUALITY_UNCOMMON = (Enum and Enum.ItemQuality and Enum.ItemQuality.Uncommon) or 2
local QUALITY_RARE = (Enum and Enum.ItemQuality and Enum.ItemQuality.Rare) or 3
local QUALITY_EPIC = (Enum and Enum.ItemQuality and Enum.ItemQuality.Epic) or 4
local QUALITY_LEGENDARY = (Enum and Enum.ItemQuality and Enum.ItemQuality.Legendary) or 5

local DISENCHANT_HINTS = {
  "可分解",
  "分解",
}

local QUALITY_LABELS = {
  [QUALITY_UNCOMMON] = "绿色",
  [QUALITY_RARE] = "蓝色",
  [QUALITY_EPIC] = "紫色",
  [QUALITY_LEGENDARY] = "橙色",
}

local function containsDisenchantHint(text)
  if type(text) ~= "string" or text == "" then
    return false
  end

  for _, hint in ipairs(DISENCHANT_HINTS) do
    if text:find(hint, 1, true) then
      return true
    end
  end

  return false
end

local function hasBaseEnchantingProfession()
  local professionSlots = { GetProfessions() }

  for _, professionIndex in ipairs(professionSlots) do
    if professionIndex then
      local _, _, _, _, _, _, skillLine = GetProfessionInfo(professionIndex)
      if skillLine == ENCHANTING_PROFESSION_SKILL_LINE_ID then
        return true
      end
    end
  end

  return false
end

local function hasCurrentVersionEnchanting()
  if not hasBaseEnchantingProfession() then
    return false
  end

  if not C_TradeSkillUI or not C_TradeSkillUI.GetProfessionInfoBySkillLineID then
    return true
  end

  local professionInfo = C_TradeSkillUI.GetProfessionInfoBySkillLineID(MIDNIGHT_ENCHANTING_SKILL_LINE_ID)
  if professionInfo and (professionInfo.skillLevel or 0) > 0 then
    return true
  end

  if C_TradeSkillUI.GetAllProfessionTradeSkillLines and C_TradeSkillUI.GetTradeSkillDisplayName then
    local skillLineIDs = C_TradeSkillUI.GetAllProfessionTradeSkillLines() or {}
    for _, skillLineID in ipairs(skillLineIDs) do
      local skillInfo = C_TradeSkillUI.GetProfessionInfoBySkillLineID(skillLineID)
      if skillInfo and (skillInfo.skillLevel or 0) > 0 then
        local displayName = C_TradeSkillUI.GetTradeSkillDisplayName(skillLineID)
        if type(displayName) == "string" and (displayName:find("至暗之夜", 1, true) or displayName:find("Midnight", 1, true)) then
          local parentSkillLine = skillInfo.parentProfessionID or skillInfo.parentProfessionSkillLineID
          if parentSkillLine == ENCHANTING_PROFESSION_SKILL_LINE_ID or (ENCHANTING_PROFESSION_ENUM_ID and skillInfo.profession == ENCHANTING_PROFESSION_ENUM_ID) then
            return true
          end
        end
      end
    end
  end

  return false
end

local function getBagRangeEnd()
  return NUM_TOTAL_EQUIPPED_BAG_SLOTS or NUM_BAG_SLOTS or 4
end

local function collectBagSlotTotals()
  local totalSlots = 0
  local freeSlots = 0

  for bagID = 0, getBagRangeEnd() do
    totalSlots = totalSlots + (C_Container.GetContainerNumSlots(bagID) or 0)
    freeSlots = freeSlots + (C_Container.GetContainerNumFreeSlots(bagID) or 0)
  end

  return totalSlots, freeSlots
end

local function isTooltipDisenchantableByDataLines(bagID, slotID)
  if not C_TooltipInfo or not C_TooltipInfo.GetBagItem then
    return false
  end

  local tooltipData = C_TooltipInfo.GetBagItem(bagID, slotID)
  if not tooltipData or not tooltipData.lines then
    return false
  end

  for _, line in ipairs(tooltipData.lines) do
    if containsDisenchantHint(line.leftText) or containsDisenchantHint(line.rightText) or containsDisenchantHint(line.text) then
      return true
    end
  end

  return false
end

local scanTooltip = CreateFrame("GameTooltip", "EnchantQuickDisenchantScanTooltip", UIParent, "GameTooltipTemplate")
scanTooltip:SetOwner(UIParent, "ANCHOR_NONE")

local function isTooltipDisenchantableByGameTooltip(bagID, slotID)
  scanTooltip:ClearLines()
  scanTooltip:SetBagItem(bagID, slotID)

  for i = 1, scanTooltip:NumLines() do
    local leftLine = _G["EnchantQuickDisenchantScanTooltipTextLeft" .. i]
    local rightLine = _G["EnchantQuickDisenchantScanTooltipTextRight" .. i]

    if containsDisenchantHint(leftLine and leftLine:GetText()) or containsDisenchantHint(rightLine and rightLine:GetText()) then
      return true
    end
  end

  return false
end

local function isDisenchantableBagItem(bagID, slotID, itemLink)
  if not itemLink or not IsEquippableItem(itemLink) then
    return false
  end

  if isTooltipDisenchantableByDataLines(bagID, slotID) then
    return true
  end

  return isTooltipDisenchantableByGameTooltip(bagID, slotID)
end

local function collectDisenchantableCountsByQuality()
  local totalCount = 0
  local qualityCounts = {
    [QUALITY_UNCOMMON] = 0,
    [QUALITY_RARE] = 0,
    [QUALITY_EPIC] = 0,
    [QUALITY_LEGENDARY] = 0,
  }

  for bagID = 0, getBagRangeEnd() do
    local slots = C_Container.GetContainerNumSlots(bagID) or 0

    for slotID = 1, slots do
      local itemInfo = C_Container.GetContainerItemInfo(bagID, slotID)
      if itemInfo and itemInfo.hyperlink then
        local quality = itemInfo.quality or 0
        if quality >= QUALITY_UNCOMMON and isDisenchantableBagItem(bagID, slotID, itemInfo.hyperlink) then
          local count = itemInfo.stackCount or 1
          totalCount = totalCount + count

          if qualityCounts[quality] ~= nil then
            qualityCounts[quality] = qualityCounts[quality] + count
          end
        end
      end
    end
  end

  return totalCount, qualityCounts
end

local function buildQualityBreakdown(qualityCounts)
  local orderedQualities = {
    QUALITY_UNCOMMON,
    QUALITY_RARE,
    QUALITY_EPIC,
    QUALITY_LEGENDARY,
  }

  local parts = {}

  for _, quality in ipairs(orderedQualities) do
    local count = qualityCounts[quality] or 0
    if count > 0 then
      table.insert(parts, string.format("%s: %d", QUALITY_LABELS[quality], count))
    end
  end

  return table.concat(parts, ", ")
end

local function runScan()
  if not hasCurrentVersionEnchanting() then
    print(string.format("%s 未学习至暗之夜附魔。", ADDON_PREFIX))
    return
  end

  local totalSlots, freeSlots = collectBagSlotTotals()
  local totalDisenchantable, qualityCounts = collectDisenchantableCountsByQuality()

  print(string.format("%s 总格子: %d, 空格子: %d, 可分解总数: %d", ADDON_PREFIX, totalSlots, freeSlots, totalDisenchantable))

  local qualityBreakdown = buildQualityBreakdown(qualityCounts)
  if qualityBreakdown ~= "" then
    print(string.format("%s %s", ADDON_PREFIX, qualityBreakdown))
  end
end

SLASH_EQD1 = "/eqd"
SlashCmdList["EQD"] = function()
  runScan()
end
