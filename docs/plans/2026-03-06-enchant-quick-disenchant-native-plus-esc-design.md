# Enchant Quick Disenchant Native Plus and ESC Design

## Scope
Apply three updates:
1. Plus slot uses Blizzard native item-upgrade visual style
2. Main window title changes to `可分解装备`
3. Pressing `Esc` closes addon windows (main and candidate)

## Native Plus Style
Use Blizzard item-upgrade atlases:
- `itemupgrade_greenplusicon`
- `itemupgrade_greenplusicon_pressed`
- `itemupgrade_slotborder`
- `itemupgrade_fx_slotinnerglow`

Plus remains in-grid at `n+1` slot and keeps current toggle behavior.

## Title Changes
- Main window title: `可分解装备 (%d)`
- Candidate window title remains `可添加装备`.

## ESC Behavior
- Register main frame in `UISpecialFrames`.
- Existing main `OnHide` already hides candidate frame, so pressing `Esc` on main closes both windows.

## Validation
1. Plus visual style matches native item-upgrade look.
2. Main title shows `可分解装备` with count.
3. Pressing `Esc` closes main and candidate windows.
4. `/eqd` still reopens and functions normally.
