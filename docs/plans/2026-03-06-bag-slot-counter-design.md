# Bag Slot Counter Design

## Scope
Build a World of Warcraft (Retail CN, interface 120001) addon that prints two numbers to chat once at login:
- Total bag slots
- Total free bag slots

No UI panel, no slash command, no persistent storage.

## API and Data Source
- Use `C_Container.GetContainerNumSlots(bagID)` for slot count per bag.
- Use `C_Container.GetContainerNumFreeSlots(bagID)` for free slots per bag.
- Iterate bag IDs from `0` to `NUM_TOTAL_EQUIPPED_BAG_SLOTS` to include backpack, regular equipped bags, and reagent bag slot when present.

## Trigger
- Register `PLAYER_LOGIN` and run once.

## Output
- Print one chat line in Chinese with both values.
