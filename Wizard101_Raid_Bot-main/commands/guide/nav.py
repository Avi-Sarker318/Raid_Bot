"""/guide button routing.

One DynamicItem button class (GuideNav) carries a `path` in its custom_id,
so the guide survives bot restarts without re-registering views. Every
screen is a branch in `guide_screen`, which returns (embed, view) — plus
an optional filename when the screen needs an image attachment.
"""
import os

import discord

import guides.loader as raid_defs
from core import ASSETS_DIR
from miscellaneous.stat_caps import caps_embed

from .embeds import (
    PURPLE, base_embed, cantrip_embed, dice_boss_embed, dice_pair_embed,
    dice_table_embed, duo_picker_embed, duo_table_embed, fight_embed,
    gear_embed, left_deck_embed, raid_picker_embed, right_decks_embed,
    roshambo_school_embed, sections_embed, team_embed, fight_turn_embed,
    dice_turn_embed, duo_turn_embed)

GHASTLY = "Ghastly Conspiracy Raid"


def _nav(rows: list[list[tuple[str, str, discord.ButtonStyle] | tuple[str, str]]]
         ) -> discord.ui.View:
    """Build a view of GuideNav buttons from (label, path[, style]) rows."""
    view = discord.ui.View(timeout=None)
    for rownum, row in enumerate(rows):
        for item in row:
            label, path = item[0], item[1]
            style = item[2] if len(item) > 2 else discord.ButtonStyle.secondary
            btn = discord.ui.Button(label=label[:80], style=style,
                                    custom_id=f"gnav:{path}", row=rownum)
            view.add_item(GuideNav(btn, path))
    return view


class GuideNav(discord.ui.DynamicItem[discord.ui.Button],
               template=r"gnav:(?P<path>.+)"):
    """One routed button class for the entire guide — restart-proof."""

    def __init__(self, btn: discord.ui.Button, path: str):
        super().__init__(btn)
        self.path = path

    @classmethod
    async def from_custom_id(cls, itx, item, match):
        return cls(discord.ui.Button(custom_id=item.custom_id),
                   match.group("path"))

    async def callback(self, itx: discord.Interaction):
        result = guide_screen(self.path)
        embed, view = result[0], result[1]
        fname = result[2] if len(result) > 2 else None
        if fname:
            path = os.path.join(ASSETS_DIR, "schools", fname)
            file = discord.File(path, filename=fname)
            await itx.response.edit_message(embed=embed, view=view,
                                            attachments=[file])
        else:
            await itx.response.edit_message(embed=embed, view=view,
                                            attachments=[])


P = discord.ButtonStyle.primary
S = discord.ButtonStyle.secondary


def guide_screen(path: str):
    """Route a nav path to (embed, view)."""
    parts = path.split("|")
    kind = parts[0]
    raid = GHASTLY
    back_sec = ("🏠 Sections", f"sec")

    if kind == "top":
        rows, cur = [[]], 0
        for name in raid_defs.RAIDS:
            r = raid_defs.RAIDS[name]
            has = name == GHASTLY and r["available"]
            label = name if has else f"🚧 {name}"
            if len(rows[cur]) == 3:
                rows.append([]); cur += 1
            rows[cur].append((label, "sec" if has else f"soon|{name}",
                              P if has else S))
        # Always-available tools at the bottom of the main menu.
        rows.append([("📊 Stat Caps", "capsmenu", P),
                     ("✨ Cantrip Tutorial", "cantrip", P),
                     ("⚔️ Roshambo Tutorial", "roshambo", P)])
        return raid_picker_embed(), _nav(rows)

    if kind == "capsmenu":
        # Stat caps live under Ghastly's data; show its cap levels.
        levels = sorted(raid_defs.RAIDS[GHASTLY]["stat_caps"], key=int,
                        reverse=True)
        rows = [[(f"📊 Level {lvl} Caps", f"caps|{lvl}|menu", P)]
                for lvl in levels]
        rows.append([("📚 Main menu", "top")])
        e = discord.Embed(
            title="📊 Stat Caps",
            description="Pick a level to see the per-school caps (HP, damage, "
                        "resist, pierce, accuracy, and outgoing).",
            color=PURPLE)
        return e, _nav(rows)

    if kind == "cantrip":
        return cantrip_embed(), _nav([[("📚 Main menu", "top")]])

    if kind == "roshambo":
        # Menu: intro + a button per school (each opens its own page).
        e = discord.Embed(
            title="⚔️ Roshambo Tutorial — the Magic Circle",
            description=(
                "Every school has strengths, weaknesses, and matchups it "
                "struggles with. These can be **neutralized with weaving and "
                "spell-writing** — unpredictability is key.\n\n"
                "**Pick a school** to see its breakdown:"),
            color=PURPLE)
        order = ["fire", "ice", "storm", "life", "death", "myth", "balance"]
        rows, cur = [[]], 0
        for s in order:
            if len(rows[cur]) == 4:
                rows.append([]); cur += 1
            rows[cur].append((s.title(), f"rosh|{s}", P))
        rows.append([("📚 Main menu", "top")])
        return e, _nav(rows)

    if kind == "rosh":
        school = parts[1]
        embed, fname = roshambo_school_embed(school)
        back = _nav([[("⚔️ All schools", "roshambo"),
                     ("📚 Main menu", "top")]])
        return (embed, back, fname) if fname else (embed, back)

    if kind.startswith("soon"):
        e = discord.Embed(description="That raid's guide is coming soon.",
                          color=0x999999)
        return e, _nav([[("📚 Raids", "top")]])

    if kind == "sec":
        return sections_embed(raid), _nav([
            [("👥 Team Setup", "team", P)],
            [("➡️ Right Side", "right", P), ("⬅️ Left Side", "left", P),
             ("📐 Basics & Gear", "basics", P)],
            [("📚 Other raids", "top")]])

    if kind == "team":
        return (team_embed(raid),
                _nav([[("🏠 Sections", "sec"), ("📚 Other raids", "top")]]))

    if kind == "right":
        return (base_embed(raid, "➡️ Right Side",
                "Decks and fights for Support + Storm 1/2/3."),
                _nav([[("🃏 Deck Setups", "rdecks", P),
                       ("⚔️ Fights", "fights|right", P)], [back_sec]]))

    if kind == "rdecks":
        names = list(raid_defs.RAIDS[raid]["decks_right"])
        return (right_decks_embed(raid),
                _nav([[(n, f"rdeck|{n}") for n in names],
                      [("⬅ Right Side", "right"), back_sec]]))

    if kind == "rdeck":
        return (right_decks_embed(raid, parts[1]),
                _nav([[("⬅ Decks", "rdecks"), back_sec]]))

    if kind == "left":
        return (base_embed(raid, "⬅️ Left Side",
                "Tanks & Hitters — deck and fights."),
                _nav([[("🃏 Deck Setup", "ldeck", P),
                       ("⚔️ Fights", "fights|left", P)], [back_sec]]))

    if kind == "ldeck":
        schools = list(raid_defs.RAIDS[raid]["left_schools"])
        return (left_deck_embed(raid),
                _nav([[(s, f"lschool|{s}") for s in schools[:4]],
                      [(s, f"lschool|{s}") for s in schools[4:]],
                      [("⬅ Left Side", "left"), back_sec]]))

    if kind == "lschool":
        return (left_deck_embed(raid, parts[1]),
                _nav([[("⬅ Another school", "ldeck"), back_sec]]))

    if kind == "fights":
        side = parts[1]
        keys = raid_defs.RAIDS[raid][f"fights_{side}"]
        fights = raid_defs.RAIDS[raid]["fights"]
        rows, cur = [[]], 0
        for k in keys:
            if len(rows[cur]) == 3:
                rows.append([]); cur += 1
            rows[cur].append((fights[k]["title"], f"fight|{side}|{k}"))
        rows.append([(f"⬅ {'Right' if side=='right' else 'Left'} Side", side),
                     back_sec])
        return (base_embed(raid,
                f"⚔️ {'Right' if side=='right' else 'Left'} Side — Fights",
                "Gameplan order — tap a fight for what to do:"), _nav(rows))

    if kind == "fight":
        side, key = parts[1], parts[2]
        if key == "dice":
            bosses = list(raid_defs.RAIDS[raid]["dice"])
            return (dice_boss_embed(raid),
                    _nav([[(b, f"dicep|{b}") for b in bosses[:3]],
                          [(b, f"dicep|{b}") for b in bosses[3:]],
                          [("⬅ Fights", f"fights|{side}"), back_sec]]))
        if key == "2v2":
            duos = list(raid_defs.RAIDS[raid]["duos"])
            return (duo_picker_embed(raid),
                    _nav([[(d, f"duot|{d}", P) for d in duos],
                          [("⬅ Fights", f"fights|{side}"), back_sec]]))
        fight = raid_defs.RAIDS[raid]["fights"][key]
        tables = [fight[t] for t in ("table", "table2") if t in fight] + fight.get("tables", [])
        rows = []
        if tables:
            rows.append([("▶️ Start Turn Guide", f"turn|{side}|{key}|0|0", P)])
        rows.append([("⬅ Fights", f"fights|{side}"), back_sec])
        return fight_embed(raid, key), _nav(rows)

    if kind == "dicep":
        boss = parts[1]
        return (dice_pair_embed(raid, boss),
                _nav([[("Support / Storm 1", f"dicet|{boss}|s1", P),
                       ("Storm 2 / Storm 3", f"dicet|{boss}|s23", P)],
                      [("⬅ Other bosses", "fight|right|dice"), back_sec]]))

    if kind == "dicet":
        boss, pair = parts[1], parts[2]
        d = raid_defs.RAIDS[raid]["dice"][boss][pair]
        rows = []
        if d.get("rows"):
            rows.append([("▶️ Start Turn Guide", f"diceturn|{boss}|{pair}|0", P)])
        rows.append([("⬅ Change role", f"dicep|{boss}"),
                     ("🎲 Other boss", "fight|right|dice"), back_sec])
        return dice_table_embed(raid, boss, pair), _nav(rows)

    if kind == "duot":
        duo = parts[1]
        return (duo_table_embed(raid, duo),
                _nav([[('▶️ Start Turn Guide', f'duoturn|{duo}|0', P)],
                      [("⬅ Other duo", "fight|right|2v2"), back_sec]]))

    if kind == "turn":
        side, key = parts[1], parts[2]
        table_i, row_i = int(parts[3]), int(parts[4])
        fight = raid_defs.RAIDS[raid]["fights"][key]
        tables = [fight[t] for t in ("table", "table2") if t in fight] + fight.get("tables", [])
        table = tables[table_i]
        rows = table["rows"]
        buttons = []
        if row_i > 0:
            buttons.append(("⬅ Previous", f"turn|{side}|{key}|{table_i}|{row_i-1}"))
        elif table_i > 0:
            prev_i = table_i - 1
            buttons.append(("⬅ Previous", f"turn|{side}|{key}|{prev_i}|{len(tables[prev_i]['rows'])-1}"))
        buttons.append(("🏠 Overview", f"fight|{side}|{key}"))
        if row_i + 1 < len(rows):
            buttons.append(("Next ➡", f"turn|{side}|{key}|{table_i}|{row_i+1}", P))
        elif table_i + 1 < len(tables):
            buttons.append(("Next ➡", f"turn|{side}|{key}|{table_i+1}|0", P))
        return fight_turn_embed(raid, key, table_i, row_i), _nav([buttons])

    if kind == "diceturn":
        boss, pair, row_s = parts[1], parts[2], parts[3]
        row_i = int(row_s)
        rows = raid_defs.RAIDS[raid]["dice"][boss][pair]["rows"]
        buttons = []
        if row_i > 0:
            buttons.append(("⬅ Previous", f"diceturn|{boss}|{pair}|{row_i-1}"))
        buttons.append(("🏠 Overview", f"dicet|{boss}|{pair}"))
        if row_i + 1 < len(rows):
            buttons.append(("Next ➡", f"diceturn|{boss}|{pair}|{row_i+1}", P))
        return dice_turn_embed(raid, boss, pair, row_i), _nav([buttons])

    if kind == "duoturn":
        duo, row_s = parts[1], parts[2]
        row_i = int(row_s)
        rows = raid_defs.RAIDS[raid]["duos"][duo]["rows"]
        buttons = []
        if row_i > 0:
            buttons.append(("⬅ Previous", f"duoturn|{duo}|{row_i-1}"))
        buttons.append(("🏠 Overview", f"duot|{duo}"))
        if row_i + 1 < len(rows):
            buttons.append(("Next ➡", f"duoturn|{duo}|{row_i+1}", P))
        return duo_turn_embed(raid, duo, row_i), _nav([buttons])

    if kind == "basics":
        levels = sorted(raid_defs.RAIDS[raid]["stat_caps"], key=int,
                        reverse=True)
        guide_set = raid_defs.RAIDS[raid].get("gear", {})
        rows = []
        right = [k for k in guide_set if not k.endswith("_gear")]  # right/ files
        left = [k for k in guide_set if k.endswith("_gear")]       # left/ files
        if right:
            rows.append([(guide_set[k]["title"], f"gear|{k}", P) for k in sorted(right)][:5])
        if left:
            rows.append([(guide_set[k]["title"], f"gear|{k}", P) for k in sorted(left)])
        rows.append([(f"📊 Level {lvl} Caps", f"caps|{lvl}|basics")
                     for lvl in levels])
        rows.append([back_sec])
        return (base_embed(raid, "📐 Basics & Gear",
                "Gear guides per role, and the stat caps:"), _nav(rows))

    if kind == "gear":
        return (gear_embed(raid, parts[1]),
                _nav([[("⬅ Basics & Gear", "basics"), back_sec]]))

    if kind == "caps":
        lvl = parts[1]
        # parts[2] records where the reader came from: "menu" (main menu's
        # Stat Caps) or "basics" (a raid's Basics & Gear). The back button
        # returns them to that spot instead of somewhere they never opened.
        origin = parts[2] if len(parts) > 2 else "basics"
        others = [l for l in raid_defs.RAIDS[raid]["stat_caps"] if l != lvl]
        back = (("⬅ Stat Caps", "capsmenu") if origin == "menu"
                else ("⬅ Basics & Gear", "basics"))
        return (caps_embed(raid, lvl),
                _nav([[(f"See {o}", f"caps|{o}|{origin}")
                       for o in sorted(others)],
                      [back, ("📚 Main menu", "top")]]))

    return raid_picker_embed(), _nav([[("📚 Raids", "top")]])
