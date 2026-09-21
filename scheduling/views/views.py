"""Assembles the signup card: make_signup_view() wires the buttons from
card.py, manage.py, results.py, and reschedule.py."""
import discord

from core import events
from scheduling.card import *  # noqa: F401,F403
from scheduling.manage import *  # noqa: F401,F403
from scheduling.results import *  # noqa: F401,F403
from scheduling.reschedule import *  # noqa: F401,F403


def make_signup_view(ev: dict) -> discord.ui.View:
    view = discord.ui.View(timeout=None)
    # Signup buttons fill rows 0–2 (max 5 each = 15 slots, enough for 12
    # players). Controls live on rows 3–4. We keep same-team roles together
    # and wrap to the next row when a row fills.
    from scheduling.card import _group_of
    roles = list(ev["roles"])
    row, in_row, last_group = 0, 0, object()
    for role in roles:
        grp = _group_of(role)
        # start a new row when the current one is full, or (when there's
        # space to spare) when the team changes and the row isn't empty
        if in_row == 5 or (grp != last_group and in_row and row < 2
                           and len(roles) <= 10):
            row += 1
            in_row = 0
        if row > 2:      # safety: never collide with control rows
            row, in_row = 2, in_row
        view.add_item(SignupButton(ev, role, row=row))
        in_row += 1
        last_group = grp
    view.add_item(ManageButton(ev["id"]))
    view.add_item(HistoryButton(ev["id"]))
    view.add_item(FinishButton(ev["id"]))
    view.add_item(CancelButton(ev["id"]))
    view.add_item(RescheduleButton(ev["id"]))
    return view


async def refresh_card(ev: dict):
    """Re-render the public card (embed + buttons) after any change."""
    from miscellaneous import names as N
    await N.learn_event(ev)            # names instead of raw IDs
    from core import client
    from scheduling.card import build_embed
    try:
        chan = client.get_channel(ev["channel_id"])
        msg = await chan.fetch_message(ev["message_id"])
        await msg.edit(embed=build_embed(ev), view=make_signup_view(ev))
    except Exception:
        pass
    # Keep the "needs N more" alert in step with mod adds/switches too.
    from scheduling.card import sync_need_alert
    await sync_need_alert(ev)
