"""Ghastly Conspiracy Raid — right-side fights.

Split out of the old single gameplan.py. Import from `plan` (the
package re-exports everything), not from this module directly.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""

FIGHT_FOLDERS = {'title': '📁 Find the Folders',
 'fields': [('Objective',
             '2-player puzzle: collect evidence for Dog Tracy → sends '
             'support spells to Lower Side.'),
            ('Forensic (unlit tar)',
             '3 pieces → Call in Backup (10% dmg + 660 3-round HoT). '
             "Roshambo doesn't apply to Dog Tracy HoTs."),
            ('Bombshell (lit tar)',
             'Light tar w/ Eternal Flame. 3 pieces → R&R (3000 HP heal).'),
            ('Hazards',
             'Tar slows you; lit tar ticks 50 dmg while standing in it.'),
            ('Note',
             'Most people do the folders and skip the Red Herring solo. If '
             "you'd rather not do folders, Red Herring (Left) is the "
             'alternative.'),
            ('💣 After folders + 1v1s',
             'Pick 2 players to do the mana bombs.')]}

FIGHT_SOLO = {'title': '🧍 Solo Fights (1v1s)',
 'fields': [('Rule', 'STALL YOUR TURNS! You get Darcy and RRs this fight.'),
            ('Storm/Myth/Life/Fire mob',
             'Storm Blade → Empower → Attenuate → Owl/Oni'),
            ('Ice/Death mob', 'Storm Trap → Empower → Pass → Owl/Oni')]}

FIGHT_AUTOMATION = {'title': '🤖 Automaton Fight',
 'table': {'cols': ['Storm 1', 'Storm 3', 'Support', 'Storm 2'],
           'rows': [['1',
                     'Wand boss',
                     '🟠Frenzy/🟣Trap minion',
                     'Storm Bubble',
                     '🟠Blade 🟣Pass'],
                    ['2',
                     'Triton boss',
                     'Heqet minion',
                     'Spirit-Weakness',
                     'Frenzy'],
                    ['3',
                     'TC Infection',
                     'Tri-Weakness',
                     '🟠Attenuate/🟣Blade Storm 2',
                     'Oni boss']]},
 'fields': [('⚠️ Rules',
             'LOOK AT PULLING ORDER! Storm 1 pulls minion. '
             '**🟠 = any minion, 🟣 = Death minion.**'),
            ('Tips',
             'Unicorn cantrips if low HP. Touch Balance Stone after!')]}

FIGHT_GHASTLY_R = {'title': '👻 Ghastly Fight (Right)',
 'table': {'turn': 'Rnd',
           'cols': ['Support', 'Storm 3', 'Storm 2', 'Storm 1'],
           'rows': [['1', 'Weakness', 'Blade Self', 'Blade Self', 'Pass'],
                    ['2', 'Blade (S1)', 'Weakness', 'Darkwind', 'Pass'],
                    ['3', 'Pass', 'Frenzy', 'Frenzy', 'Frenzy'],
                    ['4', '— PASS FAST! —'],
                    ['5', '— PASS FAST! —'],
                    ['6',
                     'Attenuate',
                     'Attenuate',
                     'Attenuate',
                     'Attenuate'],
                    ['7', 'Weakness', 'Oni', 'Oni', 'Oni']]},
 'fields': [('⚠️ Rules',
             'Need ALL side fights done. NO cantrips. Start BEFORE Fire '
             'Stone. Watch pulling order.'),
            ('Cheat (end R2)',
             "'I am becoming Fire→Storm, Ice→Fire, Storm→Ice, Life→Death, "
             "Myth→Life, Death→Myth' (Support converts pips)")]}
