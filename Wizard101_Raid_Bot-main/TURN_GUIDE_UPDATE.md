# Interactive Turn Guide Update

This version keeps the original raid strategy data and adds a reusable Discord turn viewer.

## What changed

- Regular fights with turn tables now include a **Start Turn Guide** button.
- Dice pair plans and 2v2 plans also include a **Start Turn Guide** button.
- **Previous**, **Overview**, and **Next** update the same Discord message.
- Each page shows one existing turn, the role order, and each role's exact action.
- Multi-table fights automatically continue into the next existing table.
- Empty/None action cells display as an em dash rather than the word `None`.
- Storm uses purple visual markers. Other school marker colors follow the requested mapping when a school name is present.

## Preserved strategy corrections

- Automaton: Storm 1 → Storm 3 → Support → Storm 2.
- Ghastly Right: Support → Storm 3 → Storm 2 → Storm 1.

## Validation performed

- Python syntax compilation across the full project.
- Route generation checks for 109 turn pages.
- Checked regular, multi-table, Dice, and 2v2 navigation paths.
- Confirmed no strategy text was invented for the new viewer.
