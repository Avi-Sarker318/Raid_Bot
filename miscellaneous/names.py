"""Show Discord names instead of <@id> in embeds.

Why this exists: Discord only turns `<@123…>` into "@Name" if the viewer's
app already has that person loaded. Mentions inside an embed never load
anyone (unlike mentions in normal message text), so people the viewer hasn't
seen recently show up as a raw user ID — especially on mobile.

So we remember each person's server display name whenever the bot sees them
(joining, being added by a mod, /ban, …) and print that plain name in
embeds. Real pings still use <@id> in the message text, so notifications
keep working.

Names are saved per server in data/names.json.
"""
import json
import os

from data.paths import data_file

PATH = data_file("names.json")
_cache: dict[str, dict[str, str]] | None = None


def _load() -> dict:
    global _cache
    if _cache is None:
        try:
            with open(PATH) as f:
                _cache = json.load(f)
        except (OSError, ValueError):
            _cache = {}
    return _cache


def _save() -> None:
    try:
        with open(PATH, "w") as f:
            json.dump(_load(), f, indent=1)
    except OSError:
        pass


def _display(user) -> str:
    return (getattr(user, "display_name", None)
            or getattr(user, "global_name", None)
            or getattr(user, "name", None) or "Unknown")


def remember(guild_id, user) -> None:
    """Store/refresh a member's display name (call with a Member/User)."""
    if user is None:
        return
    store = _load().setdefault(str(guild_id), {})
    name = _display(user)
    if store.get(str(user.id)) != name:
        store[str(user.id)] = name
        _save()


def name(guild_id, uid) -> str:
    """Best-known display name for a user id ("" if unknown)."""
    uid = str(uid)
    known = _load().get(str(guild_id), {}).get(uid)
    if known:
        return known
    try:
        from core import client
        guild = client.get_guild(int(guild_id)) if guild_id else None
        member = guild.get_member(int(uid)) if guild else None
        user = member or client.get_user(int(uid))
        if user:
            remember(guild_id, user)
            return _display(user)
    except Exception:
        pass
    return ""


def bold(guild_id, uid) -> str:
    """**Name** — or a plain mention as a last resort if we truly can't
    find a name (Discord may still resolve it)."""
    n = name(guild_id, uid)
    return f"**{n}**" if n else f"<@{uid}>"


async def learn(guild_id, uids) -> None:
    """Look up anyone we don't have a name for yet (old signups from before
    this update). Uses the API, so it works without the Members intent."""
    store = _load().setdefault(str(guild_id), {})
    missing = [u for u in {int(u) for u in uids} if str(u) not in store]
    if not missing or not guild_id:
        return
    try:
        from core import client
        guild = client.get_guild(int(guild_id))
    except Exception:
        return
    for uid in missing:
        try:
            member = (guild.get_member(uid) or await guild.fetch_member(uid)
                      if guild else None)
            if member is None:
                member = client.get_user(uid) or await client.fetch_user(uid)
            remember(guild_id, member)
        except Exception:
            continue


async def learn_event(ev: dict) -> None:
    """Capped at 1.5s: button clicks must answer Discord within 3 seconds.
    Anyone not found in time shows as a mention and is looked up next time."""
    import asyncio
    try:
        await asyncio.wait_for(
            learn(ev.get("guild_id"),
                  [u for lst in ev.get("signups", {}).values() for u in lst]),
            timeout=1.5)
    except asyncio.TimeoutError:
        pass
