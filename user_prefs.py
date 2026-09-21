"""Per-user preferences — currently just their timezone.

Discord doesn't expose a user's timezone to bots, so the first time
someone schedules they pick it once; after that it's remembered and
the picker is skipped. Stored in user_prefs.json.
"""
import json
import os

from data.paths import data_file
PATH = data_file("user_prefs.json")


def _load() -> dict:
    if os.path.exists(PATH):
        with open(PATH) as f:
            return json.load(f)
    return {}


def get_tz(user_id: int) -> str | None:
    return _load().get(str(user_id), {}).get("tz")


def set_tz(user_id: int, tz_label: str) -> None:
    data = _load()
    data.setdefault(str(user_id), {})["tz"] = tz_label
    with open(PATH, "w") as f:
        json.dump(data, f, indent=2)
