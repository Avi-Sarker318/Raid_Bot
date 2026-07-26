"""Ghastly Conspiracy Raid — metadata + assembly (the RAID dict the
bot loads). Game-plan content lives in the plan/ package; this imports it.
The loader looks for this file (data.py) in every raid folder.
"""
from .plan import *  # noqa: F401,F403  (all FIGHT_*, DICE, DECKS, caps…)
from .plan import (
    DICE, DECKS, DECK_SLOTS, SCHOOLS, DECK_NOTES, DUOS, CHEATS_2V2,
    STAT_CAPS, OFF_SCHOOL, OFF_COLS, MAIN_FIELDS,
    FIGHT_DICE, FIGHT_FOLDERS, FIGHT_SOLO, FIGHT_AUTOMATION,
    FIGHT_2V2, FIGHT_TOUCH, FIGHT_GHASTLY_R, FIGHT_COINS,
    FIGHT_LAZERS, FIGHT_QUARTERMANE, FIGHT_4V4, FIGHT_RED_HERRING,
    FIGHT_GHASTLY_L)
from .gear.loader import GEAR as GEAR_GUIDES

# ---- metadata ----
NAME = 'Ghastly Conspiracy Raid'
AVAILABLE = True
LEVEL = 170
PLAYERS = 8
CREDIT = 'Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild'
DURATION_OPTIONS = [1.5, 3]
MAP_IMAGE = 'ghastly_map.png'
GEAR_FOLDER = "ghastly"          # gear lives in Gear/ghastly/

from scheduling.views.formats.ghastly_format import ROLES  # single source of truth

# ---- assembly ----
RIGHT_FIGHT_ORDER = ["dice", "folders", "solo", "automation", "2v2",
                     "touch", "ghastly-r"]
LEFT_FIGHT_ORDER = ["coins", "lazers", "quartermane", "4v4", "touch",
                    "red-herring", "ghastly-l"]

FIGHTS = {
    "dice": FIGHT_DICE,
    "folders": FIGHT_FOLDERS,
    "solo": FIGHT_SOLO,
    "automation": FIGHT_AUTOMATION,
    "2v2": FIGHT_2V2,
    "touch": FIGHT_TOUCH,
    "ghastly-r": FIGHT_GHASTLY_R,
    "coins": FIGHT_COINS,
    "lazers": FIGHT_LAZERS,
    "quartermane": FIGHT_QUARTERMANE,
    "4v4": FIGHT_4V4,
    "red-herring": FIGHT_RED_HERRING,
    "ghastly-l": FIGHT_GHASTLY_L,
}

RAID = {
    "name": NAME, "available": AVAILABLE, "level": LEVEL,
    "players": PLAYERS, "credit": CREDIT,
    "duration_options": DURATION_OPTIONS, "map_image": MAP_IMAGE,
    "gear_folder": GEAR_FOLDER, "roles": ROLES,
    "decks_right": DECKS, "dice": DICE,
    "duos": DUOS, "cheats_2v2": CHEATS_2V2,
    "fights_right": RIGHT_FIGHT_ORDER,
    "left_deck_slots": DECK_SLOTS, "left_schools": SCHOOLS,
    "left_deck_notes": DECK_NOTES, "fights_left": LEFT_FIGHT_ORDER,
    "stat_caps": STAT_CAPS, "off_school": OFF_SCHOOL,
    "off_cols": OFF_COLS, "main_fields": MAIN_FIELDS,
    "fights": FIGHTS,
    "gear": GEAR_GUIDES,
}
