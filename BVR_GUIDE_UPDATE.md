# Update notes

## /guide — Blighted Veil Raid (new)
Pick a side → **🌀 Spirit (Outside)** or **🔥 Elemental (Inside)**.
- Elemental: pick Strategy 1 / 2 → pick your role → My Fights (Onis or Roots), My Deck, My Gear.
- Spirit: one shared guide — Opening, Oni Doors, Final Phase, Wisps & Gates.
- Content: `guides/raids/blighted/` (`plan/`, `gear/`, `data.py`)
- Screens: `commands/guide/bvr_embeds.py`, routing `commands/guide/bvr_nav.py`
- Maps: `assets/bvr/`

## /guide — Ghastly (right side by role)
Pick a side → Right Side → pick your role → My Fights / My Deck / My Gear.
Never asks "Support / Storm 1" or "Storm 2 / Storm 3". Support skips the 1v1s.
Left side unchanged. Turn cards show a progress bar.

## Signups
- Card shows "Need N more players" live, plus the 3-hour leave rule.
- When a spot opens, one public "needs N more" alert (no names). Staff tagged inside 3 hours.
- Private join/leave confirmation to the person who clicked.

## Mod log (new) — `/setlog #channel`
Joins, leaves (who + how close to start), 🔴 late leaves, mod changes, bans, cancels.
No log channel → late leaves are DM'd to the owner and /assign'd staff.

## Bans
Banned users clicking Join see a generic error, not a ban notice. Bot owner can't be banned.

## Owner
`config.py` `OWNER_IDS` — staff in every server. Add more with `OWNER_IDS=` in `.env`.
