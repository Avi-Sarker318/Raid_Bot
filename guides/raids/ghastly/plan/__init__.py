"""Ghastly Conspiracy Raid — game plan content.

This used to be one 554-line gameplan.py. It's now split by topic:

    plan/
      stat_caps.py      MAIN_FIELDS, OFF_COLS, STAT_CAPS, OFF_SCHOOL
      decks.py          DECKS, DECK_SLOTS, SCHOOLS, DECK_NOTES
      dice.py           DICE, FIGHT_DICE
      two_v_two.py      CHEATS_2V2, DUOS, FIGHT_2V2
      fights_right.py   FIGHT_FOLDERS, FIGHT_SOLO, FIGHT_AUTOMATION,
                        FIGHT_GHASTLY_R
      fights_left.py    FIGHT_COINS, FIGHT_LAZERS, FIGHT_QUARTERMANE,
                        FIGHT_4V4, FIGHT_RED_HERRING, FIGHT_GHASTLY_L
      fights_shared.py  FIGHT_TOUCH  (both sides run it)

Everything is re-exported here, so `from .plan import *` or
`from .plan import DICE` behave exactly like the old single file did.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""
from .stat_caps import MAIN_FIELDS, OFF_COLS, STAT_CAPS, OFF_SCHOOL
from .decks import DECKS, DECK_SLOTS, SCHOOLS, DECK_NOTES
from .dice import DICE, FIGHT_DICE
from .two_v_two import CHEATS_2V2, DUOS, FIGHT_2V2
from .fights_right import (
    FIGHT_FOLDERS, FIGHT_SOLO, FIGHT_AUTOMATION, FIGHT_GHASTLY_R)
from .fights_left import (
    FIGHT_COINS, FIGHT_LAZERS, FIGHT_QUARTERMANE, FIGHT_4V4,
    FIGHT_RED_HERRING, FIGHT_GHASTLY_L)
from .fights_shared import FIGHT_TOUCH

__all__ = [
    "MAIN_FIELDS", "OFF_COLS", "STAT_CAPS", "OFF_SCHOOL",
    "DECKS", "DECK_SLOTS", "SCHOOLS", "DECK_NOTES",
    "DICE", "FIGHT_DICE",
    "CHEATS_2V2", "DUOS", "FIGHT_2V2",
    "FIGHT_FOLDERS", "FIGHT_SOLO", "FIGHT_AUTOMATION", "FIGHT_GHASTLY_R",
    "FIGHT_COINS", "FIGHT_LAZERS", "FIGHT_QUARTERMANE", "FIGHT_4V4",
    "FIGHT_RED_HERRING", "FIGHT_GHASTLY_L",
    "FIGHT_TOUCH",
]
