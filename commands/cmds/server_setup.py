"""/setup, /assign and /setlog — per-server configuration.

/setup names the in-game guilds this server raids for; /assign picks the
mods and admins allowed to manage raids. Both are staff-gated.
"""
import discord

import server_config as cfg
from core import tree


class GuildNamesModal(discord.ui.Modal, title="Name your guilds"):
    """One form: type each in-game guild name on its own line. Pre-filled
    with the current names so you can edit, rename, add, or remove them."""

    def __init__(self, current: list[str] | None = None):
        super().__init__()
        self.names_input = discord.ui.TextInput(
            label="Guild names — one per line",
            style=discord.TextStyle.paragraph,
            placeholder="SGD Guild\nSecond Guild\nThird Guild",
            default="\n".join(current) if current else None,
            required=True,
            max_length=1000,
        )
        self.add_item(self.names_input)

    async def on_submit(self, interaction: discord.Interaction):
        names = [n.strip() for n in self.names_input.value.splitlines() if n.strip()]
        names = names[:25]  # Discord select-menu limit
        if not names:
            await interaction.response.send_message(
                "No names found — type at least one guild name.", ephemeral=True
            )
            return
        cfg.set_guild_names(interaction.guild_id, names)
        listed = "\n".join(f"• {n}" for n in names)
        await interaction.response.send_message(
            f"✅ Saved {len(names)} guild(s):\n{listed}\n\n"
            "Next: run **/assign** to choose which mods/admins can manage raids. "
            "This setup is saved for **this server only** — other servers won't "
            "see it.",
            ephemeral=True,
        )


@tree.command(name="setup", description="Set up the guild names for this server")
async def setup(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Run this in a server, not a DM.", ephemeral=True
        )
        return
    # Manage Server permission OR already a configured mod/admin
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins (or someone with **Manage Server**) can run /setup.",
            ephemeral=True,
        )
        return
    await interaction.response.send_modal(
        GuildNamesModal(cfg.guild_names(interaction.guild_id)))


# ─────────────── COMMAND: /assign ───────────────
class StaffPickerView(discord.ui.View):
    """Pick the mods/admins who can manage raids and override signups."""

    def __init__(self, server_id: int):
        super().__init__(timeout=300)
        self.server_id = server_id
        self.picker = discord.ui.UserSelect(
            placeholder="Select the mods & admins in charge",
            min_values=1,
            max_values=25,
        )
        self.picker.callback = self.on_pick
        self.add_item(self.picker)

    async def on_pick(self, interaction: discord.Interaction):
        ids = [u.id for u in self.picker.values]
        cfg.set_staff(self.server_id, ids)
        mentions = " ".join(f"<@{i}>" for i in ids)
        await interaction.response.send_message(
            f"✅ Assigned! Mods & admins: {mentions}\n\n"
            "They can schedule/cancel raids, reassign signups, re-run **/setup** "
            "to edit guilds, and re-run **/assign** to change this list. "
            "Anyone can now use **/schedule** to schedule and **/guide** for help.",
            ephemeral=True,
        )


@tree.command(name="assign",
              description="Choose which mods/admins can manage raids in this server")
async def assign(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Run this in a server, not a DM.", ephemeral=True
        )
        return
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins (or someone with **Manage Server**) can run /assign.",
            ephemeral=True,
        )
        return
    if not cfg.is_configured(interaction.guild_id):
        await interaction.response.send_message(
            "Run **/setup** first to add this server's guild names.",
            ephemeral=True,
        )
        return
    await interaction.response.send_message(
        "Choose who's in charge below:",
        view=StaffPickerView(interaction.guild_id),
        ephemeral=True,
    )


# ─────────────── COMMAND: /setlog ───────────────
@tree.command(name="setlog",
              description="Pick the private channel for the mod log (who "
                          "joined/left)")
@discord.app_commands.describe(
    channel="Private mods-only channel. Leave empty to turn the log off.")
async def setlog(interaction: discord.Interaction,
                 channel: discord.TextChannel | None = None):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Run this in a server, not a DM.", ephemeral=True)
        return
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins can set the mod log.", ephemeral=True)
        return
    if channel is None:
        cfg.set_log_channel(interaction.guild_id, None)
        await interaction.response.send_message(
            "📜 Mod log turned **off**. Late leaves (inside 3 hours) will be "
            "DM'd to the bot owner and staff instead.", ephemeral=True)
        return
    perms = channel.permissions_for(interaction.guild.me)
    if not (perms.send_messages and perms.embed_links):
        await interaction.response.send_message(
            f"I can't post in {channel.mention} — give me **Send Messages** "
            "and **Embed Links** there, then try again.", ephemeral=True)
        return
    cfg.set_log_channel(interaction.guild_id, channel.id)
    await interaction.response.send_message(
        f"📜 Mod log set to {channel.mention}. Every join, leave (with who "
        "and how close to start), mod change, ban and cancel goes there.\n"
        "Keep this channel **mods-only** — it shows names.", ephemeral=True)
    try:
        await channel.send(embed=discord.Embed(
            title="📜 Mod log is on",
            description=f"Set up by {interaction.user.mention}. Raid joins, "
                        "leaves, mod changes, bans and cancels will show up "
                        "here.", color=0x5865F2))
    except discord.HTTPException:
        pass
