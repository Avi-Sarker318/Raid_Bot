"""Central location for the bot's saved data files (JSON).

Keeping them in one folder makes backups and .gitignore simple.
"""
import os

DATA_DIR = os.path.dirname(__file__)


def data_file(name: str) -> str:
    """Absolute path to a file inside data/ (e.g. data_file('history.json'))."""
    return os.path.join(DATA_DIR, name)
