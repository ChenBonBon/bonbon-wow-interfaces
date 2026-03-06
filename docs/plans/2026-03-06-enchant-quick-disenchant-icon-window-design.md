# Enchant Quick Disenchant Icon Window Design

## Scope
Refactor `EnchantQuickDisenchant` so that:
- `/eqd` is the only trigger (already true)
- Remove bag total/free slot output
- Show a small UI window with all disenchantable items as icon-only cells
- Window layout: 3 columns x 3 visible rows, scroll when more than 9 items
- Tooltip appears when hovering each icon

## Trigger Behavior
- `/eqd` command executes scan
- If spell `7411` is not known: print a single chat hint and do not open window
- If known: refresh data and open window

## Data Model
Store scan result as array items with:
- `itemLink`
- `iconFileID`
- `quality`

Existing disenchant rule remains:
- Equippable item
- Item class armor or weapon
- Quality from uncommon to epic

## UI Structure
Single reusable frame tree created once:
- Main frame with title and close button
- ScrollFrame + scrollbar
- Content frame holding icon buttons in 3-column grid
- Empty-state font string when no items found

## Rendering Rules
- Icon size fixed, grid gaps fixed
- Position by index:
  - column = (index - 1) % 3
  - row = floor((index - 1) / 3)
- Content frame height set from row count
- Extra old buttons hidden during refresh

## Output Changes
- Remove summary chat line and quality breakdown chat line
- Keep only "not learned" hint message path

## Validation
1. `/eqd` without spell 7411: hint shown, window not shown.
2. `/eqd` with <= 9 items: all visible, no scrolling needed.
3. `/eqd` with > 9 items: scrolling reveals all icons.
4. Hover icon: tooltip shows item info.
5. Re-run `/eqd` after inventory change: grid updates correctly.
