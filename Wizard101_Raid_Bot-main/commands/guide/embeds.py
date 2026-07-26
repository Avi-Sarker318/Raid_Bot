"""Every embed the /guide browser can show — one builder per screen.

These only build embeds; the buttons and routing that string them together
live in commands/guide/nav.py.
"""
import discord

from guides.loader import RAIDS

from .tables import grid, table_fields

PURPLE = 0x8A2BE2


SCHOOL_COLORS = {
    "fire": 0xE74C3C,
    "storm": 0x8E44AD,
    "ice": 0x3498DB,
    "death": 0x7F8C8D,
    "myth": 0xF1C40F,
    "life": 0x27AE60,
    "balance": 0xC47F17,
}


def _role_icon(role: str) -> str:
    name = role.lower()
    if "storm" in name:
        return "🟣"
    if "fire" in name:
        return "🔴"
    if "ice" in name:
        return "🔵"
    if "death" in name:
        return "⚫"
    if "myth" in name:
        return "🟡"
    if "life" in name:
        return "🟢"
    if "balance" in name:
        return "🟠"
    if "support" in name:
        return "🛡️"
    return "🔹"


def _turn_card(raid: str, title: str, table: dict, row_index: int,
               description: str = "", extra_fields=None) -> discord.Embed:
    """Render exactly one existing strategy row as a clean raid turn card."""
    cols = list(table["cols"])
    rows = list(table["rows"])
    row = rows[row_index]
    turn_name = table.get("turn", "Turn")
    table_name = table.get("name")
    heading = f"{title} — {turn_name} {row[0]}"
    if table_name:
        heading = f"{title} — {table_name} — {turn_name} {row[0]}"
    e = base_embed(raid, heading, description)
    e.color = SCHOOL_COLORS["storm"]
    e.add_field(
        name="👥 Role order",
        value="  →  ".join(f"{_role_icon(c)} **{c}**" for c in cols),
        inline=False,
    )
    if len(row) < len(cols) + 1:
        e.add_field(name="📌 Instruction", value=str(row[-1]), inline=False)
    else:
        for i, role in enumerate(cols, 1):
            action = "—" if row[i] is None else str(row[i]).strip() or "—"
            e.add_field(name=f"{_role_icon(role)} {role}", value=action, inline=False)
    for field in extra_fields or []:
        name, value = field[0], field[1]
        inline = field[2] if len(field) > 2 else False
        e.add_field(name=name, value=str(value)[:1024], inline=inline)
    e.set_footer(text=f"{_credit(raid)} • Step {row_index + 1} of {len(rows)}")
    return e


def fight_turn_embed(raid: str, key: str, table_index: int, row_index: int) -> discord.Embed:
    f = RAIDS[raid]["fights"][key]
    tables = [f[t] for t in ("table", "table2") if t in f] + f.get("tables", [])
    return _turn_card(raid, f["title"], tables[table_index], row_index,
                      f.get("description", ""))


def dice_turn_embed(raid: str, boss: str, pair: str, row_index: int) -> discord.Embed:
    d = RAIDS[raid]["dice"][boss][pair]
    a, b = (("Support", "Storm 1") if pair == "s1" else ("Storm 2", "Storm 3"))
    hp = RAIDS[raid]["dice"][boss]["hp"]
    return _turn_card(raid, f"🎲 {boss} ({hp} HP)",
                      {"cols": [a, b], "rows": d["rows"]}, row_index)


def duo_turn_embed(raid: str, duo: str, row_index: int) -> discord.Embed:
    f = RAIDS[raid]["duos"][duo]
    desc = f"**{f['puller']}**" + (f" • {f['note']}" if f["note"] else "")
    return _turn_card(raid, f"⚔️ {duo} Fight — {f['pair']}",
                      {"cols": f["cols"], "rows": f["rows"]}, row_index, desc)


def _credit(raid: str) -> str:
    return RAIDS[raid].get("credit", "")



def base_embed(raid: str, title: str, desc: str = "") -> discord.Embed:
    e = discord.Embed(title=title, description=desc or None, color=PURPLE)
    e.set_footer(text=_credit(raid))
    return e


def fields_into(e: discord.Embed, fields) -> discord.Embed:
    """Add fields to an embed. Each entry is (name, value) — stacked
    full-width — or (name, value, inline) to place it side-by-side."""
    for f in fields:
        name, value = f[0], f[1]
        inline = f[2] if len(f) > 2 else False
        e.add_field(name=name, value=value[:1024], inline=inline)
    return e


# --------------------------- screens ---------------------------------------


# --------------------------- screens -----------------------------

def raid_picker_embed() -> discord.Embed:
    return discord.Embed(
        title="📚 Raid Guides",
        description="Which raid do you want to see? More guides coming soon.",
        color=PURPLE)


def sections_embed(raid: str) -> discord.Embed:
    r = RAIDS[raid]
    return base_embed(raid, f"📖 {raid}",
                      f"Lvl {r.get('level','?')} raid • "
                      f"{r.get('players','?')} players • Pick a section:")


def right_decks_embed(raid: str, deck: str | None = None) -> discord.Embed:
    decks = RAIDS[raid]["decks_right"]
    if deck is None:
        return base_embed(raid, "🃏 Right Side — Deck Setups",
                          "Pick a role for its card list:")
    e = base_embed(raid, f"🃏 {deck} Deck")
    return fields_into(e, decks[deck])


def left_deck_embed(raid: str, school: str | None = None) -> discord.Embed:
    r = RAIDS[raid]
    if school is None:
        base = ", ".join(
            (s["f"] if "f" in s else f"[{s['s']}]") for s in r["left_deck_slots"])
        e = base_embed(raid, "⬅️ Left Side Deck",
                       "Pick your school below — bracketed slots swap to "
                       "your school's cards.")
        e.add_field(name="Base layout", value=base, inline=False)
        e.add_field(name="Also required", value=r["left_deck_notes"],
                    inline=False)
        return e
    sc = r["left_schools"][school]
    cards = [(sc[s["s"]] if "s" in s else s["f"]) for s in r["left_deck_slots"]]
    marked = [f"**{c}**" if "s" in r["left_deck_slots"][i] else c
              for i, c in enumerate(cards)]
    e = base_embed(raid, f"{sc['emoji']} {school} — Left Side deck",
                   "Your school's cards are **bold**; the rest is the same "
                   "for everyone:")
    e.add_field(name="Deck (10 slots, in order)",
                value=", ".join(marked), inline=False)
    e.add_field(name="Also required", value=r["left_deck_notes"], inline=False)
    return e


def fight_embed(raid: str, key: str) -> discord.Embed:
    f = RAIDS[raid]["fights"][key]
    e = base_embed(raid, f["title"], f.get("description", ""))
    # Turn tables render as inline fields — easy to read, never wraps badly.
    tabs = [f[t] for t in ("table", "table2") if t in f] + f.get("tables", [])
    extra = f.get("fields", [])

    # Some entries (notably Dice and 2v2) normally open a specialized picker.
    # If routing ever sends them here, show a useful message instead of a
    # title-only embed whose content appears as None/blank.
    if not tabs and not extra:
        fallback = {
            "dice": "Choose a dice boss from the fight menu to view its turn-by-turn plan.",
            "2v2": "Choose a 2v2 pairing from the fight menu to view its turn-by-turn plan.",
        }.get(key, "No fight instructions have been added yet.")
        e.add_field(name="Instructions", value=fallback, inline=False)
        return e
    # Discord allows 25 fields per embed; keep room for the fight's own notes.
    budget = 25 - len(extra)
    for t in tabs:
        rows = table_fields(t)
        if len(rows) > budget:
            e = fields_into(e, rows[:max(budget - 1, 0)])
            leftover = rows[max(budget - 1, 0):]
            summary = "\n".join(
                f"**{n}** — " + v.replace("\n", " · ").replace("**", "")
                for n, v, *_ in leftover)
            e.add_field(name="…continued", value=summary[:1024], inline=False)
            budget = 0
            break
        e = fields_into(e, rows)
        budget -= len(rows)
    return fields_into(e, extra)


def roshambo_school_embed(school: str):
    """One school's strengths/weaknesses page. The school's PNG sits at the
    top-right (thumbnail). Matchup schools are shown as *italic* names.
    Returns (embed, filename_to_attach)."""
    FIRE, ICE, STORM = "*Fire*", "*Ice*", "*Storm*"
    LIFE, DEATH, MYTH = "*Life*", "*Death*", "*Myth*"

    DATA = {
        "fire": ("🔥 Fire", 0xE74C3C,
            f"Damage Overtimes, Shield Removal, Trap Removal — {MYTH}, {ICE}",
            f"Damage Overtimes, Healing Overtimes, Blade Debuffs, Blades — "
            f"{STORM}, {LIFE}", DEATH),
        "ice": ("❄️ Ice", 0x3498DB,
            f"Blade Removal, Blade Debuff Removals, Best Resist — {DEATH}, "
            f"{STORM}",
            f"Traps, Damage Overtimes, Healing Overtimes, Shields — {MYTH}, "
            f"{FIRE}", LIFE),
        "storm": ("⚡ Storm", 0x8E44AD,
            f"Damage Overtime Removals, Healing Overtime Removal, Best Damage "
            f"— {LIFE}, {FIRE}",
            f"Blades, Traps, Blade Debuffs, Shields — {DEATH}, {ICE}", MYTH),
        "life": ("🌿 Life", 0x27AE60,
            f"Trap Removal, Damage Overtime Removal, Healing Spells, Best "
            f"Health — {FIRE}, {MYTH}",
            f"Shields, Healing Overtime, Blades, Blade Debuffs — {DEATH}, "
            f"{STORM}", LIFE),
        "death": ("💀 Death", 0x2C3E50,
            f"Blade Removal, Blade Debuffs, Draining Spells, Healing Overtime "
            f"Removals — {LIFE}, {STORM}",
            f"Traps, Damage Overtime, Shields, Blade Debuffs — {ICE}, {MYTH}",
            DEATH),
        "myth": ("🔮 Myth", 0xF1C40F,
            f"Shield Removal, Blade Debuff Removal, Bomb Overtime, Second Hit "
            f"Spells. Best Balanced Stat Damage School — {DEATH}, {ICE}",
            f"Traps, Blades, Healing Overtimes, Damage Overtime — {FIRE}, "
            f"{LIFE}", STORM),
    }

    if school == "balance":
        e = discord.Embed(
            title="⚖️ Balance — the Effect School",
            description="The all-knowing, echo school.",
            color=0x922B21)   # maroon
        e.add_field(name="Strength",
                    value="If your deck is built correctly, **you win.**",
                    inline=False)
        e.add_field(name="Weakness",
                    value="If your deck doesn't work correctly, **you lose.**",
                    inline=False)
        e.set_footer(text="Neutralize matchups with weaving + spell-writing.")
        e.set_thumbnail(url="attachment://balance.png")
        return e, "balance.png"

    title, color, strengths, weaknesses, hard = DATA[school]
    e = discord.Embed(title=title, color=color)
    e.add_field(name="Strengths", value=strengths, inline=False)
    e.add_field(name="Weaknesses", value=weaknesses, inline=False)
    e.add_field(name="Hard time against", value=hard, inline=False)
    e.set_footer(text="Neutralize matchups with weaving + spell-writing.")
    e.set_thumbnail(url=f"attachment://{school}.png")
    return e, f"{school}.png"


def cantrip_embed() -> discord.Embed:
    """Full level 1→7 cantrip leveling walkthrough. Sourced from Final
    Bastion's cantrip leveling guide."""
    e = discord.Embed(
        title="✨ Cantrip Tutorial — reaching Rank 7",
        description=(
            "Cantrips are out-of-combat spells cast with **energy**. Raids "
            "need **Rank 7** (lets you cast every needed cantrip). You must be "
            "**level 25+** to start.\n\n"
            "**Getting started:** talk to **Abner K. Doodle** in The Commons "
            "for Rank 1 + the *Cantrips101* quest, which sends you to "
            "**Hampshire Buttersfield** in Wysteria. You earn XP by casting "
            "cantrips **of your current rank** (XP gained = the spell's energy "
            "cost)."),
        color=PURPLE)
    e.add_field(
        name="🔑 Key idea",
        value="Always cast spells **matching your rank** — lower-rank spells "
              "give no XP. Mix trained cantrips, TC cantrips, and battle "
              "cantrips (dropped in raids / from the battle crafter).",
        inline=False)
    e.add_field(
        name="Rank 1 → 2",
        value="Do **Cantrips102** from Hampshire (6 energy). Cheapest: cast "
              "**Magic Touch** 8×, then **Flip** or **School Symbol** 4×. "
              "*(Magic Touch is free outside Guild houses since Fall 2022.)*",
        inline=False)
    e.add_field(
        name="Rank 2 → 3",
        value="~100 XP. Cheapest: **Rainmaker / Paper / Rock / Scissors** "
              "(2 XP each → ~50 casts; 3,000 gold each from Hampshire). "
              "Fastest: **Heal & Mana I** TC (15 XP) or **Healing II** TC "
              "(20 XP).",
        inline=False)
    e.add_field(
        name="Rank 3 → 5",
        value="Use **Rank 3 & 5 battle cantrips** (easy L1/L2 TCs from the "
              "battle crafter), plus trained cantrips of your rank. Keep "
              "casting your-rank spells until you tick over.",
        inline=False)
    e.add_field(
        name="Rank 5 → 7",
        value="Fastest: **Sigil Support TC** (Rank 7, 42 energy) — **Dual "
              "Strike 3** / **Restoring Rain 3** (42 XP each). No Sigil TCs? "
              "Craft **Healing IV** TCs (40 XP) — needs the *Saviour of the "
              "Sands* badge from finishing Mirage.",
        inline=False)
    e.add_field(
        name="🎯 Stop at Rank 7",
        value="Rank 7 casts everything raids need. Going past it only helps "
              "completionists — keep Heal/Mana as separate TCs instead.",
        inline=False)
    e.set_footer(text="Full guide: Final Bastion — Wizard101 Cantrips "
                      "Levelling Guide")
    return e


def dice_fights_embed(raid: str) -> discord.Embed:
    return base_embed(
        raid, "🎲 Dice Fights",
        "Each boss has a different plan. **Which boss are you getting?**\n"
        "Rule of thumb: **YOU CAN ALWAYS DARKWIND!** (credit @friedchicken935)")


def team_embed(raid: str) -> discord.Embed:
    """Boxed side-by-side team columns showing the raid's full roster —
    the reference layout. Groups roles by their (Right)/(Left)/(Spirit)/
    (Elemental)/Outside/Vanguard tag."""
    from scheduling.views.formats.loader import roles_for
    import re as _re

    roles = list(roles_for(raid))

    def group_of(role):
        m = _re.search(r"\(([^)]+)\)\s*$", role)
        if m:
            return m.group(1)
        first = role.split()[0] if role.split() else ""
        return first if first in ("Outside", "Vanguard") else "Team"

    def clean(role):
        return _re.sub(r"\s*\([^)]+\)\s*$", "", role).strip()

    label = {"Right": "➡️ Right Side", "Left": "⬅️ Left Side",
             "Spirit": "🌀 Spirit Team", "Elemental": "🔥 Elemental Team",
             "Outside": "🌐 Outside", "Vanguard": "🛡️ Vanguard"}

    groups: dict = {}
    for r in roles:
        groups.setdefault(group_of(r), []).append(r)

    e = base_embed(raid, "👥 Team Setup",
                   f"The full {len(roles)}-player roster. Each team's roles "
                   "are listed below — use this to organize who plays what.")
    for grp, grp_roles in groups.items():
        head = label.get(grp, grp)
        lines = [head, "─" * len(head)]
        for i, r in enumerate(grp_roles, 1):
            lines.append(f"{i}. {clean(r)}")
        e.add_field(name="\u200b", value="```\n" + "\n".join(lines) + "\n```",
                    inline=True)
    return e



def dice_boss_embed(raid: str) -> discord.Embed:
    """Header for the dice-room boss picker — lists every boss with its HP
    so the picker itself reads as a turn card, never an empty prompt."""
    e = base_embed(raid, "🎲 Dice Room — pick a boss",
                   "Each boss has its own turn-by-turn plan. "
                   "Tap a boss below to see it.\n"
                   "**Golden rule: YOU CAN ALWAYS DARKWIND!**")
    dice = RAIDS[raid].get("dice", {})
    for boss, info in dice.items():
        e.add_field(name=f"🎲 {boss}", value=f"{info['hp']} HP", inline=True)
    return e


def dice_pair_embed(raid: str, boss: str) -> discord.Embed:
    hp = RAIDS[raid]["dice"][boss]["hp"]
    return base_embed(raid, f"🎲 {boss} — {hp} HP",
                      "**What role are you?** You'll get your pair's plan.")


def dice_table_embed(raid: str, boss: str, pair: str) -> discord.Embed:
    d = RAIDS[raid]["dice"][boss][pair]
    a, b = (("Support", "Storm 1") if pair == "s1" else ("Storm 2", "Storm 3"))
    hp = RAIDS[raid]["dice"][boss]["hp"]
    e = base_embed(raid, f"🎲 {boss} ({hp} HP) — {a} & {b}")
    if d.get("avoid"):
        e.add_field(name="⛔ AVOID THIS!",
                    value="If you got pulled into this fight all you can do is "
                          "**Darkwind and spam hits.** *Good luck!*",
                    inline=False)
        e.add_field(name="Discard", value=d["d"][0], inline=False)
        return e
    for name, value, inline in table_fields({"cols": [a, b], "rows": d["rows"]}):
        e.add_field(name=name, value=value, inline=inline)
    db = d["d"][0] if d["d"][1] == "same" else d["d"][1]
    e.add_field(name="Discard", value=f"**{a}:** {d['d'][0]}\n**{b}:** {db}",
                inline=False)
    return e


def duo_picker_embed(raid: str) -> discord.Embed:
    r = RAIDS[raid]
    e = base_embed(raid, "⚔️ 2v2 Fights",
                   "⚠️ **DO NOT KILL UNTIL YOU KNOW THE CHEAT CODE!**\n"
                   "🗿 Touch the **Balance Attunement Stone BEFORE** the 2v2s.")
    e.add_field(name="Cheat codes", value=r["cheats_2v2"], inline=False)
    return e


def duo_table_embed(raid: str, duo: str) -> discord.Embed:
    f = RAIDS[raid]["duos"][duo]
    e = base_embed(raid, f"⚔️ {duo} Fight — {f['pair']}",
                   f"**{f['puller']}**" + (f" • {f['note']}" if f["note"] else ""))
    for name, value, inline in table_fields({"cols": f["cols"], "rows": f["rows"]}):
        e.add_field(name=name, value=value, inline=inline)
    if f["d"]:
        e.add_field(name="Discard",
                    value=f"**{f['cols'][0]}:** {f['d'][0]}\n"
                          f"**{f['cols'][1]}:** {f['d'][1]}", inline=False)
    e.add_field(name="Cheat codes", value=RAIDS[raid]["cheats_2v2"],
                inline=False)
    e.add_field(name="⚠️ Important",
                value="**Don't kill any until you know the cheat.**",
                inline=False)
    return e


def gear_embed(raid: str, key: str) -> discord.Embed:
    g = RAIDS[raid].get("gear", {})[key]
    e = base_embed(raid, g["title"], g["intro"])
    return fields_into(e, g["fields"])
