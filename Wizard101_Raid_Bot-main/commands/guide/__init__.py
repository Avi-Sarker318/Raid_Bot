"""The /guide browser, split into three pieces:

    tables.py   turn-table → embed fields / monospace grid
    embeds.py   one builder per guide screen
    nav.py      GuideNav button routing + guide_screen()

GuideNav is re-exported here because bot.py registers it on startup.
"""
from .nav import GuideNav, guide_screen

__all__ = ["GuideNav", "guide_screen"]
