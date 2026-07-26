"""Blighted Veil Raid — schedulable now; full guide coming later.

Generic 8-player roles so it can be scheduled. When you have the real
comp and strategy, flip AVAILABLE to True and fill in the guide fields
(roles, fights, decks, stat_caps) the way ghastly/ does.
"""
from scheduling.views.formats.veil_format import ROLES
RAID = {
    "name": "Blighted Veil Raid",
    "available": False,          # guide gated until True; scheduling always works
    "level": 170,
    "players": 8,
    "credit": "SGD Guild",
    "duration_options": [1.5, 3],
    "map_image": None,
    "gear_folder": None,
    "roles": ROLES,   # single source of truth: scheduling format file
    # guide content (empty until this raid is written up)
    "decks_right": {}, "dice": {}, "duos": {}, "cheats_2v2": "",
    "fights_right": [], "left_deck_slots": [], "left_schools": {},
    "left_deck_notes": "", "fights_left": [],
    "stat_caps": {}, "off_school": {}, "off_cols": [], "main_fields": [],
    "fights": {},
}
