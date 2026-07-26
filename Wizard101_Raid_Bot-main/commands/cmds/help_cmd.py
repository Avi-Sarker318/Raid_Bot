"""/help — the full walkthrough of commands, buttons, and tracking."""
import discord

import server_config as cfg
from config import REMINDER_MINUTES, TEST_MODE
from core import tree


@tree.command(name="help",
              description="How the raid bot works — commands, roles, buttons")
async def help_cmd(interaction: discord.Interaction):
    is_staff = (interaction.guild is not None
                and cfg.is_staff(interaction.guild_id, interaction.user))

    e1 = discord.Embed(
        title="🧙 Wizard101 Raid Bot — Help",
        description=(
            "This bot schedules raids with click-to-join "
            "signups, reminds everyone before start, tracks who raided each "
            "month, and has a full in-Discord strategy guide.\n\n"
            "Below: who can do what, every command, the signup card buttons, "
            "and how monthly tracking works."),
        color=0x8A2BE2)

    e1.add_field(
        name="👥 Who can do what",
        value=(
            "**Everyone** — join open spots and leave your own spot by "
            "tapping role buttons, and use **/guide**.\n"
            "**Mods / admins / granted people** — schedule with **/schedule**, "
            "manage signups, edit/reschedule, finish raids, cancel, ban/unban "
            "players, view **📜 History**, and share monthly tracking. Access = "
            "anyone with **Manage Server**, plus anyone added via **/assign**."),
        inline=False)

    e1.add_field(
        name="📋 Commands",
        value=(
            "**/guide** — Browse decks, fights, gear, and stat caps. Only you "
            "see it. *(Everyone)*\n"
            "**/raids** — Browse upcoming raids one at a time (soonest "
            "first) with ◀ ▶. Staff also get 🗑 Remove. *(Everyone)*\n"
            "**/cancelraid** — Cancel the last raid, or all of them. "
            "*(Staff only)*\n"
            "**/clearallevents** — Wipe stored raids from /raids — all, or "
            "just dead ones whose card was deleted. *(Staff only)*\n"
            "**/clearhistory** — Wipe this server's raid tracking. "
            "*(Staff only)*\n"
            "**/help** — This message.\n"
            "**/setup** — Set or edit this server's guild names (opens "
            "pre-filled — rename, add, or delete lines). *(Staff only)*\n"
            "**/ban** / **/unban** — Block or allow a user from joining raids. "
            "*(Staff only)*\n"
            "**/assign** — Choose which mods/admins can manage raids. "
            "*(Staff only)*\n"
            "**/schedule** — Schedule a raid. "
            "*(Staff only)*"),
        inline=False)

    e2 = discord.Embed(color=0x8A2BE2)
    e2.add_field(
        name="🗓️ Scheduling a raid (staff)",
        value=(
            "**/schedule** → pick the guild and raid → pick the **date** from "
            "a calendar → pick the **hour, minutes, AM/PM, and duration** from "
            "labeled menus → pick your **timezone** (asked once, then "
            "remembered). Add optional **notes** along the way.\n"
            "The bot posts a signup card. **Everyone sees the start time in "
            "their own timezone automatically.**"),
        inline=False)

    e2.add_field(
        name="🎟️ The signup card buttons",
        value=(
            "**Join <role>** — claim an open spot. Once a spot is filled, its "
            "button turns into **Leave <role>** — only the person in it can "
            "free it (or a mod via Manage). One spot per person. *(Everyone)*\n"
            "**Manage signups (mod)** — ➕ Add, 🔄 Replace, 🔁 Switch, or ➖ "
            "Remove a player. *(Staff only)*\n"
            "**✏️ Edit / Reschedule** — change date/time/duration/notes. If the "
            "time changed, it asks whether to **notify** everyone signed up. "
            "*(Staff only)*\n"
            "**✅ Finish** — end the raid, record who played, and enter how "
            "many **wins** (blank = 0; editable later). Needs every spot "
            "filled. *(Staff only)*\n"
            "**📜 History (mod)** — this month's tracking. *(Staff only)*\n"
            "**Cancel Event** — delete the raid. *(Staff only)*"),
        inline=False)

    e3 = discord.Embed(color=0x8A2BE2)
    e3.add_field(
        name="⏰ Reminders & start time",
        value=(f"• **~{REMINDER_MINUTES} min before:** the bot pings everyone "
               "signed up to get ready.\n"
               "• **~5 min before:** if any spot is still open, the bot alerts "
               "mods with **⏩ Extend** / **❌ Cancel** buttons.\n"
               "• **At start:** if people are in, a mod hits **🚀 Raid Up!** to "
               "ping the roster that it's go-time. If **nobody** joined, the "
               "bot tags mods to extend or cancel — it never auto-cancels.\n"
               "Extending re-arms all of these for the new time."),
        inline=False)
    e3.add_field(
        name="📊 Monthly tracking",
        value=(
            "Every finished raid counts toward the month. **📜 History** shows "
            "who raided and how many, a breakdown by which raid/boss was run, "
            "and total wins — plus a button for each raid's roster.\n"
            "Staff can **📤 Share & delete** to post the list publicly and "
            "clear it. On the **1st of each month** the bot auto-posts the "
            "previous month and resets. Tracking is **per-server** — other "
            "servers never see it."),
        inline=False)
    e3.add_field(
        name="📖 The guide",
        value=("**/guide** → pick a raid → Right Side, Left Side, or Basics & "
               "gear. Includes role decks, a school-picker left-side deck, "
               "turn-by-turn fight tables (dice, 2v2, bosses), gear guides, "
               "and stat caps. Credit: K31Z, DHMO, FriedChicken935 & MJ — "
               "SGD Guild."),
        inline=False)

    if TEST_MODE:
        e3.add_field(
            name="🧪 Test mode is ON",
            value=("Solo testing: one person can fill every role, reminders "
                   "fire fast, and **/testreport** posts the monthly report on "
                   "demand. Turn off by setting `TEST_MODE=false` in .env."),
            inline=False)
    if not is_staff:
        e3.set_footer(text="You'll see extra options on cards if you're granted "
                           "mod access via /assign.")

    await interaction.response.send_message(embeds=[e1, e2, e3], ephemeral=True)
