# Enchant Quick Disenchant Design

## Scope
Build a standalone WoW addon `EnchantQuickDisenchant` for CN Retail (`Interface 120001`) that runs on login.

Behavior:
- If the player has not learned current-version enchanting (user term: 至暗之夜附魔), print nothing.
- If learned, print:
  - Total bag slots
  - Total free bag slots
  - Total count of disenchantable items in current bags only
  - Breakdown by quality (green/blue/purple/orange)

`BagSlotCounter` remains unchanged.

## Trigger and Boundaries
- Event: `PLAYER_LOGIN`, run once per login.
- Bag range: `bagID = 0..NUM_TOTAL_EQUIPPED_BAG_SLOTS`.
- No bank/reagent bank/warband bank traversal.

## Profession Gate
Use profession APIs to detect enchanting profession ownership as the practical gate for current-version enchanting on Retail:
- Read profession slots via `GetProfessions()` and `GetProfessionInfo(index)`.
- Detect enchanting by `skillLine == 333`.
- If gate fails: return without output.

## Disenchantable Item Detection
- Iterate each bag slot with `C_Container.GetContainerItemInfo`.
- Keep only equippable items with quality `>= Enum.ItemQuality.Uncommon`.
- Use hidden `GameTooltip` scan on bag item to detect localized disenchant hint (`"可分解"`).
- Count qualifying items by quality.

## Output
Single summary line plus optional quality-detail line:
- `[EnchantQuickDisenchant] 总格子: X, 空格子: Y, 可分解总数: Z`
- `[EnchantQuickDisenchant] 绿色: a, 蓝色: b, 紫色: c, 橙色: d` (only qualities with count > 0)

## Error Handling
- Nil-safe numeric fallback (`or 0`) on bag APIs.
- Missing item link or tooltip text treated as non-qualifying.
- Any unavailable API path degrades gracefully (no Lua error).

## Validation
Game-side checks:
1. Character without enchanting: no output.
2. Character with enchanting and known DE items: totals and quality split match expected.
3. Character with enchanting but no DE items: `可分解总数: 0`, no quality line.
