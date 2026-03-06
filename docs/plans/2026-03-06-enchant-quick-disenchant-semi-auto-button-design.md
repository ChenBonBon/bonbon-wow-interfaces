# Enchant Quick Disenchant Semi-Auto Button Design

## Scope
Add a `分解` button at the bottom of the main window.

Behavior:
- One click processes at most one item
- Target item is the first item in current main-window order
- Auto performs spell cast + item use attempt
- On failure, keep the item selected and show hint
- On success, remove the item from selected list and refresh UI

## Constraints
WoW protected actions require hardware input. No simulated clicks or full automation.

## UI
- Main window adds bottom centered button: `分解`
- Candidate window unchanged
- Main close behavior unchanged

## Execution Flow
1. Click `分解`
2. Validate spell known and queue not empty
3. Pick queue head item
4. Cast disenchant spell, then use bag item
5. Store pending attempt state
6. Resolve by bag change or timeout:
   - item removed/changed => success
   - item still present => failure

## Feedback
- Success: `已尝试分解：<物品链接>`
- Failure: `分解失败，请确认距离、状态和技能可用。`
- Empty queue: `当前无可分解装备。`
- Missing spell: `未学习分解技能。`

## Validation
1. Button exists and is clickable.
2. Each click processes only one item.
3. Failure keeps item in list and shows message.
4. Success removes one item and refreshes windows.
5. Candidate window synchronization remains correct.
