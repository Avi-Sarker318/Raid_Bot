"""Core: the Discord client, command tree, and event storage.

Everything else imports from here; this imports no other bot module,
so there are never circular imports.
"""
import json
import os

import discord
from discord import app_commands

from data.paths import data_file
DATA_FILE = data_file("events.json")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def load_events() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_events(events: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(events, f, indent=2)

events = load_events()


events: dict = load_events()
