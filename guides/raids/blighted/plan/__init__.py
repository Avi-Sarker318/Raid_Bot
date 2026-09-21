"""Blighted Veil Raid — guide content, split by topic.

    plan/
      overview.py    team layout, callouts, dryad table, maps
      outside.py     Outside team (wisps, shrines, gates, N/E/S/W players)
      strategy_1.py  Inside team — Strategy 1 (most used)
      strategy_2.py  Inside team — Strategy 2

Everything is re-exported here, so `from .plan import *` works like the
Ghastly plan package.

Guide by Roaring Raptors & Battling Giraffes — template by Major
"""
from .overview import (
    OUTSIDE_PLAYERS, INSIDE_NOTE, RAID_FLOW, EFFECT_SCHOOLS, CALLOUT_HOW,
    CALLOUT_EXAMPLES, SWAP_RULES, DRYAD_KEY, DRYADS, MAPS, SCHOOL_EMOJI,
    ONI_NAMES, ABBREVIATIONS, ONIS_INTRO, ROOTS_INTRO)
from .outside import (
    WISPS, SHRINES, BOMB_CHAIN, TORII_GATES, TORII_HOW, BUTTONS, SWAPS,
    DOOR_INTRO, DOOR_LOGIC, WRONG_ESSENCE, MOB_REASON, PLAYERS, FINAL_HOW)
from .strategy_1 import STRATEGY_1
from .strategy_2 import STRATEGY_2

STRATEGIES = {"1": STRATEGY_1, "2": STRATEGY_2}

__all__ = [
    "OUTSIDE_PLAYERS", "INSIDE_NOTE", "RAID_FLOW", "EFFECT_SCHOOLS",
    "CALLOUT_HOW", "CALLOUT_EXAMPLES", "SWAP_RULES", "DRYAD_KEY", "DRYADS",
    "MAPS", "SCHOOL_EMOJI", "ONI_NAMES", "ABBREVIATIONS", "ONIS_INTRO",
    "ROOTS_INTRO",
    "WISPS", "SHRINES", "BOMB_CHAIN", "TORII_GATES", "TORII_HOW", "BUTTONS",
    "SWAPS", "DOOR_INTRO", "DOOR_LOGIC", "WRONG_ESSENCE", "MOB_REASON",
    "PLAYERS", "FINAL_HOW", "STRATEGY_1", "STRATEGY_2", "STRATEGIES",
]
