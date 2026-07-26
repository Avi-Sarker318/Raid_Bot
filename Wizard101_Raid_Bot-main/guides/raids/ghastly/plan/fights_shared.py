"""Ghastly Conspiracy Raid — fights that both sides run.

Split out of the old single gameplan.py. Import from `plan` (the
package re-exports everything), not from this module directly.

Guide by K31Z, DHMO, FriedChicken935 & MJ (@Makemejelly) — SGD Guild
"""

FIGHT_TOUCH = {'title': '✨ Magic Touch',
 'fields': [('For everyone',
             'Right AND Left side — this is when the two teams meet. '
             '**When:** Right — after the 2v2s. Left — after the 4v4 '
             'counter fight.'),
            ('What happens',
             "Eight touchstones spawn, one for each school in the team's "
             'composition. *(8 Storm wizards → 8 Storm touchstones.)*'),
            ('What you do',
             'Each player must **Magic Touch a touchstone of their OWN '
             'school.** A Magic Touch icon appears at the bottom of your '
             'screen to confirm. One stone each — a lit stone glows and '
             "can't be touched again."),
            ('Then',
             'Once all eight players have touched, **the gates to Mr. '
             'Ghastly & The Red Herring open.**')]}
