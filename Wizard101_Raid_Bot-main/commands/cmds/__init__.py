"""Every slash command, grouped by what it does.

Importing this package imports each module, and importing a module is what
registers its @tree.command handlers with Discord — so this single import
is all bot.py needs.

    server_setup.py      /setup   /assign
    scheduling_cmds.py   /schedule  /raids
    guide_cmds.py        /guide
    help_cmd.py          /help
    moderation.py        /testreport  /ban  /unban
    cleanup.py           /cancelraid  /clearhistory  /clearallevents
"""
from . import (  # noqa: F401 — imported for their command registrations
    cleanup,
    guide_cmds,
    help_cmd,
    moderation,
    scheduling_cmds,
    server_setup,
)
