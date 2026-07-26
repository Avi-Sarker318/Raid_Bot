"""
Wizard101 Raid Bot — entry point.

  Raidbot/
    bot.py                 ← you are here
    core.py                  client + command tree + event storage
    config.py                .env → token, reminders, TEST_MODE
    user_prefs.py            remembered timezone per scheduler
    tasks.py                 reminder + monthly-report loop
    server_config.py         per-server guild names + staff
    guides/
      raids/ghastly/
        data.py              metadata + assembly of the RAID dict
        plan/                ★ game plan, split by topic (decks, dice,
                             stat_caps, two_v_two, fights_*)
    commands/
      cmds/                  the slash commands, grouped by purpose
      guide/                 /guide browser: tables · embeds · nav
      slash_commands.py      thin shim that imports both (kept for compat)
    scheduling/              card · time_input · manage · results · reschedule
    miscellaneous/           history · stat_caps
    Gear/ghastly/            left/ + right/ gear guides, one file per role

Run:  python bot.py
"""
from config import DISCORD_TOKEN, TEST_MODE
from core import client, tree, events, save_events

import commands.slash_commands                       # noqa: F401 — registers all commands
from commands.slash_commands import GuideNav
from scheduling.views.views import make_signup_view
import tasks


@client.event
async def on_ready():
    if TEST_MODE:
        print("🧪 TEST MODE ON — solo testing: multi-role signups, "
              "fast reminders, /testreport available.")
    await _prune_dead_events()
    for ev in events.values():
        client.add_view(make_signup_view(ev), message_id=ev.get("message_id"))
    client.add_dynamic_items(GuideNav)
    # Discord rate-limits command syncing heavily, so only sync when the
    # command set actually changed since last launch (tracked by a hash).
    await _sync_commands_if_changed()
    client.loop.create_task(tasks.reminder_loop())
    print(f"Logged in as {client.user} — {len(events)} saved event(s)")


async def _sync_commands_if_changed():
    import hashlib
    import json
    from data.paths import data_file

    cmds = sorted((c.name, c.description) for c in tree.get_commands())
    fingerprint = hashlib.sha256(json.dumps(cmds).encode()).hexdigest()
    stamp = data_file("commands.sync")
    try:
        with open(stamp) as f:
            if f.read().strip() == fingerprint:
                return                       # unchanged — skip the slow sync
    except FileNotFoundError:
        pass
    await tree.sync()
    with open(stamp, "w") as f:
        f.write(fingerprint)
    print("Slash commands synced.")


async def _prune_dead_events():
    """Drop stored raids whose signup card no longer exists.

    An event can outlive its card if someone deleted the message, or if the
    bot couldn't post it (missing permissions). Those would otherwise linger
    in /raids forever with nothing to click.
    """
    import discord
    dead = []
    for eid, ev in list(events.items()):
        mid = ev.get("message_id")
        ch = client.get_channel(ev.get("channel_id"))
        if ch is None or not mid:
            dead.append(eid)
            continue
        try:
            await ch.fetch_message(mid)
        except (discord.NotFound, discord.Forbidden):
            dead.append(eid)
        except Exception:
            pass          # transient error — keep the event, try again later
    for eid in dead:
        events.pop(eid, None)
    if dead:
        save_events(events)
        print(f"Cleaned {len(dead)} raid(s) whose signup card was gone.")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)