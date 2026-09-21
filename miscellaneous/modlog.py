"""Private mod log — who joined, who left (and how close to start), mod
changes, bans, cancels.

Entries go to the server's log channel (set with /setlog). Late leaves —
someone dropping within LEAVE_HOURS of start — are urgent: if no log channel
is set, they're DM'd to the bot owner and every /assign'd staff member
instead, so nobody is ever left guessing who bailed.

The public "needs N more" alert stays anonymous; only this log has names.
"""
from datetime import datetime, timezone

import discord

import server_config as cfg
from miscellaneous import names as N

LEAVE_HOURS = 3


def _until(ev: dict) -> str:
    secs = int(ev["start_ts"]) - datetime.now(timezone.utc).timestamp()
    if secs <= 0:
        return "after start"
    h, m = int(secs // 3600), int(secs % 3600 // 60)
    return (f"{h}h {m}m" if h else f"{m}m") + " before start"


def hours_left(ev: dict) -> float:
    return (int(ev["start_ts"]) - datetime.now(timezone.utc).timestamp()) / 3600


def _card_link(ev: dict) -> str:
    if ev.get("guild_id") and ev.get("channel_id") and ev.get("message_id"):
        return (f"https://discord.com/channels/{ev['guild_id']}/"
                f"{ev['channel_id']}/{ev['message_id']}")
    return ""


def _embed(ev: dict | None, title: str, text: str, color: int) -> discord.Embed:
    e = discord.Embed(title=title, description=text, color=color,
                      timestamp=datetime.now(timezone.utc))
    if ev:
        start = int(ev["start_ts"])
        link = _card_link(ev)
        e.add_field(name="Raid",
                    value=f"**{ev['raid']}** • {ev['guild']}\n"
                          f"Starts <t:{start}:F> (<t:{start}:R>)"
                          + (f"\n[Jump to signup card]({link})" if link else ""),
                    inline=False)
        e.set_footer(text=f"Event ID {ev['id']}")
    return e


async def _send(guild_id: int, embed: discord.Embed, urgent: bool) -> None:
    from core import client
    chan_id = cfg.log_channel_id(guild_id)
    chan = client.get_channel(chan_id) if chan_id else None
    if chan is not None:
        try:
            await chan.send(embed=embed)
            return
        except discord.HTTPException:
            pass                         # fall through to DMs if urgent
    if not urgent:
        return
    from config import OWNER_IDS
    for uid in set(OWNER_IDS) | set(cfg.staff_ids(guild_id)):
        try:
            user = client.get_user(uid) or await client.fetch_user(uid)
            await user.send(embed=embed)
        except discord.HTTPException:
            pass                         # DMs closed — nothing else to do


async def log_join(ev: dict, uid: int, role: str) -> None:
    await _send(ev.get("guild_id"), _embed(
        ev, "🟢 Joined",
        f"{N.bold(ev.get('guild_id'), uid)} joined **{role}** ({_until(ev)}).",
        0x3BA55D), urgent=False)


async def log_leave(ev: dict, uid: int, role: str, by: int | None = None,
                    reason: str = "left") -> None:
    """Someone left a spot (themselves, a mod removal, or a ban)."""
    late = 0 < hours_left(ev) < LEAVE_HOURS
    g = ev.get("guild_id")
    who = N.bold(g, uid)
    if by and by != uid:
        what = f"{who} was **{reason}** from **{role}** by {N.bold(g, by)}"
    else:
        what = f"{who} left **{role}**"
    title = "🔴 LATE LEAVE" if late else "🟠 Left"
    text = f"{what} — **{_until(ev)}**."
    if late:
        text += (f"\n⚠️ Inside the {LEAVE_HOURS}-hour window — a replacement "
                 "is needed.")
    await _send(ev.get("guild_id"), _embed(
        ev, title, text, 0xED4245 if late else 0xE67E22), urgent=late)


async def log_mod(ev: dict | None, guild_id: int, text: str) -> None:
    """Mod actions: add / replace / switch / cancel."""
    await _send(guild_id, _embed(ev, "🛠️ Mod action", text, 0x5865F2),
                urgent=False)


async def log_ban(guild_id: int, target: int, by: int, banned: bool,
                  removed: int = 0) -> None:
    if banned:
        text = (f"{N.bold(guild_id, target)} was **banned** from raids by "
                f"{N.bold(guild_id, by)}"
                + (f" and removed from {removed} spot(s)." if removed else "."))
    else:
        text = (f"{N.bold(guild_id, target)} was **unbanned** by "
                f"{N.bold(guild_id, by)}.")
    await _send(guild_id, _embed(None, "🚫 Ban" if banned else "✅ Unban",
                                 text, 0x99AAB5), urgent=False)
