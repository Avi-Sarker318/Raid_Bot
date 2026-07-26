"""Maps each raid's name to its signup ROLES (team format).

Add a new raid's format by dropping a <name>_format.py here with a ROLES
dict, then add it to FORMATS below.
"""
from . import (ghastly_format, cabal_format, veil_format,
               void_format, sky_format)

# raid name (as it appears in guides) -> ROLES
FORMATS = {
    "Ghastly Conspiracy Raid": ghastly_format.ROLES,
    "Cabal Revenge Raid": cabal_format.ROLES,
    "Blighted Veil Raid": veil_format.ROLES,
    "Voracious Void Raid": void_format.ROLES,
    "Crying Sky Raid": sky_format.ROLES,
}


def roles_for(raid_name: str) -> dict:
    """Signup roles for a raid; falls back to generic 8 if unknown."""
    if raid_name in FORMATS:
        return dict(FORMATS[raid_name])
    return {f"Player {i}": 1 for i in range(1, 9)}
