"""Background loop: raid reminders, event cleanup, and the
1st-of-month history auto-post + reset."""
import asyncio
from datetime import datetime, timezone

import discord

from config import REMINDER_MINUTES, TEST_MODE
from core import client, events, save_events
from miscellaneous import history
import server_config as cfg

# How long to wait after the start-time prompt before auto-cancelling a raid
# that still hasn't filled. Kept short in test mode for quick iteration.
AUTO_CANCEL_MINUTES = 10


def _is_full(ev: dict) -> bool:
    """Every role has at least its capacity signed up."""
    return all(len(ev["signups"].get(r, [])) >= cap
               for r, cap in ev["roles"].items())


def _can_manage(ev: dict, interaction) -> bool:
    """The raid's creator or a server mod/admin may extend/cancel."""
    if interaction.user.id == ev.get("creator"):
        return True
    return cfg.is_staff(interaction.guild_id, interaction.user)


def _notify_tag(ev: dict) -> str:
    """Who to ping about an under/unfilled raid: only the raid's creator.
    If the event somehow has no creator, fall back to configured staff so
    the prompt still reaches someone who can act on it."""
    creator = ev.get("creator")
    if creator:
        return f"<@{creator}>"
    gid = ev.get("guild_id")
    staff = cfg.staff_ids(gid) if gid else []
    return " ".join(f"<@{uid}>" for uid in staff) if staff else "@mods"


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
        if not _is_full(ev):
            await interaction.response.send_message(
                "The roster isn't full anymore — someone left. Fill the open "
                "spot(s) on the signup card, or extend/cancel the raid.",
                ephemeral=True)
            return
        from scheduling.card import roster_lines
        pings = " ".join(f"<@{uid}>"
                         for lst in ev["signups"].values() for uid in lst)
        e = discord.Embed(
            title=f"🚀 {ev['raid']} — RAID UP!",
            description=f"It's time to go for **{ev['guild']}**!\n\n"
                        + roster_lines(ev),
            color=0x3BA55D)
        await interaction.response.edit_message(
            content=pings, embed=e, view=None)


async def _prompt_underfilled(ev: dict, channel, empty: list) -> None:
    """5 min out and roles are still open — notify only the raid's creator
    (or fall back to staff if there's no creator) with Extend/Cancel."""
    tag = _notify_tag(ev)
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
    """Nobody signed up by start time — notify only the raid's creator
    (or fall back to staff if there's no creator) with Extend/Cancel."""
    tag = _notify_tag(ev)
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
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.edit_message(
                content="This raid is already gone.", embed=None, view=None)
            return False
        if not _can_manage(ev, interaction):
            await interaction.response.send_message(
                "Only the raid's creator or a mod/admin can extend or cancel.",
                ephemeral=True)
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
        ev["prompted_at"] = None          # re-arm the 10-min auto-cancel
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

            # At start time, branch on how full the roster is:
            #   • FULL  → show the Raid Up! page (go-time).
            #   • partly filled → ask creator/mods to Extend or Cancel.
            #   • empty → ask creator/mods to Extend or Cancel.
            # The Raid Up! page is ONLY shown when every role is filled, so it
            # never appears for a half-empty raid.
            if not ev.get("started") and starts_in <= 0:
                ev["started"] = True
                channel = client.get_channel(ev["channel_id"])
                if channel:
                    if _is_full(ev):
                        from scheduling.card import roster_lines
                        e = discord.Embed(
                            title=f"🚦 {ev['raid']} — start time",
                            description=(
                                f"**{ev['guild']}** — roster is full! A mod, "
                                "hit **Raid Up!** when everyone's ready.\n\n"
                                + roster_lines(ev)),
                            color=0x5865F2)
                        await channel.send(embed=e,
                                           view=RaidUpView(ev["id"]))
                    else:
                        # Not enough people. Don't show Raid Up — ask the
                        # creator/mods to extend or cancel, and start the
                        # 10-minute auto-cancel clock.
                        empty = [r for r in ev["roles"]
                                 if not ev["signups"].get(r)]
                        signed = [uid for lst in ev["signups"].values()
                                  for uid in lst]
                        if signed:
                            await _prompt_underfilled(ev, channel, empty)
                        else:
                            await _prompt_empty_raid(ev, channel)
                        ev["empty_prompted"] = True
                        ev["prompted_at"] = now
                save_events(events)

            # 10 minutes after the start-time prompt, if the raid still isn't
            # full and no one extended, assume it's dead: auto-cancel and
            # remove the event entirely.
            pa = ev.get("prompted_at")
            if (pa and not _is_full(ev)
                    and now - pa >= AUTO_CANCEL_MINUTES * 60):
                channel = client.get_channel(ev["channel_id"])
                if channel:
                    e = discord.Embed(
                        title=f"❌ {ev['raid']} — auto-cancelled",
                        description=(
                            f"**{ev['raid']}** ({ev['guild']}) never filled "
                            f"and no one extended it within "
                            f"{AUTO_CANCEL_MINUTES} minutes, so it's been "
                            "cancelled automatically."),
                        color=0x999999)
                    try:
                        await channel.send(embed=e)
                    except discord.Forbidden:
                        pass
                events.pop(ev["id"], None)
                save_events(events)
                continue

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
