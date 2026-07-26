"""/cancelraid, /clearhistory, /clearallevents — destructive staff actions.

Each one goes through _ConfirmView first, so nothing damaging is ever a
single tap.
"""
import discord
from discord import app_commands

import server_config as cfg
from core import client, events, save_events, tree
from miscellaneous import history


# ─────────────── COMMANDS: /cancelraid + /clearhistory (staff) ───────────────
class _ConfirmView(discord.ui.View):
    """Generic yes/no confirm so a destructive action is never one tap."""

    def __init__(self, on_yes, label: str):
        super().__init__(timeout=60)
        self.on_yes = on_yes
        self.confirm.label = label

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, itx: discord.Interaction, _):
        await self.on_yes(itx)

    @discord.ui.button(label="✖ Never mind", style=discord.ButtonStyle.secondary)
    async def cancel(self, itx: discord.Interaction, _):
        await itx.response.edit_message(content="Cancelled — nothing changed.",
                                        view=None)


@tree.command(name="cancelraid",
              description="Cancel the most recent raid, or all raids")
@app_commands.describe(scope="Which raids to cancel")
@app_commands.choices(scope=[
    app_commands.Choice(name="Last scheduled raid", value="last"),
    app_commands.Choice(name="ALL upcoming raids", value="all"),
])
async def cancelraid(interaction: discord.Interaction,
                     scope: app_commands.Choice[str]):
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins can cancel raids.", ephemeral=True)
        return

    mine = [e for e in events.values()
            if e.get("guild_id") == interaction.guild_id]
    if not mine:
        await interaction.response.send_message(
            "There are no scheduled raids to cancel.", ephemeral=True)
        return

    if scope.value == "last":
        target = [max(mine, key=lambda e: int(e["id"]))]
        what = f"**{target[0]['raid']}** ({target[0]['guild']})"
    else:
        target = mine
        what = f"**all {len(mine)} scheduled raid(s)**"

    async def do_cancel(itx: discord.Interaction):
        removed = 0
        for ev in target:
            # try to mark the public card as cancelled
            try:
                ch = client.get_channel(ev.get("channel_id"))
                if ch and ev.get("message_id"):
                    msg = await ch.fetch_message(ev["message_id"])
                    await msg.edit(embed=discord.Embed(
                        title=f"❌ {ev['raid']} — cancelled",
                        description=f"Cancelled by {itx.user.mention}.",
                        color=0x999999), view=None)
            except Exception:
                pass
            events.pop(ev["id"], None)
            removed += 1
        save_events(events)
        await itx.response.edit_message(
            content=f"❌ Cancelled {removed} raid(s).", view=None)

    await interaction.response.send_message(
        f"⚠️ This will cancel {what}. Signups will be lost. Continue?",
        view=_ConfirmView(do_cancel, "Yes, cancel"), ephemeral=True)


@tree.command(name="clearhistory",
              description="Wipe this server's raid history tracking")
async def clearhistory(interaction: discord.Interaction):
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins can clear history.", ephemeral=True)
        return
    summ = history.month_summary(interaction.guild_id)
    if summ is None:
        await interaction.response.send_message(
            "There's no history recorded yet.", ephemeral=True)
        return

    async def do_clear(itx: discord.Interaction):
        history.clear_month(itx.guild_id)
        await itx.response.edit_message(
            content="🧹 Raid history cleared for this server.", view=None)

    await interaction.response.send_message(
        "⚠️ This permanently deletes this server's recorded raid history "
        "(who played, counts, wins). Consider **📜 History → Share** first "
        "if you want a copy posted. Continue?",
        view=_ConfirmView(do_clear, "Yes, clear it"), ephemeral=True)


@tree.command(name="clearallevents",
              description="Remove ALL scheduled raids in this server (or just dead ones)")
@app_commands.describe(scope="What to remove")
@app_commands.choices(scope=[
    app_commands.Choice(name="Only dead entries (card deleted/missing)",
                        value="dead"),
    app_commands.Choice(name="EVERYTHING in this server", value="all"),
])
async def clearallevents(interaction: discord.Interaction,
                         scope: app_commands.Choice[str]):
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins can clear events.", ephemeral=True)
        return

    mine = [e for e in events.values()
            if e.get("guild_id") == interaction.guild_id]
    if not mine:
        await interaction.response.send_message(
            "This server has no stored raids.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    if scope.value == "all":
        target, what = mine, f"all **{len(mine)}** stored raid(s)"
    else:
        # "Dead" = the signup card no longer exists (deleted, or never posted).
        target = []
        for ev in mine:
            ch = client.get_channel(ev.get("channel_id"))
            if ch is None or not ev.get("message_id"):
                target.append(ev)
                continue
            try:
                await ch.fetch_message(ev["message_id"])
            except (discord.NotFound, discord.Forbidden):
                target.append(ev)
        if not target:
            await interaction.followup.send(
                "✅ Nothing to clean — every stored raid still has its signup "
                "card.", ephemeral=True)
            return
        what = f"**{len(target)}** dead entr{'y' if len(target)==1 else 'ies'}"

    ids = [e["id"] for e in target]

    async def do_clear(itx: discord.Interaction):
        for eid in ids:
            events.pop(eid, None)
        save_events(events)
        await itx.response.edit_message(
            content=f"🧹 Removed {len(ids)} raid(s) from **/raids**.",
            view=None)

    await interaction.followup.send(
        f"⚠️ This will remove {what} from **/raids**. Continue?",
        view=_ConfirmView(do_clear, "Yes, remove"), ephemeral=True)
