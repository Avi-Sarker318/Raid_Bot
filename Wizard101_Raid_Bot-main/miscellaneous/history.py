"""Monthly who-raided tracking: record raids, simple name+count summary,
per-raid roster detail, share-and-delete, and month rollover helpers."""
import json
import os
from datetime import datetime, timezone


from data.paths import data_file
PATH = data_file("history.json")


def _load() -> dict:
    if os.path.exists(PATH):
        with open(PATH) as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    with open(PATH, "w") as f:
        json.dump(data, f, indent=2)


def current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _server(data: dict, server_id: int) -> dict:
    s = data.setdefault(str(server_id), {})
    s.setdefault("month", current_month())
    s.setdefault("counts", {})       # user_id -> raids done this month
    s.setdefault("raids", [])        # [{event_id, raid, ts, wins, participants}]
    return s


def record_raid(server_id: int, channel_id: int, event_id: str,
                raid_name: str, roster: dict[str, int], wins: int,
                event_type: str = "raid") -> None:
    """roster maps role -> user_id for who actually filled each spot."""
    data = _load()
    s = _server(data, server_id)
    s["last_channel"] = channel_id
    s["raids"] = [r for r in s["raids"] if r["event_id"] != event_id]
    s["raids"].append({
        "event_id": event_id,
        "raid": raid_name,
        "event_type": event_type,
        "ts": int(datetime.now(timezone.utc).timestamp()),
        "wins": wins,
        "roster": {role: uid for role, uid in roster.items()},
    })
    _recount(s)
    _save(data)


def _recount(s: dict) -> None:
    counts: dict[str, int] = {}
    for r in s["raids"]:
        for uid in r.get("roster", {}).values():
            counts[str(uid)] = counts.get(str(uid), 0) + 1
    s["counts"] = counts


def set_wins(server_id: int, event_id: str, wins: int) -> bool:
    data = _load()
    s = _server(data, server_id)
    for r in s["raids"]:
        if r["event_id"] == event_id:
            r["wins"] = wins
            _save(data)
            return True
    return False


def month_summary(server_id: int) -> tuple[str, str] | None:
    """Returns (month, text) or None.

    Per person: how many of each raid they did, plus their overall total.
    Sorted by total, highest first.
    """
    data = _load()
    s = _server(data, server_id)
    if not s["counts"]:
        return None

    # user_id -> {raid_name: times}
    per_user: dict[str, dict[str, int]] = {}
    for r in s["raids"]:
        raid = r.get("raid", "Unknown raid")
        for uid in set(r.get("roster", {}).values()):
            per_user.setdefault(str(uid), {}).setdefault(raid, 0)
            per_user[str(uid)][raid] += 1

    lines = []
    for uid, raids in sorted(per_user.items(),
                             key=lambda kv: -sum(kv[1].values())):
        total = sum(raids.values())
        lines.append(f"<@{uid}> — **{total}** total")
        for raid, n in sorted(raids.items(), key=lambda kv: -kv[1]):
            lines.append(f"  • {raid}: {n}")

    footer = f"\n\n**{len(s['raids'])} raids run this month**"
    text = "\n".join(lines)
    # Discord caps an embed description at 4096 chars — trim the tail
    # (lowest totals) if a very busy month would overflow.
    limit = 4096 - len(footer) - 40
    if len(text) > limit:
        kept, size = [], 0
        for ln in lines:
            if size + len(ln) + 1 > limit:
                break
            kept.append(ln)
            size += len(ln) + 1
        text = "\n".join(kept) + "\n… (list trimmed to fit)"
    return s["month"], text + footer


def raid_roster_lines(server_id: int) -> list[str]:
    """Detailed per-event view: each raid with roles filled."""
    data = _load()
    s = _server(data, server_id)
    out = []
    for r in s["raids"]:
        roster = r.get("roster", {})
        who = ", ".join(f"{role}: <@{uid}>" for role, uid in roster.items())
        out.append(f"**{r['raid']}** ({r.get('wins',0)} wins) — {who}")
    return out


def clear_month(server_id: int) -> None:
    """Delete this server's data — used after sharing."""
    data = _load()
    sid = str(server_id)
    if sid in data:
        chan = data[sid].get("last_channel")
        data[sid] = {"month": current_month(), "counts": {}, "raids": []}
        if chan:
            data[sid]["last_channel"] = chan
        _save(data)


def servers_needing_rollover() -> list[tuple[int, int, str, str]]:
    """Servers whose stored month is over: (server_id, channel_id, month, text).
    Called on/after the 1st — the bot posts each and then clears it."""
    data = _load()
    out = []
    now = current_month()
    for sid, s in data.items():
        if s.get("month") and s["month"] != now and s.get("counts"):
            summ = month_summary(int(sid))
            if summ and s.get("last_channel"):
                out.append((int(sid), s["last_channel"], summ[0], summ[1]))
    return out
