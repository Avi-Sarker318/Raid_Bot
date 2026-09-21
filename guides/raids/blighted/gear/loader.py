"""Loads Blighted Veil's gear guides (one module per role/group) into
GEAR = {group_key: dict}, ordered by each module's `order`."""
import os
import pkgutil
import importlib

_HERE = os.path.dirname(__file__)
_found = {}
for m in pkgutil.iter_modules([_HERE]):
    if m.name.startswith("_") or m.name == "loader":
        continue
    mod = importlib.import_module(f"guides.raids.blighted.gear.{m.name}")
    if hasattr(mod, "GEAR"):
        _found[m.name] = mod.GEAR

# group key → guide dict, in the order the picker shows them
GEAR: dict[str, dict] = dict(
    sorted(_found.items(), key=lambda kv: kv[1].get("order", 99)))
