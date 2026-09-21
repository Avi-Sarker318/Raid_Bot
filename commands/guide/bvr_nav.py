"""Blighted Veil Raid (BVR) — /guide button routing.

`bvr_screen(parts)` handles every nav path that starts with `bvr|`. The
routing in nav.py hands the rest of the path over, so these screens ride on
the same restart-proof GuideNav button as the rest of the guide.

Paths (everything after the leading `bvr|`):

    home                          pick a side: Spirit (Outside) / Elemental
    in                            Elemental: pick Strategy 1 or 2
    s|<k>                         pick your role
    rp|<k>|<role>                 your role's hub
    mf|<k>|<role>                 your fights: Onis or Roots
    ol|<k>|<role>  o|<k>|<Oni>|<role>  ot|...|<i>   your Onis -> fight -> turns
    r|<k>|<pair>|<role>  rt|...|<i>                 your Roots -> turns
    md|<k>|<role>  mg|<k>|<role>  mgb|...           your deck / gear
    dry  map|<n>  call  team      dryads, maps, callouts, team setup
    out  oo  od  ofa  om          Spirit (Outside): same for everyone
    g  gg|<group>  gb|<group>|<build>               full gear browser
"""
from guides.loader import RAIDS

from . import bvr_embeds as E
from .nav import P, S, _nav

BVR = E.BVR

HOME = ("🏠 BVR", "bvr|home")

# role -> (gear group, specific build or None to let them pick)
MY_GEAR = {"-ice": ("ice", None), "Lyth/Mife": ("lyth_mife", None),
           "Stire": ("stire", None), "Steath": ("steath", None),
           "Stife": ("duos", "stife"), "Dyth": ("duos", "dyth")}
OTHER_RAIDS = ("📚 Other raids", "top")


def _grid(buttons, per_row: int = 3):
    """Split (label, path[, style]) buttons into rows of `per_row`."""
    return [buttons[i:i + per_row] for i in range(0, len(buttons), per_row)]


def _turn_nav(prefix: str, overview: str, i: int, total: int):
    """Previous / Overview / Next row for a turn viewer."""
    buttons = []
    if i > 0:
        buttons.append(("⬅ Previous", f"{prefix}|{i - 1}"))
    buttons.append(("🏠 Overview", overview))
    if i + 1 < total:
        buttons.append(("Next ➡", f"{prefix}|{i + 1}", P))
    return [buttons]


# Section colours + breadcrumbs — applied to every screen in one place.
_COLORS = {"in": 0xE67E22, "out": 0x1ABC9C, "g": 0x3498DB, "call": 0xF1C40F,
           "dry": 0xE91E63, "team": 0x8A2BE2}
_SECTION = {"in": "in", "s": "in", "rp": "in", "tm": "in", "ol": "in",
            "o": "in", "ot": "in", "r": "in", "rt": "in", "d": "in",
            "dry": "dry", "map": "dry", "out": "out", "op": "out", "oo": "out", "ofa": "out",
            "of": "out", "od": "out", "om": "out", "g": "g", "gg": "g",
            "gb": "g", "call": "call", "team": "team", "md": "in", "mf": "in",
            "mg": "in", "mgb": "in"}


def _crumb(kind: str, p: list[str]) -> str:
    r = RAIDS[BVR]
    trail = [BVR]
    if _SECTION.get(kind) == "in":
        trail.append("🔥 Elemental")
        if len(p) > 1 and kind not in ("in",):
            trail.append(r["strategies"][p[1]]["name"])
        if kind in ("rp", "ol", "o", "ot", "r", "rt", "md", "mg", "mgb", "mf"):
            role = p[2] if kind in ("rp", "ol", "md", "mg", "mgb", "mf") else p[3]
            trail.append(role)
        if kind in ("mf", "ol", "o", "ot", "r", "rt"):
            trail.append("My Fights")
        if kind in ("ol", "o", "ot"):
            trail.append("Onis")
        if kind in ("r", "rt"):
            trail.append("Roots")
        if kind in ("d", "md"):
            trail.append("Deck")
        if kind in ("mg", "mgb"):
            trail.append("Gear")
    elif _SECTION.get(kind) == "out":
        trail.append("🌀 Spirit")
        trail.append({"oo": "Opening", "od": "Oni Doors",
                      "ofa": "Final Phase", "om": "Wisps & Gates"}.get(kind, ""))
        if trail[-1] == "":
            trail.pop()
    elif _SECTION.get(kind) == "g":
        trail.append("Gear")
    elif kind == "call":
        trail.append("Callouts")
    elif kind in ("dry", "map"):
        trail.append("Dryads")
    elif kind == "team":
        trail.append("Team Setup")
    return " › ".join(trail)


def bvr_screen(parts: list[str]):
    """Route a `bvr|...` path and dress the embed (colour + breadcrumb)."""
    res = _route(parts)
    kind = parts[0] if parts else "home"
    e = res[0]
    sec = _SECTION.get(kind)
    if sec and e.color is not None and e.color.value == 0x8A2BE2:
        e.color = _COLORS.get(sec, 0x8A2BE2)
    if kind != "home":
        e.set_author(name=_crumb(kind, parts))
    if kind in ("o", "ot") and len(res) == 2:      # school icon, top-right
        fname = f"{parts[2 if kind == 'o' else 2].lower()}.png"
        e.set_thumbnail(url=f"attachment://{fname}")
        return e, res[1], fname
    return res


def _route(parts: list[str]):
    """Route a `bvr|...` nav path to (embed, view[, asset])."""
    r = RAIDS[BVR]
    kind = parts[0] if parts else "home"

    if kind == "home":
        return E.home_embed(), _nav([
            [("🌀 Spirit (Outside)", "bvr|out", P),
             ("🔥 Elemental (Inside)", "bvr|in", P)],
            [("👥 Team Setup", "bvr|team"), ("📐 Gear", "bvr|g"),
             ("📣 Callouts", "bvr|call")],
            [OTHER_RAIDS]])

    if kind == "team":
        return E.team_embed(), _nav([
            [("🔥 Elemental Team", "bvr|in"), ("🌀 Spirit Team", "bvr|out")],
            [HOME, OTHER_RAIDS]])

    # ------------------------------ inside team ------------------------------
    if kind == "in":
        strategies = [
            (f"{'⭐ ' if st['popular'] else ''}{st['name']}",
             f"bvr|s|{k}", P if st["popular"] else S)
            for k, st in r["strategies"].items()]
        return E.inside_embed(), _nav([
            strategies,
            [("🌸 Dryads & Maps", "bvr|dry"), ("📣 Callouts", "bvr|call"),
             HOME]])

    if kind == "s":                        # which role are you?
        k = parts[1]
        roles = [(f"{E.role_icon(x)} {x}", f"bvr|rp|{k}|{x}", P)
                 for x in E.oni_roles(k)]
        return E.strategy_embed(k), _nav([
            roles, [("⬅ Change strategy", "bvr|in"), HOME]])

    if kind == "rp":                       # your role's hub
        k, role = parts[1], parts[2]
        key = next(kk for kk, rt in r["strategies"][k]["roots"].items()
                   if role in (E._short(c) for c in rt["cols"]))
        return E.role_embed(k, role), _nav([
            [("⚔️ My Fights", f"bvr|mf|{k}|{role}", P),
             ("🃏 My Deck", f"bvr|md|{k}|{role}", P),
             ("🎒 My Gear", f"bvr|mg|{k}|{role}", P)],
            [("⬅ Change role", f"bvr|s|{k}"), HOME]])

    if kind == "mf":                       # your fights: Onis or Roots
        k, role = parts[1], parts[2]
        key = next(kk for kk, rt in r["strategies"][k]["roots"].items()
                   if role in (E._short(c) for c in rt["cols"]))
        return E.my_fights_embed(k, role), _nav([
            [("⚔️ Onis", f"bvr|ol|{k}|{role}", P),
             ("🌱 Roots", f"bvr|r|{k}|{key}|{role}", P)],
            [(f"⬅ {role}", f"bvr|rp|{k}|{role}"), HOME]])

    if kind == "md":
        k, role = parts[1], parts[2]
        return E.role_deck_embed(k, role), _nav([
            [(f"⬅ {role}", f"bvr|rp|{k}|{role}"), HOME]])

    if kind == "mg":                       # your gear: group or straight build
        k, role = parts[1], parts[2]
        group, build = MY_GEAR[role]
        back = (f"⬅ {role}", f"bvr|rp|{k}|{role}")
        if build:
            return E.gear_build_embed(group, build), _nav([[back, HOME]])
        builds = [(b["label"], f"bvr|mgb|{k}|{role}|{bk}", P)
                  for bk, b in r["gear"][group]["builds"].items()]
        return E.gear_group_embed(group), _nav(
            _grid(builds) + [[back, HOME]])

    if kind == "mgb":
        k, role, build = parts[1], parts[2], parts[3]
        group = MY_GEAR[role][0]
        return E.gear_build_embed(group, build), _nav([
            [("⬅ Builds", f"bvr|mg|{k}|{role}"),
             (f"⬅ {role}", f"bvr|rp|{k}|{role}"), HOME]])

    if kind == "ol":                       # which Oni are you fighting?
        k, role = parts[1], parts[2]
        oni_btns = [(f"{r['school_emoji'][s]} {s}",
                     f"bvr|o|{k}|{s}|{role}", P)
                    for s in E.oni_role_schools(k, role)]
        return E.oni_list_embed(k, role), _nav(
            _grid(oni_btns) + [[("⬅ My Fights", f"bvr|mf|{k}|{role}"), HOME]])

    if kind == "o":
        k, school, role = parts[1], parts[2], parts[3]
        return E.oni_embed(k, school), _nav([
            [("▶️ Start Turn Guide", f"bvr|ot|{k}|{school}|{role}|0", P)],
            [("⬅ Onis", f"bvr|ol|{k}|{role}"),
             (f"⬅ {role}", f"bvr|rp|{k}|{role}"), HOME]])

    if kind == "ot":
        k, school, role, i = parts[1], parts[2], parts[3], int(parts[4])
        rows = r["strategies"][k]["onis"][school]["rows"]
        return E.oni_turn_embed(k, school, i), _nav(_turn_nav(
            f"bvr|ot|{k}|{school}|{role}", f"bvr|o|{k}|{school}|{role}",
            i, len(rows)))

    if kind == "r":
        k, key, role = parts[1], parts[2], parts[3]
        return E.roots_embed(k, key), _nav([
            [("▶️ Start Turn Guide", f"bvr|rt|{k}|{key}|{role}|0", P)],
            [("⬅ My Fights", f"bvr|mf|{k}|{role}"), HOME]])

    if kind == "rt":
        k, key, role, i = parts[1], parts[2], parts[3], int(parts[4])
        rows = r["strategies"][k]["roots"][key]["rows"]
        return E.roots_turn_embed(k, key, i), _nav(_turn_nav(
            f"bvr|rt|{k}|{key}|{role}", f"bvr|r|{k}|{key}|{role}",
            i, len(rows)))

    if kind == "dry":
        return E.dryads_embed(), _nav([
            [("🗺️ Floor 1 map", "bvr|map|1", P),
             ("🗺️ Floor 2 map", "bvr|map|2", P)],
            [("⬅ Elemental Team", "bvr|in"), HOME]])

    if kind == "map":
        n = parts[1]
        embed, asset = E.map_embed(n)
        other = "2" if n == "1" else "1"
        return embed, _nav([
            [(f"🗺️ Floor {other} map", f"bvr|map|{other}", P)],
            [("🌸 Dryads", "bvr|dry"), HOME]]), asset

    if kind == "call":
        return E.callouts_embed(), _nav([
            [("🔥 Elemental Team", "bvr|in"), ("🌀 Spirit Team", "bvr|out")],
            [HOME]])

    # ------------------------------ outside team -----------------------------
    if kind == "out":
        return E.outside_embed(), _nav([
            [("💣 Opening", "bvr|oo", P), ("🚪 Oni Doors", "bvr|od", P),
             ("🔒 Final Phase", "bvr|ofa", P)],
            [("🌿 Wisps, Shrines & Gates", "bvr|om"), HOME]])

    if kind == "oo":
        return E.outside_opening_embed(), _nav([
            [("🚪 Oni Doors ➡", "bvr|od", P)],
            [("⬅ Spirit Team", "bvr|out"), HOME]])

    if kind == "ofa":
        return E.outside_final_all_embed(), _nav([
            [("⬅ Spirit Team", "bvr|out"), HOME]])

    if kind in ("op", "of"):               # old per-player buttons
        return _route(["out"])

    if kind == "od":
        return E.outside_doors_embed(), _nav([
            [("🔒 Final Phase ➡", "bvr|ofa", P)],
            [("⬅ Spirit Team", "bvr|out"), HOME]])

    if kind == "om":
        return E.outside_general_embed(), _nav([
            [("🚪 Oni Doors", "bvr|od"), ("⬅ Spirit Team", "bvr|out")],
            [HOME]])

    # ------------------------------ gear -------------------------------------
    if kind == "g":
        groups = [(g["title"], f"bvr|gg|{key}", P)
                  for key, g in r["gear"].items()]
        return E.gear_menu_embed(), _nav(_grid(groups, 2) + [[HOME]])

    if kind == "gg":
        group = parts[1]
        builds = [(b["label"], f"bvr|gb|{group}|{key}", P)
                  for key, b in r["gear"][group]["builds"].items()]
        return E.gear_group_embed(group), _nav(
            _grid(builds) + [[("⬅ Gear", "bvr|g"), HOME]])

    if kind == "gb":
        group, key = parts[1], parts[2]
        return E.gear_build_embed(group, key), _nav([
            [("⬅ Builds", f"bvr|gg|{group}"), ("⬅ Gear", "bvr|g"), HOME]])

    # unknown path — fall back to the BVR menu
    return _route(["home"])
