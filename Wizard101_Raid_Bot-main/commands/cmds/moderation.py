"""/testreport, /ban, /unban — staff tools for reports and raid bans."""
import discord
from discord import app_commands

import server_config as cfg
from config import TEST_MODE
from core import tree
from miscellaneous import history


# ─────────────── COMMAND: /testreport ───────────────
@tree.command(name="testreport",
              description="[TEST MODE] Post this month's report now, then clear it")
async def testreport(interaction: discord.Interaction):
    if not TEST_MODE:
        await interaction.response.send_message(
            "That command only works when **TEST_MODE=true** in the .env "
            "(it's for testing alone).", ephemeral=True)
        return
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Staff only.", ephemeral=True)
        return
    summ = history.month_summary(interaction.guild_id)
    if summ is None:
        await interaction.response.send_message(
            "No raids recorded yet this month — finish a raid first, then try "
            "again.", ephemeral=True)
        return
    month, text = summ
    e = discord.Embed(
        title=f"📜 Raid tracking — {month}",
        description=text + "\n\n*(Test report — this data has now been "
                           "deleted and the tracker restarted.)*",
        color=0x8A2BE2)
    await interaction.channel.send(embed=e)
    history.clear_month(interaction.guild_id)
    await interaction.response.send_message(
        "✅ Test report posted and the tracker cleared.", ephemeral=True)


# ─────────────── COMMANDS: /ban + /unban (per-server raid bans) ───────────────
@tree.command(name="ban",
              description="Ban a user from joining any raid in this server")
@app_commands.describe(user="The member to ban from raids")
async def ban(interaction: discord.Interaction, user: discord.User):
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins can ban users from raids.", ephemeral=True)
        return
    cfg.ban_user(interaction.guild_id, user.id)
    # Remove them from any raids they're currently signed up for.
    from core import events, save_events
    from scheduling.views.views import refresh_card
    removed = 0
    for ev in events.values():
        # Bans are per-server, so only pull them from THIS server's raids.
        if ev.get("guild_id") != interaction.guild_id:
            continue
        touched = False
        for role, lst in ev.get("signups", {}).items():
            if user.id in lst:
                lst.remove(user.id)
                removed += 1
                touched = True
        if touched:
            try:
                await refresh_card(ev)
            except Exception:
                pass
    save_events(events)
    await interaction.response.send_message(
        f"🚫 {user.mention} is now **banned** from joining raids in this "
        f"server. Removed them from {removed} open spot(s). Use **/unban** "
        "to reverse it.", ephemeral=True)


@tree.command(name="unban",
              description="Lift a user's raid ban in this server")
@app_commands.describe(user="The member to unban")
async def unban(interaction: discord.Interaction, user: discord.User):
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins can unban users.", ephemeral=True)
        return
    if not cfg.is_banned(interaction.guild_id, user.id):
        await interaction.response.send_message(
            f"{user.mention} isn't banned.", ephemeral=True)
        return
    cfg.unban_user(interaction.guild_id, user.id)
    await interaction.response.send_message(
        f"✅ {user.mention} can join raids again.", ephemeral=True)
