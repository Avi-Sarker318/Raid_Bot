"""Mod signup control: add / replace / switch / remove."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import discord

import guides.loader
import guides.loader as raid_defs
import server_config as cfg
import user_prefs
from config import TEST_MODE, REMINDER_MINUTES
from core import client, events, save_events


def _occupant(ev: dict, role: str) -> int | None:
    lst = ev["signups"].get(role, [])
    return lst[0] if lst else None


MANAGE_HEADER = (
    "**Manage signups** — here's what you can do:\n"
    "➕ **Add** a player to an open spot • 🔄 **Replace** who's in a "
    "spot • 🔁 **Switch** two players • ➖ **Remove** a player")


def _menu(status: str = "") -> str:
    """The manage menu text, with an optional status line on top so the
    message stays self-contained (no scrolling back for the instructions)."""
    return (f"{status}\n\n{MANAGE_HEADER}" if status else MANAGE_HEADER)


class ManageView(discord.ui.View):
    """Ephemeral menu for mods: exactly what they can do to the signups.
    Everything happens in THIS one message — each step edits it in place."""

    def __init__(self, ev: dict):
        super().__init__(timeout=180)
        self.ev = ev

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        """Runs before EVERY button in this view — non-staff can't touch
        any of it, even if they somehow get a handle on the message."""
        if cfg.is_staff(itx.guild_id, itx.user):
            return True
        await itx.response.send_message(
            "Only mods/admins can manage signups.", ephemeral=True)
        return False

    @discord.ui.button(label="➕ Add player", style=discord.ButtonStyle.success)
    async def add(self, itx: discord.Interaction, _):
        open_roles = [r for r in self.ev["roles"] if not _occupant(self.ev, r)]
        if not open_roles:
            await itx.response.edit_message(
                content=_menu("⚠️ No open positions."),
                view=ManageView(self.ev))
            return
        await itx.response.edit_message(
            content="Add a player — pick the **open position**, then the person:",
            view=RolePickView(self.ev, open_roles, mode="add"))

    @discord.ui.button(label="🔄 Replace player", style=discord.ButtonStyle.primary)
    async def replace(self, itx: discord.Interaction, _):
        filled = [r for r in self.ev["roles"] if _occupant(self.ev, r)]
        if not filled:
            await itx.response.edit_message(
                content=_menu("⚠️ No filled positions."),
                view=ManageView(self.ev))
            return
        await itx.response.edit_message(
            content="Replace a player — pick the **position to replace**, "
                    "then the new person:",
            view=RolePickView(self.ev, filled, mode="replace"))

    @discord.ui.button(label="🔁 Switch players", style=discord.ButtonStyle.primary)
    async def switch(self, itx: discord.Interaction, _):
        filled = [r for r in self.ev["roles"] if _occupant(self.ev, r)]
        if len(filled) < 2:
            await itx.response.edit_message(
                content=_menu("⚠️ Need at least two filled positions to switch."),
                view=ManageView(self.ev))
            return
        await itx.response.edit_message(
            content="Switch two players — pick the **first position**:",
            view=RolePickView(self.ev, filled, mode="switch"))

    @discord.ui.button(label="➖ Remove player", style=discord.ButtonStyle.danger)
    async def remove(self, itx: discord.Interaction, _):
        filled = [r for r in self.ev["roles"] if _occupant(self.ev, r)]
        if not filled:
            await itx.response.edit_message(
                content=_menu("⚠️ No filled positions."),
                view=ManageView(self.ev))
            return
        await itx.response.edit_message(
            content="Remove a player — pick the **position to clear**:",
            view=RolePickView(self.ev, filled, mode="remove"))

    @discord.ui.button(label="✖ Done", style=discord.ButtonStyle.secondary,
                       row=1)
    async def done(self, itx: discord.Interaction, _):
        await itx.response.edit_message(
            content="Finished managing signups.", view=None)


class RolePickView(discord.ui.View):
    """Pick a role; behavior depends on mode (add/replace/switch/remove)."""

    def __init__(self, ev: dict, roles: list[str], mode: str,
                 first_role: str | None = None):
        super().__init__(timeout=180)
        self.ev, self.mode, self.first_role = ev, mode, first_role
        sel = discord.ui.Select(
            placeholder="Which position?",
            options=[discord.SelectOption(label=r) for r in roles],
        )
        sel.callback = self.on_pick
        self.sel = sel
        self.add_item(sel)

        back = discord.ui.Button(label="⬅ Back", row=1,
                                 style=discord.ButtonStyle.secondary)

        async def go_back(itx: discord.Interaction):
            await itx.response.edit_message(
                content=_menu(), view=ManageView(self.ev))
        back.callback = go_back
        self.add_item(back)

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        """Runs before every control in this view — non-staff can't use it."""
        if cfg.is_staff(itx.guild_id, itx.user):
            return True
        await itx.response.send_message(
            "Only mods/admins can manage signups.", ephemeral=True)
        return False

    async def on_pick(self, itx: discord.Interaction):
        role = self.sel.values[0]
        ev = self.ev
        if self.mode == "remove":
            uid = _occupant(ev, role)
            from scheduling.card import _is_full, _announce_dropout
            was_full = _is_full(ev)
            ev["signups"][role] = []
            save_events(events)
            from scheduling.views.views import refresh_card
            await refresh_card(ev)
            await itx.response.edit_message(
                content=_menu(f"➖ Removed <@{uid}> from **{role}**."),
                view=ManageView(ev))
            # If that broke a full roster close to start, raise the alarm.
            if was_full and uid:
                await _announce_dropout(itx, ev, role, uid)
            return
        if self.mode == "switch":
            if self.first_role is None:
                remaining = [r for r in ev["roles"]
                             if _occupant(ev, r) and r != role]
                await itx.response.edit_message(
                    content=f"Switching **{role}** — now pick the "
                            "**second position**:",
                    view=RolePickView(ev, remaining, "switch", first_role=role))
                return
            a, b = self.first_role, role
            ev["signups"][a], ev["signups"][b] = (
                ev["signups"].get(b, []), ev["signups"].get(a, []))
            save_events(events)
            from scheduling.views.views import refresh_card
            await refresh_card(ev)
            await itx.response.edit_message(
                content=_menu(f"🔁 Switched **{a}** ↔ **{b}**."),
                view=ManageView(ev))
            return
        # add / replace → pick the person
        await itx.response.edit_message(
            content=f"Now pick the player for **{role}**:",
            view=UserPickView(ev, role, self.mode))


class UserPickView(discord.ui.View):
    def __init__(self, ev: dict, role: str, mode: str):
        super().__init__(timeout=180)
        self.ev, self.role, self.mode = ev, role, mode
        picker = discord.ui.UserSelect(placeholder=f"Player for {role}",
                                       min_values=1, max_values=1)
        picker.callback = self.on_pick
        self.picker = picker
        self.add_item(picker)

        back = discord.ui.Button(label="⬅ Back", row=1,
                                 style=discord.ButtonStyle.secondary)

        async def go_back(itx: discord.Interaction):
            await itx.response.edit_message(
                content=_menu(), view=ManageView(self.ev))
        back.callback = go_back
        self.add_item(back)

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        """Runs before every control in this view — non-staff can't use it."""
        if cfg.is_staff(itx.guild_id, itx.user):
            return True
        await itx.response.send_message(
            "Only mods/admins can manage signups.", ephemeral=True)
        return False

    async def on_pick(self, itx: discord.Interaction):
        member = self.picker.values[0]
        ev = self.ev
        # Admins may place the same person in several different roles (e.g.
        # someone dual-boxing), so we do NOT strip them from other spots here.
        # Public self-service Join is still one-position-per-person; that's
        # enforced in SignupButton, not here.
        old = _occupant(ev, self.role)
        ev["signups"][self.role] = [member.id]
        save_events(events)
        from scheduling.views.views import refresh_card
        await refresh_card(ev)
        verb = (f"🔄 Replaced <@{old}> with {member.mention}"
                if self.mode == "replace" and old
                else f"➕ Added {member.mention}")
        await itx.response.edit_message(
            content=_menu(f"{verb} in **{self.role}**."),
            view=ManageView(ev))


class ManageButton(discord.ui.Button):
    """Opens the mod-only assignment panel."""

    def __init__(self, event_id: str):
        super().__init__(
            label="Manage signups (mod)",
            style=discord.ButtonStyle.secondary,
            custom_id=f"manage:{event_id}",
            row=3,
        )
        self.event_id = event_id

    async def callback(self, interaction: discord.Interaction):
        ev = events.get(self.event_id)
        if ev is None:
            await interaction.response.send_message("Event gone.", ephemeral=True)
            return
        if not cfg.is_staff(interaction.guild_id, interaction.user):
            await interaction.response.send_message(
                "Only mods/admins can manage signups.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            _menu(), view=ManageView(ev), ephemeral=True)