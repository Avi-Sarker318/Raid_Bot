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
from .embeds import guide_help_embed

from .embeds import (
    PURPLE, base_embed, cantrip_embed, dice_boss_embed, dice_pair_embed,
    dice_table_embed, duo_picker_embed, duo_table_embed, fight_embed,
    gear_embed, left_deck_embed, raid_picker_embed, right_decks_embed,
    roshambo_school_embed, sections_embed, team_embed, fight_turn_embed,
    dice_turn_embed, duo_turn_embed)

from .tables import _role_icon as _tbl_icon

GHASTLY = "Ghastly Conspiracy Raid"
BLIGHTED = "Blighted Veil Raid"

# Ghastly right-side roles (left side stays as-is): side, deck page, gear page, dice pair, 2v2 duo. Picking a
# role once means the guide never asks "Storm 2 or Storm 3?" again.
ROLE_INFO = {
    "Support": dict(side="right", deck="Support (Universal)",
                    gear="support_gear_guide", pair="s1", duo="Chicken & Bull"),
    "Storm 1": dict(side="right", deck="Storm 1", gear="storm1_gear_guide",
                    pair="s1", duo="Chicken & Bull"),
    "Storm 2": dict(side="right", deck="Storm 2", gear="storm2_gear_guide",
                    pair="s23", duo="Zebra & Panther"),
    "Storm 3": dict(side="right", deck="Storm 3", gear="storm3_gear_guide",
                    pair="s23", duo="Zebra & Panther"),
}

# Raids with a written guide -> the /guide screen their button opens.
GUIDE_ENTRY = {GHASTLY: "sec", BLIGHTED: "bvr|home"}


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
            # "fire.png" lives in assets/schools/; "bvr/floor1.png" is a
            # path relative to assets/ (used by the Blighted Veil maps).
            if "/" in fname:
                path = os.path.join(ASSETS_DIR, *fname.split("/"))
            else:
                path = os.path.join(ASSETS_DIR, "schools", fname)
            file = discord.File(path, filename=os.path.basename(fname))
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
    if kind == "bvr":
        # Blighted Veil Raid has its own screens (bvr_nav.py). Imported here
        # because bvr_nav builds on _nav / P / S from this module.
        from .bvr_nav import bvr_screen
        return bvr_screen(parts[1:])
    raid = GHASTLY
    back_sec = ("🏠 Sections", f"sec")

    if kind == "top":
        # Only raids with a finished guide are listed.
        raids = [(n, GUIDE_ENTRY[n]) for n in GUIDE_ENTRY
                 if n in raid_defs.RAIDS and raid_defs.RAIDS[n]["available"]]
        return raid_picker_embed(), _nav([
            [(f"📖 {n}", path, P) for n, path in raids],
            [("📊 Stat Caps", "capsmenu"), ("✨ Cantrip Tutorial", "cantrip"),
             ("⚔️ Roshambo Tutorial", "roshambo")],
            [("❓ How to use /guide", "help")]])

    if kind == "help":
        return guide_help_embed(), _nav([[("📚 Main menu", "top", P)]])

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

    if kind == "sec":                      # step 1: which side?
        return sections_embed(raid), _nav([
            [("➡️ Right Side", "right", P), ("⬅️ Left Side", "left", P)],
            [("👥 Team Setup", "team"), ("🎒 Gear Setups", "basics"),
             ("📚 Other raids", "top")]])

    if kind == "team":
        return (team_embed(raid),
                _nav([[("🏠 Sections", "sec"), ("📚 Other raids", "top")]]))

    # ---------------- Right side: pick your role once ----------------
    # Every right-side path carries the role, so the guide never asks
    # "Support / Storm 1" or "Storm 2 / Storm 3" again.
    if kind == "right":                    # step 2: which role?
        e = base_embed(raid, "➡️ Right Side",
                       "**Which role are you?** Everything after this is "
                       "just for your role.")
        e.color = 0x8E44AD
        return e, _nav([
            [(f"{_tbl_icon(r_)} {r_}", f"grole|{r_}", P) for r_ in ROLE_INFO],
            [back_sec]])

    if kind == "grole":                    # step 3: role hub
        role = parts[1]
        e = base_embed(raid, f"{_tbl_icon(role)} {role}",
                       "Pick what you need:")
        e.color = 0x8E44AD
        e.set_author(name=f"{raid} › ➡️ Right Side › {role}")
        return e, _nav([
            [("⚔️ My Fights", f"gf|{role}", P),
             ("🃏 My Deck", f"gdeck|{role}", P),
             ("🎒 My Gear", f"ggear|{role}", P)],
            [("⬅ Change role", "right"), back_sec]])

    if kind == "gdeck":
        role = parts[1]
        e = right_decks_embed(raid, ROLE_INFO[role]["deck"])
        e.set_author(name=f"{raid} › ➡️ Right Side › {role}")
        return e, _nav([[(f"⬅ {role}", f"grole|{role}"), back_sec]])

    if kind == "ggear":
        role = parts[1]
        e = gear_embed(raid, ROLE_INFO[role]["gear"])
        e.set_author(name=f"{raid} › ➡️ Right Side › {role}")
        return e, _nav([[(f"⬅ {role}", f"grole|{role}"), back_sec]])

    if kind == "gf":                       # your fights, in gameplan order
        role = parts[1]
        keys = raid_defs.RAIDS[raid]["fights_right"]
        fights = raid_defs.RAIDS[raid]["fights"]
        btns = []
        for k in keys:
            if k == "solo" and role == "Support":
                continue                          # Support skips the 1v1s
            path = {"dice": f"gdice|{role}",
                    "2v2": f"gduo|{role}"}.get(k, f"gfight|{role}|{k}")
            btns.append((fights[k]["title"], path, P))
        rows = [btns[i:i + 3] for i in range(0, len(btns), 3)]
        rows.append([(f"⬅ {role}", f"grole|{role}"), back_sec])
        e = base_embed(raid, f"⚔️ {role} — Fights",
                       "Gameplan order — tap a fight:")
        e.set_author(name=f"{raid} › ➡️ Right Side › {role}")
        return e, _nav(rows)

    if kind == "gfight":
        role, key = parts[1], parts[2]
        fight = raid_defs.RAIDS[raid]["fights"][key]
        tables = [fight[t] for t in ("table", "table2") if t in fight] + fight.get("tables", [])
        rows = []
        if tables:
            rows.append([("▶️ Start Turn Guide", f"gturn|{role}|{key}|0|0", P)])
        rows.append([("⬅ My Fights", f"gf|{role}"), back_sec])
        e = fight_embed(raid, key)
        e.set_author(name=f"{raid} › ➡️ Right Side › {role}")
        return e, _nav(rows)

    if kind == "gturn":
        role, key = parts[1], parts[2]
        table_i, row_i = int(parts[3]), int(parts[4])
        fight = raid_defs.RAIDS[raid]["fights"][key]
        tables = [fight[t] for t in ("table", "table2") if t in fight] + fight.get("tables", [])
        rows = tables[table_i]["rows"]
        base = f"gturn|{role}|{key}"
        buttons = []
        if row_i > 0:
            buttons.append(("⬅ Previous", f"{base}|{table_i}|{row_i-1}"))
        elif table_i > 0:
            buttons.append(("⬅ Previous", f"{base}|{table_i-1}|{len(tables[table_i-1]['rows'])-1}"))
        buttons.append(("🏠 Overview", f"gfight|{role}|{key}"))
        if row_i + 1 < len(rows):
            buttons.append(("Next ➡", f"{base}|{table_i}|{row_i+1}", P))
        elif table_i + 1 < len(tables):
            buttons.append(("Next ➡", f"{base}|{table_i+1}|0", P))
        return fight_turn_embed(raid, key, table_i, row_i), _nav([buttons])

    if kind == "gdice":                    # boss picker for your pair
        role = parts[1]
        bosses = list(raid_defs.RAIDS[raid]["dice"])
        btns = [(b, f"gdicet|{role}|{b}", P) for b in bosses]
        rows = [btns[i:i + 3] for i in range(0, len(btns), 3)]
        rows.append([("⬅ My Fights", f"gf|{role}"), back_sec])
        return dice_boss_embed(raid), _nav(rows)

    if kind == "gdicet":
        role, boss = parts[1], parts[2]
        pair = ROLE_INFO[role]["pair"]
        d = raid_defs.RAIDS[raid]["dice"][boss][pair]
        rows = []
        if d.get("rows"):
            rows.append([("▶️ Start Turn Guide", f"gdiceturn|{role}|{boss}|0", P)])
        rows.append([("🎲 Other boss", f"gdice|{role}"),
                     ("⬅ My Fights", f"gf|{role}"), back_sec])
        return dice_table_embed(raid, boss, pair), _nav(rows)

    if kind == "gdiceturn":
        role, boss, row_i = parts[1], parts[2], int(parts[3])
        pair = ROLE_INFO[role]["pair"]
        rows = raid_defs.RAIDS[raid]["dice"][boss][pair]["rows"]
        base = f"gdiceturn|{role}|{boss}"
        buttons = []
        if row_i > 0:
            buttons.append(("⬅ Previous", f"{base}|{row_i-1}"))
        buttons.append(("🏠 Overview", f"gdicet|{role}|{boss}"))
        if row_i + 1 < len(rows):
            buttons.append(("Next ➡", f"{base}|{row_i+1}", P))
        return dice_turn_embed(raid, boss, pair, row_i), _nav([buttons])

    if kind == "gduo":                     # your 2v2 duo, straight away
        role = parts[1]
        duo = ROLE_INFO[role]["duo"]
        return (duo_table_embed(raid, duo),
                _nav([[("▶️ Start Turn Guide", f"gduoturn|{role}|0", P)],
                      [("⬅ My Fights", f"gf|{role}"), back_sec]]))

    if kind == "gduoturn":
        role, row_i = parts[1], int(parts[2])
        duo = ROLE_INFO[role]["duo"]
        rows = raid_defs.RAIDS[raid]["duos"][duo]["rows"]
        buttons = []
        if row_i > 0:
            buttons.append(("⬅ Previous", f"gduoturn|{role}|{row_i-1}"))
        buttons.append(("🏠 Overview", f"gduo|{role}"))
        if row_i + 1 < len(rows):
            buttons.append(("Next ➡", f"gduoturn|{role}|{row_i+1}", P))
        return duo_turn_embed(raid, duo, row_i), _nav([buttons])

    # Old right-side buttons (pair pickers etc.) on messages sent before this
    # update: send them to the role picker instead of asking for a pair.
    if kind in ("rdecks", "rdeck", "dicep", "dicet", "duot", "diceturn",
                "duoturn") or (kind in ("fights", "fight", "turn")
                               and len(parts) > 1 and parts[1] == "right"):
        return guide_screen("right")

    if kind == "left":
        return (base_embed(raid, "⬅️ Left Side",
                "Tanks & Hitters — deck and fights."),
                _nav([[("⚔️ Fights", "fights|left", P),
                       ("🃏 Deck Setup", "ldeck", P),
                       ("🎒 Gear", "lgear", P)], [back_sec]]))

    if kind == "lgear":                    # Tank / Hitter gear
        guide_set = raid_defs.RAIDS[raid].get("gear", {})
        if len(parts) > 1:
            return (gear_embed(raid, parts[1]),
                    _nav([[("⬅ Gear", "lgear"), ("⬅ Left Side", "left"),
                           back_sec]]))
        left = sorted(k for k in guide_set if k.endswith("_gear"))
        return (base_embed(raid, "🎒 Left Side — Gear", "Tank or Hitter?"),
                _nav([[(guide_set[k]["title"], f"lgear|{k}", P) for k in left],
                      [("⬅ Left Side", "left"), back_sec]]))

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

    if kind == "basics":                   # every role's gear, one place
        guide_set = raid_defs.RAIDS[raid].get("gear", {})
        right = [k for k in guide_set if not k.endswith("_gear")]  # right/ files
        left = [k for k in guide_set if k.endswith("_gear")]       # left/ files
        rows = []
        if right:
            rows.append([(guide_set[k]["title"], f"gear|{k}", P) for k in sorted(right)][:5])
        if left:
            rows.append([(guide_set[k]["title"], f"gear|{k}", P) for k in sorted(left)])
        rows.append([back_sec])
        return (base_embed(raid, "🎒 Gear Setups",
                "Suggested gear for every role:"), _nav(rows))

    if kind == "gear":
        return (gear_embed(raid, parts[1]),
                _nav([[("⬅ Gear Setups", "basics"), back_sec]]))

    if kind == "caps":                     # stat caps live on the main menu
        lvl = parts[1]
        others = [l for l in raid_defs.RAIDS[raid]["stat_caps"] if l != lvl]
        return (caps_embed(raid, lvl),
                _nav([[(f"See {o}", f"caps|{o}|menu") for o in sorted(others)],
                      [("⬅ Stat Caps", "capsmenu"), ("📚 Main menu", "top")]]))

    return raid_picker_embed(), _nav([[("📚 Raids", "top")]])
