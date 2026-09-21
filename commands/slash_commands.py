"""Backwards-compatible entry point for the slash commands.

This file used to hold all ~1400 lines. It is now a thin shim: the commands
live in commands/cmds/ and the guide browser in commands/guide/. Importing
this module still registers every command, and `from commands.slash_commands
import GuideNav` still works, so nothing that referenced it needs changing.
"""
from . import cmds  # noqa: F401 — importing registers all slash commands
from .guide import GuideNav, guide_screen  # noqa: F401 — re-exported

__all__ = ["GuideNav", "guide_screen"]
