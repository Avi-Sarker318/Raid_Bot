"""The public signup card: embed + state-aware Join/Leave buttons."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import re

import discord

from miscellaneous import names as N

import guides.loader
import guides.loader as raid_defs
import server_config as cfg
import user_prefs
from config import TEST_MODE, REMINDER_MINUTES
from core import client, events, save_events


def _group_of(role: str) -> str | None:
    """The team/side a role belongs to, for grouping columns on the card.
    Detects a trailing "(Group)" tag or an Outside/Vanguard prefix."""
    m = re.search(r"\(([^)]+)\)\s*$", role)
    if m:
        return m.group(1)
    first = role.split()[0] if role.split() else ""
    if first in ("Outside", "Vanguard"):
        return first
    return None


def _side_of(role: str) -> str | None:
    # Used for signup-button ROWS (right=row0, left=row1, else row2).
    g = _group_of(role)
    if g in ("Right", "Spirit", "Outside"):
        return "right"
    if g in ("Left", "Elemental", "Vanguard"):
        return "left"
    return None


def _clean(role: str) -> str:
    return re.sub(r"\s*\([^)]+\)\s*$", "", role).strip()


_GROUP_ICON = {
    "Right": "➡️ Right Side", "Left": "⬅️ Left Side",
    "Spirit": "🌀 Spirit Team", "Elemental": "🔥 Elemental Team",
    "Outside": "🌐 Outside", "Vanguard": "🛡️ Vanguard",
}


LEAVE_HOURS = 3
LEAVE_RULE = (f"Can't make it? Leave (or tell a guild leader) at least "
              f"**{LEAVE_HOURS} hours** before start, so we can find a "
              "replacement instead of cancelling last minute.")


def open_spots(ev: dict) -> int:
    """How many players the raid still needs."""
    return sum(max(0, cap - len(ev["signups"].get(r, [])))
               for r, cap in ev["roles"].items())


def _need_line(ev: dict) -> str:
    n = open_spots(ev)
    if n == 0:
        return "✅ **Roster full — see you there!**"
    return f"🔴 **Need {n} more {'player' if n == 1 else 'players'}** to start"


def build_embed(ev: dict) -> discord.Embed:
    start = int(ev["start_ts"])
    embed = discord.Embed(
        title=f"⚔️ {ev['raid']}",
        description=(
            f"⚔️ **Raid**\n"
            f"**Guild:** {ev['guild']}\n"
            f"**Starts:** <t:{start}:F> (<t:{start}:R>)\n"
            f"**Duration:** {ev.get('duration_h', 1.5):g} hours\n"
            + "\n"
            f"{_need_line(ev)}\n\n"
            f"Tap a **Join** button below to claim a spot. Tap again to leave."
            + f"\n⏰ {LEAVE_RULE}"
            + "\n💡 Use **/guide** to see what you need for your role."
            + ("\n\n🧪 **TEST MODE** — one person can fill every role."
               if TEST_MODE else "")
        ),
        color=0x8A2BE2,
    )

    total = 0
    filled = 0
    # Bucket roles by group, preserving first-seen order.
    groups: dict = {}
    for role, cap in ev["roles"].items():
        groups.setdefault(_group_of(role), []).append((role, cap))

    def render_side(title: str, rows: list) -> None:
        nonlocal total, filled
        lines = []
        for role, cap in rows:
            members = ev["signups"].get(role, [])
            total += cap
            filled += len(members)
            who = ", ".join(N.bold(ev.get("guild_id"), uid)
                            for uid in members) or "*open*"
            check = "✅" if len(members) >= cap else "⬜"
            lines.append(f"{check} **{_clean(role)}** — {who}")
        embed.add_field(name=title, value="\n".join(lines), inline=True)

    for grp, rows in groups.items():
        render_side(_GROUP_ICON.get(grp, grp or "Positions"), rows)

    if ev.get("notes"):
        embed.add_field(name="📝 Notes", value=ev["notes"][:1024], inline=False)

    embed.set_footer(text=f"{filled}/{total} positions filled • Event ID {ev['id']}")
    return embed


class SignupButton(discord.ui.Button):
    """State-aware: an open role shows "Join X"; a filled role shows a grey
    "Leave X" that only the occupant can use (everyone else is told it's
    taken). The card's buttons rebuild on every change."""

    def __init__(self, ev: dict, role: str, row: int = 0):
        taken = bool(ev["signups"].get(role))
        super().__init__(
            label=(f"Leave {_clean(role)}" if taken else f"Join {_clean(role)}"),
            style=(discord.ButtonStyle.secondary if taken
                   else discord.ButtonStyle.primary),
            custom_id=f"signup:{ev['id']}:{role}",
            row=row,
        )
        self.event_id = ev["id"]
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.send_message(
                "This event no longer exists.", ephemeral=True
            )
            return

        uid = interaction.user.id
        N.remember(interaction.guild_id, interaction.user)
        if cfg.is_banned(interaction.guild_id, uid):
            await interaction.response.send_message(
                "⚠️ Something went wrong — you can't join this raid right "
                "now. Please try again later.", ephemeral=True)
            return
        signups = ev["signups"].setdefault(self.role, [])

        was_full = _is_full(ev)
        left_spot = False

        if uid in signups:
            signups.remove(uid)
            left_spot = True
        elif signups:
            # Filled by someone else — only that person can free it
            await interaction.response.send_message(
                f"**{self.role}** is taken by {N.bold(interaction.guild_id, signups[0])}. Only they (or "
                "a mod via Manage signups) can free it.", ephemeral=True
            )
            return
        else:
            # Normally one position per person. In test mode, let the same
            # person fill every role so you can test alone.
            if not TEST_MODE:
                for r, lst in ev["signups"].items():
                    if uid in lst:
                        lst.remove(uid)
            signups.append(uid)

        save_events(events)
        from scheduling.views.views import make_signup_view
        # The card itself updates to show the change — no extra ping needed.
        await N.learn_event(ev)       # names, not raw IDs
        await interaction.response.edit_message(
            embed=build_embed(ev), view=make_signup_view(ev))

        # Private note to the person who clicked (only they see it).
        hours_left = (int(ev["start_ts"])
                      - datetime.now(timezone.utc).timestamp()) / 3600
        try:
            if left_spot:
                note = (f"You left **{_clean(self.role)}**. The card now shows "
                        "how many players are needed.")
                if 0 < hours_left < LEAVE_HOURS:
                    note += (f"\n⚠️ The raid starts in under {LEAVE_HOURS} "
                             "hours — please also message a guild leader so "
                             "they can find someone.")
            else:
                note = (f"✅ You're in as **{_clean(self.role)}**!\n⏰ "
                        + LEAVE_RULE)
            await interaction.followup.send(note, ephemeral=True)
        except discord.HTTPException:
            pass

        # Roster just became full → tell everyone it's locked in.
        if not was_full and _is_full(ev):
            await _announce_full(interaction, ev)
        # Someone left → tell the channel how many are needed (never who).
        # Names only go to the private mod log.
        from miscellaneous import modlog
        if left_spot:
            await post_need_alert(ev, interaction.channel)
            await modlog.log_leave(ev, uid, _clean(self.role))
        else:
            await sync_need_alert(ev)
            await modlog.log_join(ev, uid, _clean(self.role))


def roster_lines(ev: dict) -> str:
    """The signed-up roster as 'Role — @user' lines, grouped by team.
    Used by every ping (full, reminder, raid-up) so people always see
    which position they're playing."""
    groups: dict = {}
    for role in ev["roles"]:
        for uid in ev["signups"].get(role, []):
            groups.setdefault(_group_of(role), []).append((role, uid))
    out = []
    for grp, pairs in groups.items():
        header = _GROUP_ICON.get(grp, grp or "Positions")
        out.append(f"**{header}**")
        out += [f"• {_clean(role)} — {N.bold(ev.get('guild_id'), uid)}"
                for role, uid in pairs]
    return "\n".join(out)


def roster_inline(ev: dict) -> str:
    """Compact one-line version: '@user (Role)' — for short pings."""
    return " ".join(
        f"{N.bold(ev.get('guild_id'), uid)} ({_clean(role)})"
        for role in ev["roles"]
        for uid in ev["signups"].get(role, []))


def ping_string(ev: dict) -> str:
    """Space-joined @mentions of everyone signed up, each listed once even
    if an admin placed them in several roles. Order = first role they hold.
    Discord already collapses duplicate mentions into one notification; this
    also keeps the visible text clean."""
    seen: list[int] = []
    for lst in ev["signups"].values():
        for uid in lst:
            if uid not in seen:
                seen.append(uid)
    return " ".join(f"<@{uid}>" for uid in seen)


def _is_full(ev: dict) -> bool:
    return all(len(ev["signups"].get(r, [])) >= cap
               for r, cap in ev["roles"].items())


async def _announce_full(interaction, ev: dict) -> None:
    """Every spot claimed — post the lineup so everyone sees their position."""
    await N.learn_event(ev)
    start = int(ev["start_ts"])
    e = discord.Embed(
        title=f"✅ {ev['raid']} — ROSTER FULL",
        description=(f"All **{len(ev['roles'])}** spots are claimed for "
                     f"**{ev['guild']}**!\n"
                     f"Starts <t:{start}:F> (<t:{start}:R>).\n\n"
                     + roster_lines(ev)),
        color=0x3BA55D)
    pings = ping_string(ev)
    try:
        await interaction.channel.send(content=pings, embed=e)
    except discord.Forbidden:
        pass


async def _delete_need_alert(ev: dict, channel=None) -> None:
    mid = ev.pop("need_msg_id", None)
    if not mid:
        return
    try:
        channel = channel or client.get_channel(ev["channel_id"])
        msg = await channel.fetch_message(mid)
        await msg.delete()
    except Exception:
        pass
    save_events(events)


def _need_embed(ev: dict) -> discord.Embed:
    n = open_spots(ev)
    start = int(ev["start_ts"])
    return discord.Embed(
        title=f"📣 {ev['raid']} needs {n} more "
              f"{'player' if n == 1 else 'players'}!",
        description=(f"**{ev['guild']}** • starts <t:{start}:F> "
                     f"(<t:{start}:R>)\n\n"
                     "Tap an open **Join** button on the signup card above "
                     "to grab a spot.\n\n⏰ " + LEAVE_RULE),
        color=0xE67E22)


async def post_need_alert(ev: dict, channel=None) -> None:
    """A spot opened up. Post (or re-post) one alert with the count only —
    it never says who left. The previous alert is replaced, so the channel
    only ever has one. Within LEAVE_HOURS of start, staff get tagged."""
    await _delete_need_alert(ev, channel)
    if open_spots(ev) == 0:
        return
    start = int(ev["start_ts"])
    hours_left = (start - datetime.now(timezone.utc).timestamp()) / 3600
    if hours_left < -0.1:
        return                                   # raid already started
    content = None
    if hours_left < LEAVE_HOURS:
        staff = cfg.staff_ids(ev.get("guild_id"))
        if staff:
            content = " ".join(f"<@{s}>" for s in staff)
    try:
        channel = channel or client.get_channel(ev["channel_id"])
        msg = await channel.send(content=content, embed=_need_embed(ev))
        ev["need_msg_id"] = msg.id
        save_events(events)
    except (discord.Forbidden, AttributeError):
        pass


async def sync_need_alert(ev: dict) -> None:
    """Someone joined: update the open alert's count, or remove it once the
    roster is full."""
    if not ev.get("need_msg_id"):
        return
    if open_spots(ev) == 0:
        await _delete_need_alert(ev)
        return
    try:
        channel = client.get_channel(ev["channel_id"])
        msg = await channel.fetch_message(ev["need_msg_id"])
        await msg.edit(embed=_need_embed(ev))
    except Exception:
        pass


async def _announce_dropout(interaction, ev: dict, role: str, uid: int) -> None:
    """Kept for older callers — now just posts the anonymous need alert."""
    await post_need_alert(ev, getattr(interaction, "channel", None))


class CancelButton(discord.ui.Button):
    def __init__(self, event_id: str):
        super().__init__(
            label="Cancel Event",
            style=discord.ButtonStyle.danger,
            custom_id=f"cancel:{event_id}",
            row=3,
        )
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.send_message("Already gone.", ephemeral=True)
            return
        if not cfg.is_staff(interaction.guild_id, interaction.user):
            await interaction.response.send_message(
                "Only mods/admins can cancel events.", ephemeral=True,
            )
            return
        del events[self.event_id]
        save_events(events)
        from miscellaneous import modlog
        await modlog.log_mod(ev, interaction.guild_id,
                             f"{N.bold(interaction.guild_id, interaction.user.id)} "
                             "**cancelled** the raid.")
        embed = discord.Embed(
            title=f"❌ {ev['raid']} — cancelled",
            description=f"Cancelled by {interaction.user.mention}.",
            color=0x999999,
        )
        await interaction.response.edit_message(embed=embed, view=None)