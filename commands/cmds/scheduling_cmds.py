"""/schedule and /raids — creating raids and browsing upcoming ones."""
from datetime import datetime, timezone

import discord

import server_config as cfg
from core import client, events, save_events, tree
from scheduling.time_input import SetupView


# ─────────────── COMMAND: /schedule ───────────────
@tree.command(name="schedule", description="Schedule a new raid with signups")
async def schedule(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Run this in a server, not a DM.", ephemeral=True
        )
        return
    if not cfg.is_configured(interaction.guild_id):
        await interaction.response.send_message(
            "This server isn't set up yet. A mod/admin needs to run **/setup** "
            "first to add guild names.",
            ephemeral=True,
        )
        return
    if not cfg.is_staff(interaction.guild_id, interaction.user):
        await interaction.response.send_message(
            "Only mods/admins (or people granted access via **/assign**) can "
            "schedule. Anyone can use **/guide** to see raid strategies.",
            ephemeral=True,
        )
        return
    await interaction.response.send_message(
        "**Scheduling a raid.** Pick the guild and raid, then hit Schedule:",
        view=SetupView(interaction.guild_id),
        ephemeral=True,
    )


# ─────────────── COMMAND: /raids ───────────────
class RaidBrowser(discord.ui.View):
    """Paged view of this server's upcoming raids, soonest first.
    ◀ / ▶ to page through; 🗑 Remove (staff) deletes the one on screen."""

    def __init__(self, guild_id: int, is_staff: bool, index: int = 0):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.is_staff = is_staff
        self.index = index
        self._sync_buttons()

    # --- data ---
    def _raids(self) -> list:
        now = datetime.now(timezone.utc).timestamp()
        return sorted(
            (e for e in events.values()
             if e.get("guild_id") == self.guild_id and e["start_ts"] > now),
            key=lambda e: e["start_ts"])            # closest date first

    def _sync_buttons(self) -> None:
        total = len(self._raids())
        self.index = max(0, min(self.index, total - 1)) if total else 0
        self.prev.disabled = self.index <= 0
        self.next.disabled = self.index >= total - 1
        self.remove.disabled = total == 0
        # only staff can delete
        self.remove.disabled = self.remove.disabled or not self.is_staff

    def embed(self) -> discord.Embed:
        raids = self._raids()
        if not raids:
            return discord.Embed(
                title="📅 Upcoming raids",
                description="Nothing scheduled right now.",
                color=0x8A2BE2)
        ev = raids[self.index]
        start = int(ev["start_ts"])
        filled = sum(len(v) for v in ev["signups"].values())
        total = len(ev["roles"])
        from scheduling.card import roster_lines
        from miscellaneous.names import learn_event
        await learn_event(ev)
        roster = roster_lines(ev) or "*No one has signed up yet.*"
        e = discord.Embed(
            title=f"📅 {ev['raid']}",
            description=(f"**Guild:** {ev['guild']}\n"
                         f"**Starts:** <t:{start}:F> (<t:{start}:R>)\n"
                         f"**Duration:** {ev.get('duration_h', 1.5):g} hours\n"
                         f"**Filled:** {filled}/{total}\n\n{roster}"),
            color=0x8A2BE2)
        if ev.get("notes"):
            e.add_field(name="📝 Notes", value=ev["notes"][:1024], inline=False)
        e.set_footer(text=f"Raid {self.index + 1} of {len(raids)} • "
                          f"Event ID {ev['id']}")
        return e

    async def _refresh(self, itx: discord.Interaction) -> None:
        self._sync_buttons()
        await itx.response.edit_message(embed=self.embed(), view=self)

    # --- buttons ---
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def prev(self, itx: discord.Interaction, _):
        self.index -= 1
        await self._refresh(itx)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next(self, itx: discord.Interaction, _):
        self.index += 1
        await self._refresh(itx)

    @discord.ui.button(label="🗑 Remove this raid",
                       style=discord.ButtonStyle.danger)
    async def remove(self, itx: discord.Interaction, _):
        if not cfg.is_staff(itx.guild_id, itx.user):
            await itx.response.send_message(
                "Only mods/admins can remove raids.", ephemeral=True)
            return
        raids = self._raids()
        if not raids:
            await self._refresh(itx)
            return
        ev = raids[self.index]
        # mark the public card cancelled if it's still there
        try:
            ch = client.get_channel(ev.get("channel_id"))
            if ch and ev.get("message_id"):
                msg = await ch.fetch_message(ev["message_id"])
                await msg.edit(embed=discord.Embed(
                    title=f"❌ {ev['raid']} — cancelled",
                    description=f"Removed by {itx.user.mention}.",
                    color=0x999999), view=None)
        except Exception:
            pass
        events.pop(ev["id"], None)
        save_events(events)
        await self._refresh(itx)


@tree.command(name="raids", description="Browse upcoming scheduled raids")
async def raids(interaction: discord.Interaction):
    view = RaidBrowser(interaction.guild_id,
                       cfg.is_staff(interaction.guild_id, interaction.user))
    await interaction.response.send_message(
        embed=view.embed(), view=view, ephemeral=True)


# ─────────────── COMMAND: /guide (+ GuideNav routing) ───────────────
GHASTLY = "Ghastly Conspiracy Raid"
