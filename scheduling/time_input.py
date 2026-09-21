"""The /schedule flow: guild + raid pickers, timezones, the date/time
modal, and event creation. Timezone is asked ONCE per scheduler, then
saved."""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import discord

import guides.loader
import guides.loader as raid_defs
import server_config as cfg
import user_prefs
from config import TEST_MODE, REMINDER_MINUTES
from core import client, events, save_events


TIMEZONES = {
    "Eastern (ET)": "America/New_York",
    "Central (CT)": "America/Chicago",
    "Mountain (MT)": "America/Denver",
    "Pacific (PT)": "America/Los_Angeles",
    "UK (GMT/BST)": "Europe/London",
    "UTC": "UTC",
}


def parse_ampm_time(text: str) -> tuple[int, int]:
    """Parse '8:00 PM', '8 pm', '8:15pm', '20:00' → (hour24, minute). Raises ValueError."""
    t = text.strip().lower().replace(".", "")
    ampm = None
    if t.endswith("am"):
        ampm, t = "am", t[:-2].strip()
    elif t.endswith("pm"):
        ampm, t = "pm", t[:-2].strip()
    if ":" in t:
        hh, mm = t.split(":", 1)
    else:
        hh, mm = t, "0"
    hour, minute = int(hh), int(mm)
    if not (0 <= minute < 60):
        raise ValueError("minute out of range")
    if ampm:  # 12-hour
        if not (1 <= hour <= 12):
            raise ValueError("hour out of range")
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
    else:  # 24-hour fallback
        if not (0 <= hour <= 23):
            raise ValueError("hour out of range")
    return hour, minute




class NotesModal(discord.ui.Modal, title="Add notes (optional)"):
    notes_input = discord.ui.TextInput(
        label="Notes for the team",
        style=discord.TextStyle.paragraph,
        placeholder="Anything the team should know…",
        required=False, max_length=300)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    async def on_submit(self, interaction: discord.Interaction):
        self.parent.notes = self.notes_input.value.strip()
        await interaction.response.send_message(
            "📝 Notes saved. Pick your date and continue.", ephemeral=True)


class DatePickView(discord.ui.View):
    """Calendar-style date picker: a labeled dropdown of the next 3 weeks
    (each option shows the weekday + date), plus an optional Notes button.
    No typing — pick a day and continue."""

    def __init__(self, guild_name: str, target_name: str):
        super().__init__(timeout=300)
        self.guild_name = guild_name
        self.target_name = target_name
        self.date_only = None
        self.notes = ""

        today = datetime.now()
        options = []
        for i in range(21):                       # next 3 weeks
            d = today + timedelta(days=i)
            label = d.strftime("%a · %b %d")       # e.g. "Mon · Jul 21"
            if i == 0:
                label += " (today)"
            elif i == 1:
                label += " (tomorrow)"
            options.append(discord.SelectOption(
                label=label, value=d.strftime("%Y-%m-%d")))
        self.date_sel = discord.ui.Select(
            placeholder="📅 Pick a date", options=options[:25], row=0)
        self.date_sel.callback = self.on_date
        self.add_item(self.date_sel)

    async def on_date(self, interaction: discord.Interaction):
        y, mo, d = (int(x) for x in self.date_sel.values[0].split("-"))
        self.date_only = datetime(y, mo, d)
        await interaction.response.defer()

    @discord.ui.button(label="📝 Notes", style=discord.ButtonStyle.secondary, row=1)
    async def notes_btn(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(NotesModal(self))

    @discord.ui.button(label="Continue ➜", style=discord.ButtonStyle.success, row=1)
    async def cont(self, interaction: discord.Interaction, _):
        if self.date_only is None:
            await interaction.response.send_message(
                "Pick a date first.", ephemeral=True)
            return
        view = TimePickView(self.guild_name, self.target_name,
                            self.date_only, self.notes)
        await interaction.response.edit_message(
            content=f"📅 **{self.date_only.strftime('%A, %b %d, %Y')}**\n"
                    + _time_prompt(view),
            view=view,
        )

    @discord.ui.button(label="✖ Cancel", style=discord.ButtonStyle.secondary, row=1)
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(
            content="Scheduling cancelled.", view=None)


class TimePickView(discord.ui.View):
    """Labeled time picker: Hour, Minutes, AM/PM, and Duration dropdowns,
    then Continue. A live summary shows the current pick."""

    def __init__(self, guild_name: str, target_name: str,
                 date_only: datetime, notes: str):
        super().__init__(timeout=300)
        self.guild_name = guild_name
        self.target_name = target_name
        self.date_only = date_only
        self.notes = notes
        self.hour = None
        self.minute = None
        self.ampm = None
        self.duration = None
        _build_time_buttons(self)

    @staticmethod
    def _coerce(attr, raw):
        if attr == "hour":
            return int(raw)
        if attr == "minute":
            return int(raw)
        if attr == "duration":
            return float(raw)
        return raw            # ampm stays "AM"/"PM"

    async def _continue(self, interaction: discord.Interaction):
        if None in (self.hour, self.minute, self.ampm, self.duration):
            await interaction.response.send_message(
                "Tap an hour, minutes, AM/PM, and a duration first.",
                ephemeral=True)
            return
        hour24 = (self.hour % 12) + (12 if self.ampm == "PM" else 0)
        naive = self.date_only.replace(hour=hour24, minute=self.minute)
        extras = {"duration_h": self.duration, "notes": self.notes}
        saved = user_prefs.get_tz(interaction.user.id)
        if saved and saved in TIMEZONES:
            ok = await create_event(interaction, self.guild_name,
                                    self.target_name, naive, extras, saved)
            if ok:
                await interaction.response.edit_message(
                    content=f"✅ **Scheduled!** Used your saved timezone "
                            f"(**{saved}**) — everyone sees their own local "
                            "time. The signup card is posted below.",
                    view=None)
            return
        await interaction.response.edit_message(
            content=f"📅 **{naive.strftime('%A, %b %d')} at "
                    f"{naive.strftime('%I:%M %p').lstrip('0')}** — pick your "
                    "timezone (asked **once** — remembered after this):",
            view=TimezoneView(self.guild_name, self.target_name, naive, extras),
        )


def _build_time_buttons(view: discord.ui.View):
    """Adds labeled time controls to a view: Hour, Minutes, AM/PM, and
    Duration dropdowns (each clearly titled), plus a Continue button. The
    view must have .hour/.minute/.ampm/.duration attrs and a coroutine
    ._continue(interaction). Shared by scheduling + reschedule.

    Dropdowns show their label right on the control ("⏰ Hour", "Minutes",
    "AM / PM", "Duration"), and _time_summary() prints the running choice
    in the message text so it's always obvious what's selected.
    """
    def make_select(attr, placeholder, options, row):
        sel = discord.ui.Select(placeholder=placeholder, options=options,
                                row=row)

        async def cb(interaction: discord.Interaction):
            raw = sel.values[0]
            setattr(view, attr, view._coerce(attr, raw))
            # keep each dropdown showing the chosen value as its placeholder
            for o in sel.options:
                o.default = (o.value == raw)
            await interaction.response.edit_message(
                content=_time_prompt(view), view=view)
        sel.callback = cb
        view.add_item(sel)
        return sel

    make_select("hour", "⏰ Hour",
                [discord.SelectOption(label=f"{h} o'clock", value=str(h))
                 for h in range(1, 13)], 0)
    make_select("minute", "🕐 Minutes",
                [discord.SelectOption(label=f":{m:02d}", value=str(m))
                 for m in (0, 15, 30, 45)], 1)
    make_select("ampm", "🌗 AM or PM",
                [discord.SelectOption(label="AM (morning)", value="AM"),
                 discord.SelectOption(label="PM (afternoon/evening)", value="PM")], 2)
    make_select("duration", "⏳ Duration",
                [discord.SelectOption(label="1.5 hours", value="1.5"),
                 discord.SelectOption(label="3 hours", value="3")], 3)

    cont = discord.ui.Button(label="Continue ➜",
                             style=discord.ButtonStyle.success, row=4)
    cont.callback = view._continue
    view.add_item(cont)


def _time_prompt(view) -> str:
    """The message text above the dropdowns, with a live pick summary."""
    return ("🕒 **Pick the start time**\n"
            "Choose the **Hour**, **Minutes**, **AM/PM**, and **Duration** "
            "below, then hit Continue.\n\n"
            f"**Selected:** {_time_summary(view)}")


def _time_summary(view) -> str:
    h = view.hour if view.hour is not None else "—"
    m = f"{view.minute:02d}" if view.minute is not None else "—"
    ap = view.ampm or "—"
    dur = (f"{view.duration:g}h" if view.duration is not None else "—")
    return f"{h}:{m} {ap}  •  {dur}"


def _refresh_time_styles(view: discord.ui.View):
    """No-op kept for compatibility (dropdowns show their own selection)."""
    return


async def create_event(interaction, guild_name, target_name,
                       naive, extras, tz_label) -> bool:
    """Build + post the signup card. Returns False if the time was invalid
    (an ephemeral error is sent in that case)."""
    tzname = TIMEZONES[tz_label]
    ts = int(naive.replace(tzinfo=ZoneInfo(tzname)).timestamp())
    if ts <= int(datetime.now(timezone.utc).timestamp()):
        await interaction.response.send_message(
            "That time is in the past — start over with a future time.",
            ephemeral=True)
        return False
    from scheduling.views.formats.loader import roles_for
    roles = roles_for(target_name)
    event_id = str(int(datetime.now(timezone.utc).timestamp() * 1000))
    ev = {
        "id": event_id,
        "guild": guild_name,
        "raid": target_name,
        "start_ts": ts,
        "roles": roles,
        "signups": {},
        "creator": interaction.user.id,
        "channel_id": interaction.channel_id,
        "message_id": None,
        "reminded": False,
        "fill_checked": False,
        "started": False,
        "empty_prompted": False,
        "prompted_at": None,
        "guild_id": interaction.guild_id,
        "duration_h": extras.get("duration_h", 1.5),
        "notes": extras.get("notes", ""),
        "done": False,
        "wins": None,
    }
    events[event_id] = ev
    from scheduling.views.views import make_signup_view
    from scheduling.card import build_embed
    try:
        msg = await interaction.channel.send(
            embed=build_embed(ev), view=make_signup_view(ev))
    except discord.Forbidden:
        # The bot can't post in this channel — tell the scheduler plainly
        # instead of dying with a traceback, and don't keep a half-made event.
        events.pop(event_id, None)
        save_events(events)
        warning = (
            "❌ I can't post the signup card in this channel — I'm missing "
            "permissions.\n\nAsk an admin to give me **View Channel**, "
            "**Send Messages**, and **Embed Links** here (Edit Channel → "
            "Permissions), then try **/schedule** again.")
        if interaction.response.is_done():
            await interaction.followup.send(warning, ephemeral=True)
        else:
            await interaction.response.edit_message(content=warning, view=None)
        return False
    ev["message_id"] = msg.id
    save_events(events)
    return True


class ChangeTZView(discord.ui.View):
    """Small affordance to change the remembered timezone for next time."""

    def __init__(self):
        super().__init__(timeout=180)
        sel = discord.ui.Select(placeholder="🌍 Change my saved timezone",
                                options=[discord.SelectOption(label=k)
                                         for k in TIMEZONES])
        sel.callback = self.on_pick
        self.sel = sel
        self.add_item(sel)

    async def on_pick(self, itx: discord.Interaction):
        user_prefs.set_tz(itx.user.id, self.sel.values[0])
        await itx.response.send_message(
            f"🌍 Saved — future schedules will use **{self.sel.values[0]}**.",
            ephemeral=True)


class TimezoneView(discord.ui.View):
    """Scheduler picks which timezone their entered time is in. Everyone else
    sees it auto-converted to their own local time via Discord timestamps."""

    def __init__(self, guild_name: str, target_name: str, naive: datetime,
                 extras: dict | None = None):
        super().__init__(timeout=300)
        self.guild_name = guild_name
        self.target_name = target_name
        self.naive = naive
        self.extras = extras or {}
        select = discord.ui.Select(
            placeholder="Your timezone",
            options=[discord.SelectOption(label=k) for k in TIMEZONES],
        )
        select.callback = self.on_pick
        self.select = select
        self.add_item(select)

    async def on_pick(self, interaction: discord.Interaction):
        label = self.select.values[0]
        user_prefs.set_tz(interaction.user.id, label)   # remembered from now on
        ok = await create_event(interaction, self.guild_name,
                                self.target_name, self.naive,
                                self.extras, label)
        if ok:
            await interaction.response.edit_message(
                content=f"✅ **Scheduled!** Your timezone (**{label}**) is "
                        "saved — you won't be asked again. The signup card is "
                        "posted below.",
                view=None)



class SetupView(discord.ui.View):
    """Pick a guild + a raid, then hit Schedule.

    Guild options come from this server's saved config.
    """

    def __init__(self, server_id: int):
        super().__init__(timeout=300)
        self.guild_name: str | None = None
        self.target_name: str | None = None

        names = cfg.guild_names(server_id)
        self.guild_select = discord.ui.Select(
            placeholder="Which guild is playing?",
            options=[discord.SelectOption(label=g) for g in names[:25]],
        )
        self.guild_select.callback = self.on_guild
        self.add_item(self.guild_select)

        # Every raid is schedulable — "available" only gates the guide.
        options = [discord.SelectOption(label=name)
                   for name in guides.loader.RAIDS]
        placeholder = "Which raid?"
        self.target_select = discord.ui.Select(placeholder=placeholder,
                                               options=options)
        self.target_select.callback = self.on_target
        self.add_item(self.target_select)

    async def on_guild(self, interaction: discord.Interaction):
        self.guild_name = self.guild_select.values[0]
        await interaction.response.defer()

    async def on_target(self, interaction: discord.Interaction):
        self.target_name = self.target_select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Schedule ➜", style=discord.ButtonStyle.success, row=2)
    async def schedule(self, interaction: discord.Interaction, _):
        if not self.guild_name or not self.target_name:
            await interaction.response.send_message(
                "Pick both a guild and a raid first.", ephemeral=True)
            return
        await interaction.response.send_message(
            "**Set the date** — pick a day, add notes if you want, then "
            "Continue:",
            view=DatePickView(self.guild_name, self.target_name),
            ephemeral=True)

    @discord.ui.button(label="✖ Cancel", style=discord.ButtonStyle.secondary, row=2)
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(
            content="Scheduling cancelled.", view=None)
