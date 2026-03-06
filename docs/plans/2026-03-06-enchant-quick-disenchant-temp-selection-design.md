# Enchant Quick Disenchant Temporary Selection Interaction Design

## Scope
Add temporary interaction state to `EnchantQuickDisenchant`:
- Main window starts with all disenchantable bag items selected
- Left/right click an item in main window removes it from current session selection
- `+` button opens a right-side candidate window
- Candidate window shows all disenchantable bag items
- Candidate items already selected are greyed out and not clickable
- Removed items become clickable in candidate window and can be added back
- Closing main window closes candidate window

No persistence. State resets on each `/eqd` run.

## State Model
- `allItems`: array of all disenchantable items from current bag scan
- `allItemsByKey`: key-indexed map of scanned items
- `selectedKeys`: set-like table for currently selected items
- `itemKey`: runtime key based on bag slot (`bagID:slotID`)

On each `/eqd`:
1. rebuild `allItems` and `allItemsByKey`
2. reset `selectedKeys` to all keys selected

## UI Behavior
### Main Window
- Shows only selected items
- Supports left/right click remove
- Contains `+` button to toggle candidate window

### Candidate Window
- Anchored to right of main window
- Shows all items from `allItems`
- If key is selected: icon desaturated + reduced alpha + click disabled
- If key not selected: normal icon + click adds back into `selectedKeys`

## Synchronization
Single refresh pipeline:
- `refreshMainWindow()` renders selected items
- `refreshCandidateWindow()` renders all items with disabled state
- Any selection mutation triggers refresh of both visible windows

## Validation
1. `/eqd` opens main window with all items selected.
2. Opening candidate window initially shows all items disabled.
3. Removing item in main window enables same item in candidate window.
4. Clicking enabled candidate item adds it back and disables it again.
5. Closing main window also closes candidate window.
6. Running `/eqd` again resets to all-selected state.
