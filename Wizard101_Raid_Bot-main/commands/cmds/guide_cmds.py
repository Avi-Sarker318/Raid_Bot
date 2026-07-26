"""/guide — opens the raid guide browser (ephemeral, only you see it)."""
import discord

from core import tree

from ..guide.nav import guide_screen


@tree.command(name="guide", description="Browse raid guides (only you see it)")
async def guide(interaction: discord.Interaction):
    embed, view = guide_screen("top")
    await interaction.response.send_message(embed=embed, view=view,
                                            ephemeral=True)
