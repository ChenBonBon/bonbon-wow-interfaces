local addonFrame = CreateFrame("Frame")
addonFrame:RegisterEvent("PLAYER_LOGIN")

local function getBagRangeEnd()
  return NUM_TOTAL_EQUIPPED_BAG_SLOTS or NUM_BAG_SLOTS or 4
end

local function collectBagSlotTotals()
  local totalSlots = 0
  local freeSlots = 0
  local bagEnd = getBagRangeEnd()

  for bagID = 0, bagEnd do
    local bagSlots = C_Container.GetContainerNumSlots(bagID) or 0
    local bagFreeSlots = C_Container.GetContainerNumFreeSlots(bagID) or 0
    totalSlots = totalSlots + bagSlots
    freeSlots = freeSlots + bagFreeSlots
  end

  return totalSlots, freeSlots
end

addonFrame:SetScript("OnEvent", function(_, event)
  if event ~= "PLAYER_LOGIN" then
    return
  end

  local totalSlots, freeSlots = collectBagSlotTotals()
  print(string.format("[BagSlotCounter] 总格子: %d, 空格子: %d", totalSlots, freeSlots))
end)
