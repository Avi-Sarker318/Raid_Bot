"""Ghastly Conspiracy Raid — left-side fights.

Split out of the old single gameplan.py. Import from `plan` (the
package re-exports everything), not from this module directly.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""

FIGHT_COINS = {'title': '🪙 Coins: Tokens & Chests',
 'fields': [('Roles (4-player puzzle)',
             'One player enters the pet hole in **pet mode** (ie. '
             'Butterfly, Bird, Snake 3 3 3). The other 3 players work with '
             'them to complete the puzzle.'),
            ('🗝️ Reading the chests',
             'The chests are **outside**, in order left → right: **Silver '
             '→ Gold → Wood**. Each chest sits on a chimney:'),
            ('Roman numeral (on the chimney)',
             'How **many** of that coin you need.'),
            ('Coin on top', '**Which** coin to collect for that chest.'),
            ('Objective',
             'Complete the token deposits correctly **3 times**. Try to '
             'finish before *ICE ATTUNEMENT* :)')]}

FIGHT_LAZERS = {'title': '🔦 Lazers & Moo Crew',
 'table': {'name': 'Moo Crew solo',
           'cols': ['Action'],
           'rows': [['1', 'Blade'],
                    ['2', 'Attenuate / Frenzy'],
                    ['3', 'Frenzy / Hit'],
                    ['4', 'Hit']]},
 'fields': [('Before entering',
             'Stand on the X, cast Reveal Invisible so your SCHOOL coin '
             'token spawns.'),
            ('Maze',
             '4 colored plates each disable one laser. Blinking = locked. '
             'First across helps the rest via the 2nd plate set.'),
            ('After Moo Crew', 'Pet mode, grab the mounds.')]}

FIGHT_QUARTERMANE = {'title': '🦖 Quartermane Polymorph Fight',
 'table': {'turn': 'Dino',
           'name': 'Usable gambits (the cantrips you ask for)',
           'cols': ['Ask for these'],
           'rows': [['FIRE', 'Blade, Weak, Heal, DoT'],
                    ['ICE', 'Shield, Trap, Heal, DoT'],
                    ['STORM', 'Shield, Trap, Blade, Weak']]},
 'fields': [('Requirements', '**Min 50 energy.** Do this BEFORE the 4v4.'),
            ('1. Discard',
             'Discard all unusable gambits for your dino — 0/1-pip spells '
             'are the recommended discards, to fish for more 2-pip hits.'),
            ('2. Call FAST',
             "Call for the gambit hanging effect you need that's IN HAND, "
             "FAST — so the outside helper's cantrip animation reaches you "
             'before you select a card.'),
            ('3. Below 2 pips',
             '0-pip hit or pass is fine. Dinos may debuff as you hit — '
             'conserving for 2 pips hits through a debuff.')]}

FIGHT_4V4 = {'title': '🌀 4v4 Counter Fight',
 'table': {'turn': 'Rnd',
           'name': 'What to do',
           'cols': ['Everyone'],
           'rows': [['1', 'Pass — wait for Right Side to send the cheat'],
                    ['2', 'Pass — keep waiting'],
                    ['3',
                     'P1 plays the matching counter (poly cheat in hand) • '
                     'P2–P4 hit (4–7 pip spells)']]},
 'table2': {'turn': 'Player',
            'name': 'Counter cards by health order',
            'cols': ['Cards'],
            'rows': [['P1',
                      'ICE: Elf / Iceblade / Snow Drift — also pulls '
                      'Ice/Storm mob FIRST'],
                     ['P2', 'DEATH: Bat / Trap / Sacrifice'],
                     ['P3', "MYTH: Weakness / Mythblade / Grendel's"],
                     ['P4', 'STORM: Elf / Trap / Shield']]},
 'fields': [('How it works',
             'The fight calls out your health — line up **most health → '
             "least** (P1 = highest). Right Side learns each duo's cheat "
             "in their 2v2s and tells you. **Don't kill until you know "
             'it.**'),
            ('⚠️ Rules',
             'Do 🦖 Quartermane FIRST. Join together — no staggering. Touch '
             'the Balance Stone BEFORE. ICE never last (bugs). Schools can '
             'trade either/or, but P1 always pulls the Ice/Storm mob '
             'first.')]}

FIGHT_RED_HERRING = {'title': '🐟 Red Herring (SOLO)',
 'table': {'cols': ['Death wiz', 'Storm wiz'],
           'rows': [['1', 'Set Shield', 'Set Shield'],
                    ['2',
                     'Ghoul (Mime after it hits)',
                     'Ghoul (Mime after it hits)'],
                    ['3', 'Blade', 'Blade'],
                    ['4', 'Scion of Death', 'Turmoil Oni']]},
 'fields': [('⚠️',
             'MUST GET WEAKNESS FOLDERS! Take the Crime Mime hit **AFTER** '
             "your Ghoul lands — the trap can't buff the ghoul. *Optional "
             '— most teams do the Folders instead and skip this.*'),
            ('Solo deck — Death',
             'Skeletal Pirate ×2, Ghoul, Scion of Death, Frenzy, '
             'Deathblade, Dream Shield'),
            ('Solo deck — Storm',
             'Kraken ×2, Ghoul, Turmoil Oni, Frenzy, Stormblade, Thermic '
             'Shield')]}

FIGHT_GHASTLY_L = {'title': '👻 Ghastly Fight (Left)',
 'tables': [{'name': '🦋 Moth (P1–P3)',
             'cols': ['P1–P3'],
             'rows': [['1', 'Pass'],
                      ['2', 'AoE minions (P3: Trap boss)'],
                      ['3', 'Hit the boss']]},
            {'name': '⚡ Lucien (Storms)',
             'cols': ['S1', 'S2', 'S3'],
             'rows': [['1', 'Trap', 'Bubble', 'Frenzy'],
                      ['2', 'Attenuate', 'Blade S3', 'HIT']]},
            {'name': '🐗 Morg the Merciless (Solo)',
             'cols': ['Action'],
             'rows': [['1', 'Blade'],
                      ['2', 'Attenuate'],
                      ['3', 'Frenzy'],
                      ['4', 'Oni/Jin'],
                      ['5', 'Clean up hit']]},
            {'name': '🎭 Crime Mime — 2 players',
             'cols': ['P1', 'P2'],
             'rows': [['1', 'Trap', 'Pass'],
                      ['2', '— Empower (TC) —'],
                      ['3', 'Oni/Jin', 'Trap'],
                      ['4', 'Hit', 'Oni/Jin'],
                      ['5', '— TC Hit if needed —']]},
            {'name': '🎭 Crime Mime — 3 players',
             'cols': ['P1', 'P2', 'P3'],
             'rows': [['1', 'Trap', 'Pass', 'Pass'],
                      ['2', 'Hit', 'Trap', 'Hit'],
                      ['3', 'Hit', 'Hit', 'Trap'],
                      ['4', '— TC Hit if needed —']]}],
 'fields': [('Flow',
             'Start BEFORE the Life Stone. **Left does Morg & Mime while '
             'Right does Ghastly.** If no folders: Red Herring stands by. '
             'P1–P3 fight Moth, Storms fight Lucien; then P1–P3: Crime '
             'Mime → Morg.'),
            ('🎭 Mime traps',
             'Strongest school traps: Storm-Fire-Myth-etc.'),
            ('Allowed buffs',
             '🐗 Morg (Fire): Blade, Auras, Global — **NO Shields, Traps**. '
             '🎭 Mime (Death): Trap, Global — **NO Blade, HoT, Auras**.'),
            ('Moth discards', 'Blade, Frenzy, Attenuate')]}
