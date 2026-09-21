"""Blighted Veil Raid — metadata + assembly (the RAID dict the bot loads).

Game-plan content lives in plan/ (overview, Outside team, Strategy 1/2) and
gear guides in gear/. The loader looks for this file (data.py) in every raid
folder.
"""
from .plan import *  # noqa: F401,F403
from .plan import (
    OUTSIDE_PLAYERS, INSIDE_NOTE, RAID_FLOW, EFFECT_SCHOOLS, CALLOUT_HOW,
    CALLOUT_EXAMPLES, SWAP_RULES, DRYAD_KEY, DRYADS, MAPS, SCHOOL_EMOJI,
    ONI_NAMES, ABBREVIATIONS, ONIS_INTRO, ROOTS_INTRO, WISPS, SHRINES, BOMB_CHAIN, TORII_GATES,
    TORII_HOW, BUTTONS, SWAPS, DOOR_INTRO, DOOR_LOGIC, WRONG_ESSENCE,
    MOB_REASON, PLAYERS, FINAL_HOW, STRATEGIES)
from .gear.loader import GEAR as GEAR_GUIDES

# ---- metadata ----
NAME = "Blighted Veil Raid"
AVAILABLE = True
LEVEL = 170
PLAYERS_COUNT = 8
CREDIT = ("Combat guide by Roaring Raptors & Battling Giraffes • "
          "Template by Major")
DURATION_OPTIONS = [1.5, 3]

from scheduling.views.formats.veil_format import ROLES  # single source of truth

# ---- assembly ----
RAID = {
    "name": NAME, "available": AVAILABLE, "level": LEVEL,
    "players": PLAYERS_COUNT, "credit": CREDIT,
    "duration_options": DURATION_OPTIONS, "map_image": None,
    "gear_folder": None, "roles": ROLES,
    # Ghastly-style keys stay empty — Blighted Veil has its own layout and
    # its own /guide screens (commands/guide/bvr_nav.py).
    "decks_right": {}, "dice": {}, "duos": {}, "cheats_2v2": "",
    "fights_right": [], "left_deck_slots": [], "left_schools": {},
    "left_deck_notes": "", "fights_left": [],
    "stat_caps": {}, "off_school": {}, "off_cols": [], "main_fields": [],
    "fights": {},
    # ---- Blighted Veil guide content ----
    "guide": "bvr",
    "outside_players": OUTSIDE_PLAYERS,
    "inside_note": INSIDE_NOTE,
    "raid_flow": RAID_FLOW,
    "strategies": STRATEGIES,
    "effect_schools": EFFECT_SCHOOLS,
    "callout_how": CALLOUT_HOW,
    "callout_examples": CALLOUT_EXAMPLES,
    "swap_rules": SWAP_RULES,
    "dryad_key": DRYAD_KEY,
    "dryads": DRYADS,
    "maps": MAPS,
    "school_emoji": SCHOOL_EMOJI,
    "oni_names": ONI_NAMES,
    "abbreviations": ABBREVIATIONS,
    "onis_intro": ONIS_INTRO,
    "roots_intro": ROOTS_INTRO,
    "outside": {
        "wisps": WISPS, "shrines": SHRINES, "bomb_chain": BOMB_CHAIN,
        "torii_gates": TORII_GATES, "torii_how": TORII_HOW,
        "buttons": BUTTONS, "swaps": SWAPS, "door_intro": DOOR_INTRO,
        "door_logic": DOOR_LOGIC, "wrong_essence": WRONG_ESSENCE,
        "mob_reason": MOB_REASON, "players": PLAYERS,
        "final_how": FINAL_HOW,
    },
    "gear": GEAR_GUIDES,
}
