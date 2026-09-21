"""Loads Ghastly's gear guides from left/ and right/ into GEAR = {key: dict}."""
import os
import pkgutil
import importlib

_HERE = os.path.dirname(__file__)
GEAR: dict[str, dict] = {}
for side in ("right", "left"):
    side_dir = os.path.join(_HERE, side)
    if not os.path.isdir(side_dir):
        continue
    for m in pkgutil.iter_modules([side_dir]):
        if m.name.startswith("_"):
            continue
        mod = importlib.import_module(
            f"guides.raids.ghastly.gear.{side}.{m.name}")
        if hasattr(mod, "GEAR"):
            GEAR[m.name] = mod.GEAR
