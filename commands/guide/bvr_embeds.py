"""Blighted Veil Raid (BVR) guide screens — one embed builder per screen.

These only build embeds; the buttons and routing that string them together
live in commands/guide/bvr_nav.py. The content itself lives in
guides/raids/blighted/ (plan/ and gear/).
"""
import os

import discord

from guides.loader import RAIDS

from .embeds import PURPLE, SCHOOL_COLORS, base_embed, progress_bar

BVR = "Blighted Veil Raid"


def _r() -> dict:
    return RAIDS[BVR]


# ------------------------------ small helpers --------------------------------

# One marker per role, following the wizard's main school (first letters of
# the role name). Storm builds are purple, like the Ghastly turn cards.
_ROLE_ICONS = {
    "-ice": "🔵", "ice": "🔵",
    "lyth/mife": "🟢", "lyth": "🟢", "mife": "🟡",
    "stire": "🟣", "steath": "🟣", "stife": "🟣",
    "dyth": "⚫", "meath": "🟡", "feath": "🔴",
}


def _short(role: str) -> str:
    """'-ice (Pull Myth From Back)' -> '-ice'."""
    return role.split(" (")[0].strip()


def role_icon(role: str) -> str:
    return _ROLE_ICONS.get(_short(role).lower(), "🔹")


def _pair_text(cols) -> str:
    return " + ".join(f"{role_icon(c)} **{_short(c)}**" for c in cols)


def _order_text(cols) -> str:
    return "  →  ".join(f"{role_icon(c)} **{c}**" for c in cols)


def _school_line(school: str) -> str:
    r = _r()
    return f"{r['school_emoji'][school]} {school}"


def _note_line(note: str) -> str:
    """Sheet notes starting with 'C:' are callouts; the rest are plain tips."""
    if note.startswith("C:"):
        return f"📣 **Callout:** {note[2:].strip()}"
    return f"📝 {note}"


def _turn_field(cols, row, extra_note: str | None = None):
    """One row of a turn table -> (field name, value)."""
    label = f"🎯 Turn {row[0]}"
    if len(row) == 2:                       # both players do the same thing
        lines = [f"👥 **Both:** {row[1]}"]
    else:
        lines = [f"{role_icon(c)} **{_short(c)}:** {row[i]}"
                 for i, c in enumerate(cols, start=1)]
        if len(row) > 3 and row[3]:
            lines.append(f"📌 {row[3]}")
    if extra_note:
        lines.append(_note_line(extra_note))
    return label, "\n".join(lines)


def _discard_field(cols, discard):
    # Full column names here, so notes like "(main ice no discard)" stay
    # right next to the discard list.
    lines = [f"{role_icon(c)} **{c}:** {d}" for c, d in zip(cols, discard)]
    return "🗑️ Discard", "\n".join(lines)


def _turn_card(title: str, cols, rows, i: int, description: str = "",
               discard=None, color: int | None = None,
               note: str | None = None) -> discord.Embed:
    """One turn as a full-width card, in the same style as the Ghastly
    turn viewer (role order first, then one line per role)."""
    row = rows[i]
    bar = f"{progress_bar(i, len(rows))}  **Step {i + 1} / {len(rows)}**"
    e = base_embed(BVR, f"{title} — Turn {row[0]}",
                   bar + (f"\n{description}" if description else ""))
    if color is not None:
        e.color = color
    e.add_field(name="👥 Role order", value=_order_text(cols), inline=False)
    if i == 0 and discard:                  # discards happen before turn 1
        name, value = _discard_field(cols, discard)
        e.add_field(name=name, value=value, inline=False)
    if len(row) == 2:
        e.add_field(name="📌 Both players", value=str(row[1]), inline=False)
    else:
        for k, c in enumerate(cols, start=1):
            e.add_field(name=f"{role_icon(c)} {c}", value=str(row[k]),
                        inline=False)
        if len(row) > 3 and row[3]:
            e.add_field(name="📌 Heads-up", value=str(row[3]), inline=False)
    if note:
        if note.startswith("C:"):
            e.add_field(name="📣 Callout", value=note[2:].strip(),
                        inline=False)
        else:
            e.add_field(name="📝 Note", value=note, inline=False)
    e.set_footer(text=_r()["credit"])
    return e


# ------------------------------ top level ------------------------------------

def home_embed() -> discord.Embed:
    r = _r()
    return base_embed(BVR, f"📖 {BVR}",
                      f"Lvl {r['level']} raid • {r['players']} players\n\n"
                      "**Which side are you on?**\n"
                      "🌀 **Spirit** — Outside (same job for everyone)\n"
                      "🔥 **Elemental** — Inside (pick your strategy + role)")


def team_embed() -> discord.Embed:
    r = _r()
    e = base_embed(BVR, "👥 Team Setup",
                   "8 players: **🌀 Spirit team** (Outside) + **🔥 Elemental team** "
                   "(Inside / Vanguard).")
    out = ["🌀 Spirit (Outside)", "───────────────"] + [
        f"{i}. {p}" for i, p in enumerate(r["outside_players"], 1)]
    e.add_field(name="\u200b", value="```\n" + "\n".join(out) + "\n```",
                inline=True)
    inside = ["🔥 Elemental (Inside)", "──────────────────"]
    for st in r["strategies"].values():
        inside.append(f"{st['name']}:")
        inside.append("  " + st["lineup"].replace(" · ", ", "))
    e.add_field(name="\u200b", value="```\n" + "\n".join(inside) + "\n```",
                inline=True)
    e.add_field(name="🔤 Inside names", value=r["inside_note"], inline=False)
    for name, text in r["raid_flow"]:
        e.add_field(name=name, value=text, inline=False)
    return e


# ------------------------------ inside team ----------------------------------

def _strategy_lines(sk: str) -> list[str]:
    """Short 'what's in this strategy' summary: Oni pairs + Roots pairs."""
    st = _r()["strategies"][sk]
    groups: dict[tuple, list] = {}
    for school in st["onis_order"]:
        cols = st["onis"][school]["cols"]
        groups.setdefault(tuple(sorted(_short(c) for c in cols)),
                          [cols, []])[1].append(school)
    lines = []
    for cols, schools in groups.values():
        ordered = sorted(cols, key=_short)
        lines.append(" + ".join(f"{role_icon(c)} {_short(c)}"
                                for c in ordered)
                     + " — " + ", ".join(_school_line(x) for x in schools))
    return lines


def inside_embed() -> discord.Embed:
    r = _r()
    e = base_embed(BVR, "🔥 Elemental Team — Inside",
                   "**Which strategy are you running?** Here's what each "
                   "one looks like — **Strategy 1** is the most used.")
    for k, st in r["strategies"].items():
        star = "⭐ " if st["popular"] else ""
        e.add_field(name=f"{star}{st['name']} — {st['lineup']}",
                    value="\n".join(_strategy_lines(k)), inline=False)
    return e


def role_embed(sk: str, role: str) -> discord.Embed:
    st = _r()["strategies"][sk]
    onis = ", ".join(_school_line(x) for x in oni_role_schools(sk, role))
    roots = ""
    for key, rt in st["roots"].items():
        if role in (_short(c) for c in rt["cols"]):
            partner = [c for c in rt["cols"] if _short(c) != role]
            roots = f"{ROOTS_LABELS[key]} with {_pair_text(partner)}"
    return base_embed(BVR, f"{role_icon(role)} {role}",
                      f"**Onis:** {onis}\n**Roots:** {roots}\n\n"
                      "Pick what you need:")


def strategy_embed(sk: str) -> discord.Embed:
    st = _r()["strategies"][sk]
    star = "⭐ " if st["popular"] else ""
    return base_embed(BVR, f"{star}{st['name']}",
                      f"{st['lineup']}\n\n**Which role are you?** "
                      "Everything after this is just for your role.")


def oni_roles(sk: str) -> list[str]:
    """Roles that fight Onis in this strategy, in order of first appearance."""
    st = _r()["strategies"][sk]
    seen: list[str] = []
    for school in st["onis_order"]:
        for c in st["onis"][school]["cols"]:
            if _short(c) not in seen:
                seen.append(_short(c))
    order = st["lineup"].split(" · ")          # show in lineup order
    return sorted(seen, key=lambda x: order.index(x) if x in order else 99)


def oni_role_schools(sk: str, role: str) -> list[str]:
    st = _r()["strategies"][sk]
    return [s for s in st["onis_order"]
            if role in (_short(c) for c in st["onis"][s]["cols"])]


def oni_list_embed(sk: str, role: str) -> discord.Embed:
    r = _r()
    st = r["strategies"][sk]
    e = base_embed(BVR, f"⚔️ {st['name']} — {role_icon(role)} {role}",
                   "**Which Oni are you fighting?**")
    for school in oni_role_schools(sk, role):
        cols = st["onis"][school]["cols"]
        partner = [c for c in cols if _short(c) != role]
        e.add_field(name=f"{r['school_emoji'][school]} {school} — "
                         f"{r['oni_names'][school]}",
                    value="with " + _pair_text(partner), inline=True)
    return e


def _oni_title(school: str) -> str:
    r = _r()
    return f"{r['school_emoji'][school]} {school} — {r['oni_names'][school]}"


def oni_embed(sk: str, school: str) -> discord.Embed:
    r = _r()
    st = r["strategies"][sk]
    o = st["onis"][school]
    e = base_embed(BVR, _oni_title(school),
                   f"**{st['name']}**  •  " + _pair_text(o["cols"]))
    e.color = SCHOOL_COLORS.get(school.lower(), PURPLE)
    e.add_field(name="👥 Role order", value=_order_text(o["cols"]),
                inline=False)
    name, value = _discard_field(o["cols"], o["discard"])
    e.add_field(name=name, value=value, inline=False)
    for row in o["rows"]:
        n, v = _turn_field(o["cols"], row)
        e.add_field(name=n, value=v, inline=False)
    return e


def oni_turn_embed(sk: str, school: str, i: int) -> discord.Embed:
    st = _r()["strategies"][sk]
    o = st["onis"][school]
    return _turn_card(f"{_oni_title(school)} ({st['name']})", o["cols"],
                      o["rows"], i, discard=o["discard"],
                      color=SCHOOL_COLORS.get(school.lower(), PURPLE))


ROOTS_LABELS = {"spirit": "🌀 Spirit Roots team", "ele": "🔥 Ele Roots team"}


def roots_embed(sk: str, key: str) -> discord.Embed:
    st = _r()["strategies"][sk]
    rt = st["roots"][key]
    e = base_embed(BVR, f"🌱 Roots — {ROOTS_LABELS[key]}",
                   f"**{st['name']}**  •  " + _pair_text(rt["cols"]))
    e.color = SCHOOL_COLORS["storm"]
    e.add_field(name="👥 Role order", value=_order_text(rt["cols"]),
                inline=False)
    name, value = _discard_field(rt["cols"], rt["discard"])
    e.add_field(name=name, value=value, inline=False)
    for row in rt["rows"]:
        n, v = _turn_field(rt["cols"], row, rt["notes"].get(row[0]))
        e.add_field(name=n, value=v, inline=False)
    mana = "  •  ".join(f"{role_icon(c)} **{_short(c)}** {m}"
                        for c, m in zip(rt["cols"], rt["mana"]))
    e.add_field(name="💧 Mana", value=mana, inline=False)
    return e


def roots_turn_embed(sk: str, key: str, i: int) -> discord.Embed:
    st = _r()["strategies"][sk]
    rt = st["roots"][key]
    row = rt["rows"][i]
    return _turn_card(f"🌱 Roots — {ROOTS_LABELS[key]} ({st['name']})",
                      rt["cols"], rt["rows"], i, discard=rt["discard"],
                      color=SCHOOL_COLORS["storm"],
                      note=rt["notes"].get(row[0]))


def role_deck_embed(sk: str, role: str) -> discord.Embed:
    st = _r()["strategies"][sk]
    want = ("Ice", "-Ice") if role == "-ice" else (role,)
    e = base_embed(BVR, f"🃏 {role_icon(role)} {role} — Deck",
                   f"{st['name']} • main-deck spells and treasure cards (TC).")
    for name, d in st["decks"].items():
        if name not in want:
            continue
        lines = [f"**Deck:** {', '.join(d['spells'])}",
                 f"**TC:** {', '.join(d['tc'])}"]
        lines += [f"📝 {n}" for n in d.get("notes", [])]
        e.add_field(name=d["label"], value="\n".join(lines), inline=False)
    if role == "-ice":
        for t, x in st.get("deck_notes", []):
            e.add_field(name=f"📝 {t}", value=x, inline=False)
    return e


def dryads_embed() -> discord.Embed:
    r = _r()
    e = base_embed(BVR, "🌸 Dryad Deposits", r["dryad_key"])
    w = max(len(s) for s, _, _ in r["dryads"])
    rows = ["Dryad".ljust(w + 2) + "1st flower".ljust(12) + "2nd flower",
            "-" * (w + 2 + 12 + 10)]
    for s, a, b in r["dryads"]:
        rows.append(s.ljust(w + 2) + a.ljust(12) + b)
    e.add_field(name="Flowers / essence needed",
                value="```\n" + "\n".join(rows) + "\n```", inline=False)
    e.add_field(name="🗺️ Maps",
                value="Tap a floor below to see the Elemental Plane map.",
                inline=False)
    return e


def map_embed(key: str):
    """Returns (embed, asset path relative to assets/)."""
    path, title = _r()["maps"][key]
    e = base_embed(BVR, f"🗺️ {title}")
    e.set_image(url=f"attachment://{os.path.basename(path)}")
    return e, path


# ------------------------------ callouts -------------------------------------

def callouts_embed() -> discord.Embed:
    r = _r()
    e = base_embed(BVR, "📣 Callouts & Hanging Effects", r["callout_how"])
    key = "  •  ".join(f"{eff} = {school}" for eff, school in
                       r["effect_schools"])
    e.add_field(name="Effect → school", value=key, inline=False)
    for title, text in r["callout_examples"]:
        e.add_field(name=f"E.g. {title}", value=text, inline=False)
    e.add_field(name="🔁 When it swaps", value=r["swap_rules"], inline=False)
    lines = []
    for player, info in r["outside"]["players"].items():
        cues = "  •  ".join(f"{ess} on **{cue}**" for ess, cue in info["final"])
        lines.append(f"**{player}:** {cues}")
    e.add_field(name="🌀 Who's waiting on each callout (Spirit team)",
                value="\n".join(lines), inline=False)
    return e


# ------------------------------ outside team ---------------------------------

def outside_embed() -> discord.Embed:
    return base_embed(
        BVR, "🌀 Spirit Team — Outside",
        "Everyone on the Outside does the same job:\n"
        "1. 💣 **Opening** — make school bombs, blow up the mob shrines and "
        "grab the statues.\n"
        "2. 🚪 **Oni Doors** — let the right mobs through the gates for the "
        "Inside team.\n"
        "3. 🔒 **Final Phase** — hold essences and drop them in the pagoda "
        "urns on the Inside team's callouts.\n\n"
        "Pick what you need:")


def outside_opening_embed() -> discord.Embed:
    r = _r()
    o = r["outside"]
    e = base_embed(BVR, "💣 Opening — bombs & shrines",
                   "Do this right away. Each side makes one bomb chain, "
                   "grabs the essence and statue, then goes back to defend.")
    for player in r["outside_players"]:
        info = o["players"][player]
        e.add_field(name=f"🧭 {player}",
                    value=f"{info['summary']}\n*{info['after']}*",
                    inline=False)
    e.add_field(name="📝 Every side",
                value="Grab **1 essence** and let **1 mob spawn** before "
                      "blowing up a spawner, then grab the **Shrine "
                      "Statue**. " + o["mob_reason"], inline=False)
    e.add_field(name="⚠️ Wrong essence", value=o["wrong_essence"],
                inline=False)
    return e


def outside_final_all_embed() -> discord.Embed:
    r = _r()
    o = r["outside"]
    e = base_embed(BVR, "🔒 Final Phase — pagoda urns", o["final_how"])
    for player in r["outside_players"]:
        info = o["players"][player]
        lines = [f"Grab the **{ess}** → drop it on **\"{cue}\"**"
                 for ess, cue in info["final"]]
        if info.get("final_note"):
            lines.append(f"⚡ {info['final_note']}")
        e.add_field(name=f"🧭 {player}", value="\n".join(lines),
                    inline=False)
    return e


def _door_lines(compact: bool = True) -> list[str]:
    r = _r()
    em = r["school_emoji"]
    out = []
    for d in r["outside"]["door_logic"]:
        lit = " + ".join(f"{em[s]} {s}" for s in d["lit"])
        blow = " & ".join(f"{em[s]} {s}" for s in d["reblow"])
        mobs = " · ".join(f"{em[s]} {s} → {oni} Oni" for s, oni in d["mobs"])
        skip = " / ".join(d["skip"])
        out.append(f"**{lit} lit** → re-blow {blow} spawners.\n"
                   f"Let in: {mobs}.\n"
                   f"*(No {skip} mobs needed for the gate.)*")
    return out


def outside_doors_embed() -> discord.Embed:
    o = _r()["outside"]
    e = base_embed(BVR, "🚪 Oni Doors — which tablets are lit?",
                   o["door_intro"])
    for text in _door_lines():
        head, _, body = text.partition("\n")
        e.add_field(name=head.replace("**", ""), value=body, inline=False)
    return e


def outside_general_embed() -> discord.Embed:
    r = _r()
    o = r["outside"]
    em = r["school_emoji"]
    e = base_embed(BVR, "🌿 Wisps, Shrines & Gates")
    e.add_field(name="🟢 Binding Wisps",
                value="\n".join(f"• {t}" for t in o["wisps"]), inline=False)
    e.add_field(name="🏯 Mob Shrines",
                value="\n".join(f"• {t}" for t in o["shrines"]), inline=False)
    chain = [f"Open **{em[d]} {d}** door? Grab {em[b]} {b} bomb → blow up "
             f"{em[s]} {s} spawner" for d, b, s in o["bomb_chain"]]
    e.add_field(name="💣 Bomb chain", value="\n".join(chain), inline=False)
    gates = [f"**{oni}** ← {em[s]} {s} mob" for oni, s in o["torii_gates"]]
    e.add_field(name="⛩️ Torii Gates",
                value=o["torii_how"] + "\n" + "\n".join(gates), inline=False)
    e.add_field(name="🔘 Binding Buttons",
                value="\n".join(f"• {t}" for t in o["buttons"]), inline=False)
    swaps = "  •  ".join(f"{em[s]} {s} → {eff}" for s, eff in o["swaps"])
    e.add_field(name="🔁 Swapping effects (essence at the urns)",
                value=swaps, inline=False)
    return e


# ------------------------------ gear -----------------------------------------

_SLOT_ICONS = {"Hat": "🎩", "Robe": "👘", "Boots": "👢", "Wand": "🪄",
               "Athame": "🗡️", "Amulet": "📿", "Ring": "💍", "Deck": "🃏",
               "Mount": "🐴", "Pet": "🐾"}


def gear_menu_embed() -> discord.Embed:
    r = _r()
    e = base_embed(BVR, "📐 Gear",
                   "Pick your role. **Stats rows are the minimum you need.**")
    for g in r["gear"].values():
        labels = ", ".join(b["label"] for b in g["builds"].values())
        e.add_field(name=g["title"], value=labels, inline=False)
    return e


def gear_group_embed(group: str) -> discord.Embed:
    g = _r()["gear"][group]
    e = base_embed(BVR, g["title"], g["intro"])
    e.add_field(name="Builds",
                value="  •  ".join(b["label"] for b in g["builds"].values()),
                inline=False)
    return e


def gear_build_embed(group: str, key: str) -> discord.Embed:
    g = _r()["gear"][group]
    b = g["builds"][key]
    e = base_embed(BVR, f"{g['title']} — {b['label']}")
    for slot in b["slots"]:
        name, item, jewels = slot[0], slot[1], slot[2]
        parts = []
        if item:
            parts.append(f"**{item}**")
        if jewels:
            parts.append(jewels)
        value = "\n".join(parts) or "—"
        if len(slot) > 3 and slot[3]:
            value += f"\n*{slot[3]}*"
        e.add_field(name=f"{_SLOT_ICONS.get(name, '🔹')} {name}",
                    value=value[:1024], inline=True)
    if b.get("min_stats"):
        e.add_field(name="📊 Minimum stats", value=b["min_stats"],
                    inline=False)
    if b.get("link"):
        e.add_field(name="🔗 WizBuilder",
                    value=f"[Open this build]({b['link']})", inline=False)
    return e
