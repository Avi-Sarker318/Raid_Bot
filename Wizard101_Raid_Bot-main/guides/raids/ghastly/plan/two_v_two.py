"""Ghastly Conspiracy Raid — 2v2 duo fights + cheat codes.

Split out of the old single gameplan.py. Import from `plan` (the
package re-exports everything), not from this module directly.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""

CHEATS_2V2 = ('STORM: DoT Trap Shield • ICE: DoT Blade HoT • MYTH: Weakness Blade HoT • '
 'DEATH: DoT Trap HoT')

DUOS = {'Chicken & Bull': {'pair': 'Support & Storm 1',
                    'puller': 'Support pulls Bull',
                    'note': '',
                    'cols': ['Support', 'Storm 1'],
                    'rows': [['1', 'Attenuate Bull', 'Trap Bull'],
                             ['2', 'Darkwind', 'Triton Bull'],
                             ['3',
                              'Break shield / TC hit Chicken',
                              'Wand Chicken'],
                             ['4', 'Trap Chicken', 'Empower'],
                             ['5',
                              'Hit / Shatter / Purge',
                              'Oni/Owl Chicken']],
                    'd': None},
 'Zebra & Panther': {'pair': 'Storm 2 & Storm 3',
                     'puller': 'Storm 2 pulls Zebra',
                     'note': '',
                     'cols': ['Storm 2', 'Storm 3'],
                     'rows': [['1', 'Trap Zebra', 'Trap Panther'],
                              ['2', 'Darkwind', 'Pass'],
                              ['3',
                               'Pass',
                               'Oni Zebra'],
                              ['4',
                               'Oni Panther',
                               'Clean up Hit']],
                     'd': ['Frenzy, Blade, Attenuate',
                           'Frenzy, Blade, Attenuate, Weakness']}}

FIGHT_2V2 = {'title': '⚔️ 2v2 Fights'}
