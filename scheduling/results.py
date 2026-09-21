"""✅ Finish + wins, 📜 History popup, share-and-delete."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import discord

import guides.loader
import guides.loader as raid_defs
import server_config as cfg
import user_prefs
from config import TEST_MODE, REMINDER_MINUTES
from core import client, events, save_events
from miscellaneous import history


class HistoryButton(discord.ui.Button):
    """Shows this month's raid participation: name — count."""

    def __init__(self, event_id: str):
        super().__init__(label="📜 History (mod)", style=discord.ButtonStyle.secondary,
                         custom_id=f"history:{event_id}", row=3)
        self.event_id = event_id

    async def callback(self, itx: discord.Interaction):
        if not cfg.is_staff(itx.guild_id, itx.user):
            await itx.response.send_message(
                "Only mods/admins can view raid history.", ephemeral=True)
            return
        await history.learn_names(itx.guild_id)
        summ = history.month_summary(itx.guild_id)
        if summ is None:
            await itx.response.send_message(
                "No raids recorded yet this month.", ephemeral=True)
            return
        month, text = summ
        e = discord.Embed(title=f"📜 Raids this month ({month})",
                          description=text, color=0x8A2BE2)
        view = HistoryDetailView(is_staff=cfg.is_staff(itx.guild_id, itx.user))
        await itx.response.send_message(embed=e, view=view, ephemeral=True)


class HistoryDetailView(discord.ui.View):
    def __init__(self, is_staff: bool):
        super().__init__(timeout=180)
        if is_staff:
            self.add_item(_ShareBtn())

    @discord.ui.button(label="📋 Show each raid + roles",
                       style=discord.ButtonStyle.secondary)
    async def details(self, itx: discord.Interaction, _):
        await history.learn_names(itx.guild_id)
        lines = history.raid_roster_lines(itx.guild_id)
        if not lines:
            await itx.response.send_message("No raids yet.", ephemeral=True)
            return
        e = discord.Embed(title="📋 This month — each raid & who filled it",
                          description="\n\n".join(lines)[:4000],
                          color=0x8A2BE2)
        await itx.response.send_message(embed=e, ephemeral=True)


class _ShareBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="📤 Share & delete",
                         style=discord.ButtonStyle.danger)

    async def callback(self, itx: discord.Interaction):
        await itx.response.send_message(
            "⚠️ Sharing posts this month's list **publicly** and then "
            "**deletes it from the bot** — it can't be recovered. The tracker "
            "restarts fresh (it always resets each month anyway). Share?",
            view=ShareConfirmView(), ephemeral=True)


class ShareView(discord.ui.View):
    """Staff-only: share the month publicly — which deletes it from the bot."""

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="📤 Share & delete",
                       style=discord.ButtonStyle.danger)
    async def share(self, itx: discord.Interaction, _):
        await itx.response.send_message(
            "⚠️ Sharing posts this month's list **publicly in this channel** "
            "and then **deletes it from the bot** — it can't be recovered. "
            "The tracker restarts fresh (it always resets at the start of each "
            "month anyway). Share?",
            view=ShareConfirmView(), ephemeral=True)


class ShareConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Yes — share & delete",
                       style=discord.ButtonStyle.danger)
    async def confirm(self, itx: discord.Interaction, _):
        await history.learn_names(itx.guild_id)
        summ = history.month_summary(itx.guild_id)
        if summ is None:
            await itx.response.send_message("Nothing to share.", ephemeral=True)
            return
        month, text = summ
        e = discord.Embed(title=f"📜 Raid tracking — {month}",
                          description=text, color=0x8A2BE2)
        await itx.channel.send(embed=e)
        history.clear_month(itx.guild_id)
        await itx.response.send_message(
            "✅ Shared — and deleted from the bot.", ephemeral=True)


class WinsModal(discord.ui.Modal, title="Raid finished — results"):
    wins_input = discord.ui.TextInput(
        label="How many wins did you receive?",
        placeholder="Leave blank for 0",
        required=False,
        max_length=4,
    )

    def __init__(self, event_id: str):
        super().__init__()
        self.event_id = event_id

    async def on_submit(self, itx: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await itx.response.send_message("Event gone.", ephemeral=True)
            return
        raw = self.wins_input.value.strip()
        try:
            wins = int(raw) if raw else 0
        except ValueError:
            wins = 0
        ev["wins"] = wins
        first_time = not ev.get("done")
        ev["done"] = True
        # roster: role -> the user who filled it (first occupant)
        roster = {role: lst[0] for role, lst in ev["signups"].items() if lst}
        history.record_raid(itx.guild_id, ev["channel_id"], ev["id"],
                            ev["raid"], roster, wins,
                            ev.get("event_type", "raid"))
        save_events(events)
        note = "" if first_time else " (updated)"
        await itx.response.send_message(
            f"✅ Recorded{note} — **{wins} wins**, "
            f"{len(roster)} players counted for this month. "
            "Mods can press **Finish** again to change the wins.",
            ephemeral=True)


class FinishButton(discord.ui.Button):
    """Creator or staff ends the raid: records participants + asks wins."""

    def __init__(self, event_id: str):
        super().__init__(label="✅ Finish", style=discord.ButtonStyle.success,
                         custom_id=f"finish:{event_id}", row=3)
        self.event_id = event_id

    async def callback(self, itx: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await itx.response.send_message("Event gone.", ephemeral=True)
            return
        if not cfg.is_staff(itx.guild_id, itx.user):
            await itx.response.send_message(
                "Only mods/admins can finish the raid.", ephemeral=True)
            return
        empty = [r for r in ev["roles"] if not ev["signups"].get(r)]
        if empty:
            filled = len(ev["roles"]) - len(empty)
            await itx.response.send_message(
                f"⚠️ **Not enough people** — {filled}/{len(ev['roles'])} "
                f"spots filled. Fill every role before finishing (or use "
                "Manage signups / Extend if you're short).", ephemeral=True)
            return
        await itx.response.send_modal(WinsModal(self.event_id))
