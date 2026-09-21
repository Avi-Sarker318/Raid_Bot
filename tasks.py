"""Background loop: raid reminders, event cleanup, and the
1st-of-month history auto-post + reset."""
import asyncio
from datetime import datetime, timezone

import discord

from config import REMINDER_MINUTES, TEST_MODE
from core import client, events, save_events
from miscellaneous import history
import server_config as cfg


class RaidUpView(discord.ui.View):
    """Posted at start time. A mod hits 'Raid Up!' to signal go-time and
    ping everyone signed up."""

    def __init__(self, event_id: str):
        super().__init__(timeout=None)
        self.event_id = event_id

    @discord.ui.button(label="🚀 Raid Up!", style=discord.ButtonStyle.success)
    async def raid_up(self, interaction: discord.Interaction, _):
        if not cfg.is_staff(interaction.guild_id, interaction.user):
            await interaction.response.send_message(
                "Only mods/admins can start the raid.", ephemeral=True)
            return
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.edit_message(
                content="This raid is no longer available.", view=None)
            return
        from scheduling.card import roster_lines, ping_string
        from miscellaneous.names import learn_event
        await learn_event(ev)
        pings = ping_string(ev)
        e = discord.Embed(
            title=f"🚀 {ev['raid']} — RAID UP!",
            description=f"It's time to go for **{ev['guild']}**!\n\n"
                        + roster_lines(ev),
            color=0x3BA55D)
        await interaction.response.edit_message(
            content=pings, embed=e, view=None)


async def _prompt_underfilled(ev: dict, channel, empty: list) -> None:
    """5 min out and roles are still open — tag mods with Extend/Cancel."""
    gid = ev.get("guild_id") or getattr(channel.guild, "id", None)
    staff = cfg.staff_ids(gid) if gid else []
    tag = " ".join(f"<@{uid}>" for uid in staff) if staff else "@mods"
    total = len(ev["roles"])
    filled = total - len(empty)
    missing = ", ".join(_clean_role(r) for r in empty)
    e = discord.Embed(
        title=f"⏳ {ev['raid']} — {filled}/{total} filled, starting soon",
        description=(
            f"**{ev['raid']}** ({ev['guild']}) starts <t:{ev['start_ts']}:R> "
            f"but **{len(empty)}** spot(s) are still open:\n{missing}\n\n"
            "A mod can **extend** the start time to fill them, or **cancel**."),
        color=0xF1C40F)
    await channel.send(content=f"{tag} — heads up:", embed=e,
                       view=StartPromptView(ev["id"]))


def _clean_role(role: str) -> str:
    import re
    return re.sub(r"\s*\([^)]+\)\s*$", "", role).strip()


async def _prompt_empty_raid(ev: dict, channel) -> None:
    """Nobody signed up by start time — tag mods and offer Extend/Cancel."""
    gid = ev.get("guild_id") or getattr(channel.guild, "id", None)
    staff = cfg.staff_ids(gid) if gid else []
    tag = " ".join(f"<@{uid}>" for uid in staff) if staff else "@mods"
    e = discord.Embed(
        title=f"⚠️ {ev['raid']} — no one signed up",
        description=(
            f"**{ev['raid']}** ({ev['guild']}) was set to start "
            f"<t:{ev['start_ts']}:R> but **nobody joined**.\n\n"
            "A mod can **extend** the start time to gather more players, or "
            "**cancel** it. The raid stays open until then."),
        color=0xE67E22)
    await channel.send(content=f"{tag} — action needed:", embed=e,
                       view=StartPromptView(ev["id"]))


class StartPromptView(discord.ui.View):
    """Staff-only Extend / Cancel choice for an empty raid at start time."""

    def __init__(self, event_id: str):
        super().__init__(timeout=None)
        self.event_id = event_id

    async def _staff_only(self, interaction) -> bool:
        if not cfg.is_staff(interaction.guild_id, interaction.user):
            await interaction.response.send_message(
                "Only mods/admins can extend or cancel.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⏩ Extend 30 min", style=discord.ButtonStyle.primary)
    async def ext30(self, interaction: discord.Interaction, _):
        await self._extend(interaction, 30)

    @discord.ui.button(label="⏩ Extend 1 hour", style=discord.ButtonStyle.primary)
    async def ext60(self, interaction: discord.Interaction, _):
        await self._extend(interaction, 60)

    @discord.ui.button(label="❌ Cancel raid", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        if not await self._staff_only(interaction):
            return
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.edit_message(
                content="This raid is already gone.", embed=None, view=None)
            return
        del events[self.event_id]
        save_events(events)
        await interaction.response.edit_message(
            content=f"❌ **{ev['raid']}** cancelled by "
                    f"{interaction.user.mention}.", embed=None, view=None)

    async def _extend(self, interaction, minutes: int):
        if not await self._staff_only(interaction):
            return
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.edit_message(
                content="This raid is already gone.", embed=None, view=None)
            return
        # push start time out and re-arm the reminder + start checks
        ev["start_ts"] += minutes * 60
        ev["reminded"] = False
        ev["started"] = False
        ev["empty_prompted"] = False
        ev["fill_checked"] = False
        save_events(events)
        # refresh the public signup card to show the new time
        try:
            from scheduling.views.views import refresh_card
            await refresh_card(ev)
        except Exception:
            pass
        await interaction.response.edit_message(
            content=f"⏩ **{ev['raid']}** extended by {minutes} min by "
                    f"{interaction.user.mention} — now starts "
                    f"<t:{ev['start_ts']}:R>. Signups are open!",
            embed=None, view=None)

async def reminder_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.now(timezone.utc).timestamp()
        # Monthly rollover: on the 1st, auto-post last month's tracking
        # to each server's last raid channel, then delete it from the bot.
        # Load names first so the report shows names, not raw user IDs.
        for sid in history.stale_server_ids():
            await history.learn_names(sid)
        for sid, chan_id, month, text in history.servers_needing_rollover():
            channel = client.get_channel(chan_id)
            if channel:
                e = discord.Embed(
                    title=f"📜 Raid tracking — {month}",
                    description=text + "\n\n*Auto-posted for the new month — "
                                       "this data has now been deleted from "
                                       "the bot and the tracker restarted.*",
                    color=0x8A2BE2)
                try:
                    await channel.send(embed=e)
                except Exception:
                    pass
            history.clear_month(sid)
        for ev in list(events.values()):
          # One bad event (e.g. the bot lost access to its channel) must not
          # kill the loop for everyone else.
          try:
            starts_in = ev["start_ts"] - now
            rem_window = (REMINDER_MINUTES * 60) if not TEST_MODE else max(
                REMINDER_MINUTES * 60, 90 * 60)  # test: ping up to 90m out
            if not ev["reminded"] and 0 < starts_in <= rem_window:
                channel = client.get_channel(ev["channel_id"])
                if channel:
                    from scheduling.card import roster_lines
                    from miscellaneous.names import learn_event
                    await learn_event(ev)
                    pings = " ".join(
                        f"<@{uid}>"
                        for lst in ev["signups"].values()
                        for uid in lst) or ""
                    e = discord.Embed(
                        title=f"⏰ {ev['raid']} starts soon!",
                        description=(
                            f"**{ev['guild']}** — starts "
                            f"<t:{int(ev['start_ts'])}:R>.\n\n"
                            + (roster_lines(ev) or "*(no signups yet)*")),
                        color=0xF1C40F)
                    await channel.send(content=pings, embed=e)
                ev["reminded"] = True
                save_events(events)

            # 5 min before start: if any role is still empty, alert mods so
            # they can extend (gather more) or cancel. Fires once.
            fill_window = (5 * 60) if not TEST_MODE else max(5 * 60, 60 * 60)
            if (not ev.get("fill_checked") and 0 < starts_in <= fill_window):
                ev["fill_checked"] = True
                empty = [r for r in ev["roles"]
                         if not ev["signups"].get(r)]
                if empty:
                    channel = client.get_channel(ev["channel_id"])
                    if channel:
                        await _prompt_underfilled(ev, channel, empty)
                save_events(events)

            # At start time: ping the roster, or prompt mods if nobody joined.
            if not ev.get("started") and starts_in <= 0:
                ev["started"] = True
                channel = client.get_channel(ev["channel_id"])
                signed = [uid for lst in ev["signups"].values() for uid in lst]
                if channel:
                    if signed:
                        from scheduling.card import roster_lines
                        from miscellaneous.names import learn_event
                        await learn_event(ev)
                        e = discord.Embed(
                            title=f"🚦 {ev['raid']} — start time",
                            description=(
                                f"**{ev['guild']}** — a mod, hit **Raid Up!** "
                                "when everyone's ready.\n\n"
                                + roster_lines(ev)),
                            color=0x5865F2)
                        await channel.send(embed=e,
                                           view=RaidUpView(ev["id"]))
                    else:
                        # No one joined — tag mods and wait for Extend/Cancel.
                        await _prompt_empty_raid(ev, channel)
                        ev["empty_prompted"] = True
                save_events(events)

            # Clean up events more than a day old
            if starts_in < -86400:
                del events[ev["id"]]
                save_events(events)
          except discord.Forbidden:
            # Lost permission to post in that channel — skip this event.
            continue
          except Exception:
            continue
        await asyncio.sleep(5 if TEST_MODE else 30)