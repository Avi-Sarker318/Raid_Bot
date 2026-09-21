"""Scans raids/ for content and exposes RAIDS,
raid_label() and highest_cap_level()."""
import pkgutil
import importlib

import guides.raids as _raids_pkg

RAIDS = {}
for m in pkgutil.iter_modules(_raids_pkg.__path__):
    if m.name.startswith("_"):
        continue
    mod = importlib.import_module(f"guides.raids.{m.name}")
    # A raid can be a single module (mod.RAID) or a package whose RAID dict
    # lives in a `data` submodule (e.g. ghastly/data.py). Every raid folder
    # exposes its metadata + assembled RAID dict in data.py.
    raid = getattr(mod, "RAID", None)
    if raid is None and m.ispkg:
        try:
            sub = importlib.import_module(f"guides.raids.{m.name}.data")
            raid = getattr(sub, "RAID", None)
        except ModuleNotFoundError:
            raid = None
    if raid is not None:
        RAIDS[raid["name"]] = raid



def raid_label(name: str) -> str:
    r = RAIDS[name]
    return name if r["available"] else f"🚧 {name} (coming soon)"


def highest_cap_level(name: str) -> str:
    caps = RAIDS[name].get("stat_caps", {})
    return max(caps, key=int) if caps else ""
