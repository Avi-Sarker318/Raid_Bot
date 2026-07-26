"""Ghastly Conspiracy Raid — dice room bosses + the dice fight entry.

Split out of the old single gameplan.py. Import from `plan` (the
package re-exports everything), not from this module directly.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""

DICE = {'Fire-Storm': {'hp': '16,510',
                's1': {'rows': [['1', 'Tri-Weakness', 'Pass'],
                                ['2/3', '— Attenuate if minion is first —'],
                                ['2/3', 'Blade Storm 1', 'Frenzy'],
                                ['4', 'IC Darkwind', 'Owl']],
                       'd': ['Storm Trap, Weakness', 'Oni, Triton, Trap']},
                's23': {'rows': [['1',
                                  'Stormblade Self',
                                  'Stormblade Self'],
                                 ['2/3',
                                  '— Attenuate if minion is first —'],
                                 ['2/3', 'Frenzy', 'Frenzy'],
                                 ['4', 'Oni', 'Oni']],
                        'd': ['Trap', 'Weakness, Trap']}},
 'Ice-Fire': {'hp': '13,735',
              's1': {'avoid': True,
                     'd': ['Blade, Frenzy, Attenuate, Trap, Weakness',
                           'same']},
              's23': {'rows': [['1', 'TC Empower', 'TC Empower'],
                               ['2', 'IC Darkwind', 'Oni'],
                               ['3', 'Owl', 'Sapper'],
                               ['4', 'Sapper', 'Sapper']],
                      'd': ['Trap, Blade, Frenzy, Attenuate',
                            'Weakness, Trap, Frenzy, Blade, Attenuate']}},
 'Storm-Ice': {'hp': '16,925',
               's1': {'rows': [['1', 'Storm Trap', 'Empower'],
                               ['2', 'IC Darkwind', 'Owl'],
                               ['3', 'Pass', 'Wand'],
                               ['4', 'TC Hit', 'Storm Trap'],
                               ['5+', 'TC Hit/Pass', 'Cleanup']],
                      'd': ['Attenuate, Spirit Weakness, Blade',
                            'Frenzy, Attenuate']},
               's23': {'rows': [['1', 'Pass', 'Storm Trap'],
                                ['2', 'Empower', 'Pass'],
                                ['3', 'IC Darkwind', 'Pass'],
                                ['4', 'Owl', 'Oni'],
                                ['5', 'Storm Trap', 'TC Empower'],
                                ['6', 'Pass', 'Heqet A']],
                       'd': ['Frenzy, Blade, Attenuate',
                             'Stormblade, Frenzy, Attenuate']}},
 'Myth-Life': {'hp': '29,570',
               's1': {'rows': [['1', 'Blade Storm 1', 'Pass'],
                               ['2/3', 'Darkwind', 'Frenzy'],
                               ['2/3', '— Attenuate if minion is first —'],
                               ['4', 'Pass', 'Owl'],
                               ['5', 'TC Hit', 'Pass'],
                               ['6', 'Pass', 'Triton']],
                      'd': ['Storm Trap, Weakness', 'Oni, Trap']},
               's23': {'rows': [['1', 'IC Darkwind', 'Pass'],
                                ['2', 'Stormblade Self', 'Stormblade Self'],
                                ['3',
                                 'Attenuate (if minion is first)',
                                 'Attenuate (if minion is first)'],
                                ['4', 'Frenzy', 'Frenzy'],
                                ['5', 'Owl', 'Oni']],
                       'd': ['Trap', 'Weakness, Trap']}},
 'Death-Myth': {'hp': '12,475',
                's1': {'rows': [['1', 'IC Darkwind', 'Empower'],
                                ['2', 'Storm Trap', 'Owl'],
                                ['3', 'Pass', 'Wand'],
                                ['4', 'TC Hit', 'Pass'],
                                ['5', 'TC Hit/Pass', 'Triton/Soulsapper']],
                       'd': ['Attenuate, Spirit Weakness, Blade',
                             'Frenzy, Attenuate']},
                's23': {'rows': [['1', 'IC Darkwind', 'Pass'],
                                 ['2', 'Pass', 'Storm Trap'],
                                 ['3', 'Empower', 'Pass'],
                                 ['4', 'Owl', 'Oni'],
                                 ['5+', 'Storm Trap', 'Cleanup']],
                        'd': ['Stormblade, Frenzy, Attenuate',
                              'Stormblade, Frenzy, Attenuate']}},
 'Life-Death': {'hp': '15,160',
                's1': {'rows': [['1', 'Weakness', 'Empower'],
                                ['2', 'IC Darkwind', 'Wand'],
                                ['3', 'Weakness', 'Oni'],
                                ['4', 'TC Hit', 'Pass'],
                                ['5', 'Pass', 'Triton']],
                       'd': ['Blade, Attenuate, Trap',
                             'Storm Trap, Frenzy, Attenuate']},
                's23': {'rows': [['1', 'Empower', 'Empower'],
                                 ['2', 'IC Darkwind', 'Tri-Weakness'],
                                 ['3', 'Pass', 'Treefold'],
                                 ['4+', 'Oni', 'Hit']],
                        'd': ['Stormblade, Frenzy, Storm Trap, Attenuate',
                              'Stormblade, Frenzy, Storm Trap, '
                              'Attenuate']}}}

def _dice_overview_fields():
    """Build turn-card fields for the dice overview: one line per boss with
    its HP, plus the universal rule. Derived from DICE so it never goes stale
    or renders as 'none'."""
    lines = []
    for boss, info in DICE.items():
        lines.append(f"**{boss}** — {info['hp']} HP")
    return [
        ("🎲 Which boss are you getting?",
         "Each dice-room boss has its own turn-by-turn plan. Pick your boss "
         "from the buttons, then your role, to get the exact turns."),
        ("Bosses & HP", "\n".join(lines)),
        ("🌀 Golden rule",
         "**YOU CAN ALWAYS DARKWIND!** If you're ever unsure, Darkwind and "
         "spam hits. *(credit @friedchicken935)*"),
    ]


FIGHT_DICE = {'title': '🎲 Dice Fights',
              'fields': _dice_overview_fields()}
