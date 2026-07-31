"""/petcalculator — compute every pet talent's stat from a pet's base stats.

The user gives Strength/Intellect/Agility/Will/Power. The command rounds
each talent's granted stat (matching the in-game display) and shows them
grouped by stat type across pages, with ◀ ▶ buttons.

The page buttons are a restart-proof DynamicItem: the five stats are packed
into the custom_id, so the view keeps working after the bot restarts without
re-registering anything (same approach as the guide's GuideNav).
"""
import discord
from discord import app_commands

from core import client, tree
from miscellaneous.pet_talents import (
    CAPS, CAP_LABEL, TALENTS, all_values, S, I, A, W, P)

PURPLE = 0x8A2BE2
PER_PAGE = 8  # talents per page


def _pack(stats: dict) -> str:
    return f"{stats[S]}.{stats[I]}.{stats[A]}.{stats[W]}.{stats[P]}"


def _unpack(blob: str) -> dict:
    s, i, a, w, p = (int(x) for x in blob.split("."))
    return {S: s, I: i, A: a, W: w, P: p}


def _pages(stats: dict) -> list[list[tuple[str, str, int]]]:
    rows = all_values(stats)
    return [rows[i:i + PER_PAGE] for i in range(0, len(rows), PER_PAGE)]


def calc_embed(stats: dict, page: int) -> discord.Embed:
    pages = _pages(stats)
    page = max(0, min(page, len(pages) - 1))

    over = [f"{CAP_LABEL[k]} {stats[k]} (cap {CAPS[k]})"
            for k in (S, I, A, W, P) if stats[k] > CAPS[k]]

    header = (f"**Strength** {stats[S]} · **Intellect** {stats[I]} · "
              f"**Agility** {stats[A]} · **Will** {stats[W]} · "
              f"**Power** {stats[P]}")
    if over:
        header += "\n⚠️ Above base cap: " + ", ".join(over) + \
                  " — allowed, values still computed."

    e = discord.Embed(title="🐾 Pet Talent Calculator", description=header,
                      color=PURPLE)

    lines = []
    for label, unit, val in pages[page]:
        lines.append(f"`{val:>4}`  +{val}{unit} — {label}")
    e.add_field(name="\u200b", value="\n".join(lines), inline=False)
    e.set_footer(text=f"Page {page + 1}/{len(pages)} · in-game rounded values")
    return e


def _view(stats: dict, page: int) -> discord.ui.View:
    pages = _pages(stats)
    page = max(0, min(page, len(pages) - 1))
    blob = _pack(stats)
    view = discord.ui.View(timeout=None)
    prev_p = (page - 1) % len(pages)
    next_p = (page + 1) % len(pages)
    view.add_item(PetNav(
        discord.ui.Button(label="◀ Prev", style=discord.ButtonStyle.secondary,
                          custom_id=f"pcalc:{blob}:{prev_p}"),
        blob, prev_p))
    view.add_item(PetNav(
        discord.ui.Button(label=f"{page + 1}/{len(pages)}",
                          style=discord.ButtonStyle.primary, disabled=True,
                          custom_id=f"pcalc:{blob}:{page}:x"),
        blob, page))
    view.add_item(PetNav(
        discord.ui.Button(label="Next ▶", style=discord.ButtonStyle.secondary,
                          custom_id=f"pcalc:{blob}:{next_p}"),
        blob, next_p))
    return view


class PetNav(discord.ui.DynamicItem[discord.ui.Button],
            template=r"pcalc:(?P<blob>[\d.]+):(?P<page>\d+)(?::x)?"):
    """Page button for the pet calculator — restart-proof."""

    def __init__(self, btn: discord.ui.Button, blob: str, page: int):
        super().__init__(btn)
        self.blob = blob
        self.page = page

    @classmethod
    async def from_custom_id(cls, itx, item, match):
        return cls(discord.ui.Button(custom_id=item.custom_id),
                   match.group("blob"), int(match.group("page")))

    async def callback(self, itx: discord.Interaction):
        stats = _unpack(self.blob)
        await itx.response.edit_message(
            embed=calc_embed(stats, self.page),
            view=_view(stats, self.page))


@tree.command(name="petcalculator",
              description="Calculate every pet talent's stat from your pet's "
                          "base stats")
@app_commands.describe(
    strength="Pet Strength (base cap 255)",
    intellect="Pet Intellect (base cap 250)",
    agility="Pet Agility (base cap 260)",
    will="Pet Will (base cap 260)",
    power="Pet Power (base cap 250)")
async def petcalculator(interaction: discord.Interaction,
                        strength: app_commands.Range[int, 0, 1000],
                        intellect: app_commands.Range[int, 0, 1000],
                        agility: app_commands.Range[int, 0, 1000],
                        will: app_commands.Range[int, 0, 1000],
                        power: app_commands.Range[int, 0, 1000]):
    stats = {S: strength, I: intellect, A: agility, W: will, P: power}
    await interaction.response.send_message(
        embed=calc_embed(stats, 0), view=_view(stats, 0), ephemeral=True)