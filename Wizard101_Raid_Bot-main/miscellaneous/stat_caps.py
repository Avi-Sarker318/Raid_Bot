"""Stat caps: the caps embed + level-toggle popup view."""
import discord

import guides.loader

from guides.loader import RAIDS, highest_cap_level


def _base(raid: str, title: str, desc: str) -> discord.Embed:
    # No author credit here — stat caps are general game data, not part of
    # the raid strategy guide, so crediting the guide authors would be wrong.
    return discord.Embed(title=title, description=desc, color=0x8A2BE2)


_SCHOOL_ANSI = {
    "Fire":    "\u001b[0;31m",   # red
    "Ice":     "\u001b[0;34m",   # blue
    "Storm":   "\u001b[0;35m",   # magenta (closest to purple)
    "Myth":    "\u001b[0;33m",   # yellow
    "Life":    "\u001b[0;32m",   # green
    "Death":   "\u001b[0;30m",   # dark grey/black
    "Balance": "\u001b[0;33m",   # gold (closest to brown)
}
# Off-school columns are abbreviated F/I/S/M/L/D/B — colour them to match.
_LETTER_ANSI = {
    "F": _SCHOOL_ANSI["Fire"],  "I": _SCHOOL_ANSI["Ice"],
    "S": _SCHOOL_ANSI["Storm"], "M": _SCHOOL_ANSI["Myth"],
    "L": _SCHOOL_ANSI["Life"],  "D": _SCHOOL_ANSI["Death"],
    "B": _SCHOOL_ANSI["Balance"],
}
_RESET = "\u001b[0m"


def caps_embed(raid: str, level: str) -> discord.Embed:
    r = RAIDS[raid]
    rows = r["stat_caps"][level]
    off = r.get("off_school", {}).get(level, {})
    blocks = []
    for school in ["Fire", "Ice", "Storm", "Myth", "Life", "Death", "Balance"]:
        vals = rows[school]
        main = " • ".join(f"{r['main_fields'][i]} {vals[i]}"
                          for i in range(len(vals)))
        colour = _SCHOOL_ANSI.get(school, "")
        b = f"{colour}{school}{_RESET}\n  {main}"
        if school in off:
            cells = []
            for i, letter in enumerate(r["off_cols"]):
                lc = _LETTER_ANSI.get(letter, "")
                cells.append(f"{lc}{letter}{_RESET} {off[school][i]}")
            b += "\n  Off-school:  " + "  ".join(cells)
        blocks.append(b)
    # ANSI code block so the school names render in their school colours.
    desc = (f"This is a lvl {r['level']} raid — hit the caps for **your** "
            "level or scaling drops you below the base caps.\n\n"
            "```ansi\n" + "\n\n".join(blocks) + "\n```"
            + "\n*F=Fire I=Ice S=Storm M=Myth L=Life D=Death B=Balance*")
    return _base(raid, f"📊 Level {level} Stat Caps", desc)


class StatCapsView(discord.ui.View):
    """Ephemeral: toggle stat-cap level. Defaults to the highest level."""

    def __init__(self, raid: str = "Ghastly Conspiracy Raid"):
        super().__init__(timeout=300)
        self.raid = raid
        for lvl in sorted(guides.loader.RAIDS[raid]["stat_caps"], key=int,
                          reverse=True):
            btn = discord.ui.Button(label=f"Level {lvl}",
                                    style=discord.ButtonStyle.primary)
            btn.callback = self._make_cb(lvl)
            self.add_item(btn)

    def _make_cb(self, lvl: str):
        async def cb(itx: discord.Interaction):
            await itx.response.edit_message(
                embed=caps_embed(self.raid, lvl), view=self)
        return cb
