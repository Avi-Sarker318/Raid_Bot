"""Per-server configuration: guild names and the mods/admins who can manage raids.

Saved to server_config.json, keyed by Discord server (guild) ID as a string.
Note: "guild" here has two meanings — a Discord server, and an in-game
Wizard101 guild. We store a list of in-game guild NAMES per Discord server.
"""

import json
import os

from data.paths import data_file
CONFIG_FILE = data_file("server_config.json")


def _load() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


_config = _load()


def get_server(server_id: int) -> dict:
    """Return this Discord server's config, creating a blank one if needed."""
    key = str(server_id)
    if key not in _config:
        _config[key] = {"guild_names": [], "staff_ids": []}
    return _config[key]


def set_guild_names(server_id: int, names: list[str]) -> None:
    get_server(server_id)["guild_names"] = names
    _save(_config)


def set_staff(server_id: int, user_ids: list[int]) -> None:
    get_server(server_id)["staff_ids"] = [int(u) for u in user_ids]
    _save(_config)


def banned_ids(server_id: int) -> list[int]:
    return get_server(server_id).setdefault("banned_ids", [])


def ban_user(server_id: int, user_id: int) -> None:
    b = banned_ids(server_id)
    if int(user_id) not in b:
        b.append(int(user_id))
        _save(_config)


def unban_user(server_id: int, user_id: int) -> None:
    b = banned_ids(server_id)
    if int(user_id) in b:
        b.remove(int(user_id))
        _save(_config)


def is_owner(user_id: int) -> bool:
    from config import OWNER_IDS
    return int(user_id) in OWNER_IDS


def is_banned(server_id: int, user_id: int) -> bool:
    if is_owner(user_id):
        return False                     # the bot owner can't be banned
    return int(user_id) in banned_ids(server_id)


def guild_names(server_id: int) -> list[str]:
    return get_server(server_id)["guild_names"]


def staff_ids(server_id: int) -> list[int]:
    return get_server(server_id)["staff_ids"]


def is_staff(server_id: int, member) -> bool:
    """True if the member is the bot owner, a configured mod/admin, OR has
    Manage Server."""
    if is_owner(member.id) or member.id in staff_ids(server_id):
        return True
    perms = getattr(member, "guild_permissions", None)
    return bool(perms and perms.manage_guild)


def log_channel_id(server_id) -> int | None:
    if server_id is None:
        return None
    return get_server(server_id).get("log_channel_id")


def set_log_channel(server_id: int, channel_id: int | None) -> None:
    get_server(server_id)["log_channel_id"] = channel_id
    _save(_config)


def is_configured(server_id: int) -> bool:
    return bool(guild_names(server_id))
