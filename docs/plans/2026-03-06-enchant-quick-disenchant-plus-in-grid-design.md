# Enchant Quick Disenchant Plus-In-Grid Design

## Scope
Move the `+` control from header area into the main grid so it always occupies the next slot after currently selected items.

Rule:
- If selected item count is `n`, plus button appears at grid index `n + 1`.

No behavior change for remove/add logic.

## Behavior
- Main grid items still show selected items only.
- Plus button rendered in-grid at index `#selected + 1`.
- Clicking plus toggles candidate window as before.
- Candidate window logic unchanged.

## Layout
- Grid remains 3 columns with scroll support.
- Position formula reused for both items and plus slot:
  - `column = (index - 1) % 3`
  - `row = floor((index - 1) / 3)`
- Content height now based on `#selected + 1` slots.

## Edge Cases
- `n = 0`: plus is first slot.
- `n = 8`: plus is slot 9 (row 3 col 3).
- `n = 10`: plus is slot 11 (row 4 col 2).
- Plus stays visible even when no selected items.

## Validation
1. Verify plus at slot `n+1` for several counts.
2. Verify plus click still opens/closes candidate window.
3. Verify remove/add updates plus position immediately.
4. Verify scrolling behavior when `n+1 > 9`.
