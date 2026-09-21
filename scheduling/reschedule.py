"""✏️ Edit/reschedule with the optional notify-players ping."""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import discord

import guides.loader
import guides.loader as raid_defs
import server_config as cfg
import user_prefs
from config import TEST_MODE, REMINDER_MINUTES
from core import client, events, save_events
from scheduling.time_input import TIMEZONES


class RescheduleNotesModal(discord.ui.Modal, title="Edit notes"):
    def __init__(self, parent, current: str):
        super().__init__()
        self.parent = parent
        self.notes_input = discord.ui.TextInput(
            label="Notes for the team", style=discord.TextStyle.paragraph,
            default=current, required=False, max_length=300)
        self.add_item(self.notes_input)

    async def on_submit(self, interaction: discord.Interaction):
        ev = events.get(self.parent.event_id)
        if ev is not None:
            ev["notes"] = self.notes_input.value.strip()
        await interaction.response.send_message(
            "📝 Notes updated. Pick the new date/time and continue.",
            ephemeral=True)


class RescheduleDateView(discord.ui.View):
    """Calendar-style date picker for editing an event (same style as
    scheduling): labeled dropdown of the next 3 weeks + Notes."""

    def __init__(self, event_id: str):
        super().__init__(timeout=300)
        self.event_id = event_id
        self.date_only = None
        today = datetime.now()
        options = []
        for i in range(21):
            d = today + timedelta(days=i)
            label = d.strftime("%a · %b %d")
            if i == 0:
                label += " (today)"
            elif i == 1:
                label += " (tomorrow)"
            options.append(discord.SelectOption(
                label=label, value=d.strftime("%Y-%m-%d")))
        self.date_sel = discord.ui.Select(
            placeholder="📅 Pick the new date", options=options[:25], row=0)
        self.date_sel.callback = self.on_date
        self.add_item(self.date_sel)

    async def on_date(self, interaction: discord.Interaction):
        y, mo, d = (int(x) for x in self.date_sel.values[0].split("-"))
        self.date_only = datetime(y, mo, d)
        await interaction.response.defer()

    @discord.ui.button(label="📝 Edit notes", style=discord.ButtonStyle.secondary, row=1)
    async def notes_btn(self, interaction: discord.Interaction, _):
        ev = events.get(self.event_id)
        cur = ev.get("notes", "") if ev else ""
        await interaction.response.send_modal(
            RescheduleNotesModal(self, cur))

    @discord.ui.button(label="Continue ➜", style=discord.ButtonStyle.success, row=1)
    async def cont(self, interaction: discord.Interaction, _):
        if self.date_only is None:
            await interaction.response.send_message(
                "Pick a date first.", ephemeral=True)
            return
        from scheduling.time_input import _time_prompt
        view = RescheduleTimePickView(self.event_id, self.date_only)
        await interaction.response.edit_message(
            content=f"📅 **{self.date_only.strftime('%A, %b %d, %Y')}**\n"
                    + _time_prompt(view),
            view=view)


class RescheduleTimePickView(discord.ui.View):
    """Same button time picker as scheduling, for editing an event."""

    def __init__(self, event_id: str, date_only: datetime):
        super().__init__(timeout=300)
        self.event_id = event_id
        self.date_only = date_only
        self.hour = self.minute = self.ampm = self.duration = None
        from scheduling.time_input import _build_time_buttons
        _build_time_buttons(self)

    @staticmethod
    def _coerce(attr, raw):
        if attr in ("hour", "minute"):
            return int(raw)
        if attr == "duration":
            return float(raw)
        return raw

    async def _continue(self, interaction: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.send_message("Event gone.", ephemeral=True)
            return
        if None in (self.hour, self.minute, self.ampm, self.duration):
            await interaction.response.send_message(
                "Tap an hour, minutes, AM/PM, and a duration first.",
                ephemeral=True)
            return
        ev["duration_h"] = self.duration
        hour24 = (self.hour % 12) + (12 if self.ampm == "PM" else 0)
        naive = self.date_only.replace(hour=hour24, minute=self.minute)
        saved = user_prefs.get_tz(interaction.user.id)
        if saved and saved in TIMEZONES:
            await _apply_new_time(interaction, self.event_id, naive, saved)
            return
        await interaction.response.edit_message(
            content=f"Editing **{naive.strftime('%A, %b %d')} at "
                    f"{naive.strftime('%I:%M %p').lstrip('0')}** — pick your "
                    "timezone (asked once — remembered after):",
            view=RescheduleTZView(self.event_id, naive))


class RescheduleTZView(discord.ui.View):
    def __init__(self, event_id: str, naive: datetime):
        super().__init__(timeout=300)
        self.event_id = event_id
        self.naive = naive
        select = discord.ui.Select(
            placeholder="Your timezone",
            options=[discord.SelectOption(label=k) for k in TIMEZONES])
        select.callback = self.on_pick
        self.select = select
        self.add_item(select)

    async def on_pick(self, interaction: discord.Interaction):
        label = self.select.values[0]
        user_prefs.set_tz(interaction.user.id, label)
        await _apply_new_time(interaction, self.event_id, self.naive, label)


async def _apply_new_time(interaction, event_id: str, naive, tz_label: str):
    ev = events.get(event_id)
    if ev is None:
        await interaction.response.send_message("Event gone.", ephemeral=True)
        return
    ts = int(naive.replace(tzinfo=ZoneInfo(TIMEZONES[tz_label])).timestamp())
    if ts <= int(datetime.now(timezone.utc).timestamp()):
        await interaction.response.send_message(
            "That time is in the past — pick a future time.", ephemeral=True)
        return
    changed = ts != ev["start_ts"]
    ev["start_ts"] = ts
    ev["reminded"] = False        # re-arm the reminder
    save_events(events)
    from scheduling.views.views import refresh_card
    await refresh_card(ev)
    if changed:
        await interaction.response.edit_message(
            content="✅ Time updated. Notify everyone signed up that it moved?",
            view=NotifyChoiceView(event_id))
    else:
        await interaction.response.edit_message(
            content="✅ Updated. The time didn't change, so no one was pinged.",
            view=None)


class NotifyChoiceView(discord.ui.View):
    """Only shown when the time actually changed."""

    def __init__(self, event_id: str):
        super().__init__(timeout=180)
        self.event_id = event_id

    @discord.ui.button(label="📣 Notify players", style=discord.ButtonStyle.primary)
    async def notify(self, itx: discord.Interaction, _):
        ev = events.get(self.event_id)
        if ev is None:
            await itx.response.send_message("Event gone.", ephemeral=True)
            return
        from scheduling.card import roster_lines, ping_string
        mentions = ping_string(ev)
        start = int(ev["start_ts"])
        e = discord.Embed(
            title=f"🔄 {ev['raid']} — rescheduled",
            description=(f"New start: <t:{start}:F> (<t:{start}:R>)\n\n"
                         + (roster_lines(ev) or "*(no signups yet)*")),
            color=0x5865F2)
        try:
            chan = client.get_channel(ev["channel_id"])
            await chan.send(content=mentions, embed=e)
        except Exception:
            pass
        await itx.response.edit_message(
            content="📣 Players notified of the new time.", view=None)

    @discord.ui.button(label="🤫 Don't notify", style=discord.ButtonStyle.secondary)
    async def silent(self, itx: discord.Interaction, _):
        await itx.response.edit_message(
            content="✅ Updated quietly — no ping sent.", view=None)


class RescheduleButton(discord.ui.Button):
    """Creator or staff edits the time/duration/notes."""

    def __init__(self, event_id: str):
        super().__init__(label="✏️ Edit / Reschedule",
                         style=discord.ButtonStyle.secondary,
                         custom_id=f"resched:{event_id}", row=4)
        self.event_id = event_id

    async def callback(self, itx: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await itx.response.send_message("Event gone.", ephemeral=True)
            return
        if not cfg.is_staff(itx.guild_id, itx.user):
            await itx.response.send_message(
                "Only mods/admins can edit this.", ephemeral=True)
            return
        await itx.response.send_message(
            "**Edit / reschedule** — pick the new date, edit notes if you "
            "want, then Continue:",
            view=RescheduleDateView(self.event_id), ephemeral=True)