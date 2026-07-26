"""Ghastly Conspiracy Raid — right-role decks + left school-swap deck.

Split out of the old single gameplan.py. Import from `plan` (the
package re-exports everything), not from this module directly.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""

DECKS = {'Support (Universal)': [('Base cards',
                          'Elemental Weakness ×2, Attenuate (weaved), '
                          'Storm Trap, Darkwind, Stormblade, Purge, '
                          'Shatter ×3, Healing IV, Horn of Plenty 3'),
                         ('Your hit',
                          'Own-school TC hit — **4–5 pip cost** ×3'),
                         ('Fire variant',
                          "Inferno Attenuate, Oni's Forge, Cleanse Charm, "
                          'Phoenix ×3'),
                         ('Myth variant',
                          "Epiphany Attenuate, Jinn's Defense, Cleanse "
                          'Charm, Minotaur ×3'),
                         ('Universal 2',
                          'Dark Tribute, Pierce (set pips to Storm or '
                          'Myth)')],
 'Storm 1': [('Cards',
              'Triton, Ultra Cyclone (wand hit), Attenuate, Storm Trap, '
              'Frenzy, Storm Owl, Turmoil Oni, Empower ×3 (TC), Soulsapper '
              '×3 (TC), Infection ×2 (TC), Healing IV, Horn of Plenty 3')],
 'Storm 2': [('Cards',
              'Storm Trap, Darkwind, Attenuate, Frenzy, Storm Owl, '
              'Stormblade, Turmoil Oni, Empower ×4 (TC), Soulsapper ×3 '
              '(TC), Lightning Bats ×2 (TC), Healing IV, Horn of Plenty '
              '3')],
 'Storm 3': [('Cards',
              'Stormblade, Storm Trap, Elemental Weakness, Attenuate, '
              'Heqet, Turmoil Oni, Frenzy, Threefold Fever (TC — can be an '
              'Infection instead), Empower ×4 (TC), Soulsapper ×4 (TC), '
              'Typhoon Attenuate, Healing IV, Horn of Plenty'),
             ('Note', '**Storm weaved Attenuate is better!**')]}

DECK_SLOTS = [{'s': 'blade'},
 {'f': 'Frenzy'},
 {'s': 'blue'},
 {'s': 'yellow'},
 {'s': 'orange'},
 {'f': 'Attenuate'},
 {'s': 'green'},
 {'s': 'trap'},
 {'f': 'Empower ×3 (TC)'},
 {'f': '3× own-school TC hit (4–5 pip cost)'}]

SCHOOLS = {'Ice': {'emoji': '❄️',
         'blade': 'Ice Blade',
         'trap': 'Ice Trap',
         'blue': 'Penguin Barrage',
         'yellow': 'Shu (A)',
         'orange': 'Jinn',
         'green': 'Blight Hound (A)'},
 'Fire': {'emoji': '🔥',
          'blade': 'Fire Blade',
          'trap': 'Fire Trap',
          'blue': 'Raging Bull (B) / Meteor (B)',
          'yellow': 'Amut (A)',
          'orange': 'Amut (A)',
          'green': 'Immolate (A)'},
 'Storm': {'emoji': '⚡',
           'blade': 'Storm Blade',
           'trap': 'Storm Trap',
           'blue': 'Kraken',
           'yellow': 'Heqet',
           'orange': 'Turmoil Oni',
           'green': 'Kraken'},
 'Myth': {'emoji': '🟡',
          'blade': 'Myth Blade',
          'trap': 'Myth Trap',
          'blue': 'Frog (B)',
          'yellow': 'Colossus (A)',
          'orange': 'Jinn',
          'green': 'Tom Button'},
 'Life': {'emoji': '🍃',
          'blade': 'Life Blade',
          'trap': 'Life Trap',
          'blue': 'Lamassu (A)',
          'yellow': 'Centaur (A)',
          'orange': 'Oni',
          'green': 'Earth Walker (A)'},
 'Death': {'emoji': '💀',
           'blade': 'Death Blade',
           'trap': 'Death Trap',
           'blue': 'Quismah (A)',
           'yellow': 'Anubis (A)',
           'orange': 'Oni',
           'green': 'Pirate (A)'},
 'Balance': {'emoji': '⚖️',
             'blade': 'Balance Blade',
             'trap': 'Balance Trap',
             'blue': 'Sandworm (B)',
             'yellow': 'Cameleon (A)',
             'orange': 'Chimera',
             'green': 'Scythe (A)'}}

DECK_NOTES = ('Also required: Reveal Invisible trained • 50+ energy • lvl-0 cantrips '
 '(Healing IV, Dual Strike, Legion Shield, Fiery Explosion, Restoring '
 'Rain, Virulent Plague, Sprite Swarm)')
