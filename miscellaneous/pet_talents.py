"""Wizard101 pet-talent stat formulas.

Every talent's granted stat is a linear function of the pet's five base
stats. A talent gives:

    coef * (2*stat_a + 2*stat_b + Power)

where (stat_a, stat_b, coef) come from the table below. The in-game client
shows the *rounded* result, so `value_of` rounds to match what a player
sees on their pet. The parenthetical numbers in the source guide are the
values at max stats — used only to sanity-check the coefficients.

Stats: Strength (S), Intellect (I), Agility (A), Will (W), Power (P).
Each entry: (label, unit, stat_a, stat_b, coef).
"""

from decimal import Decimal, ROUND_HALF_UP

S, I, A, W, P = "str", "int", "agi", "will", "pow"

# (display label, unit suffix, stat_a, stat_b, coefficient)
TALENTS = [
    ("Damage-Dealer",       "% Damage",          S, W, 3/400),
    ("Damage-Giver",        "% Damage",          S, W, 2/400),
    ("Damage-Boon",         "% Damage",          S, W, 1/400),
    ("Resistance-Ward",     "% Resist",          S, A, 3/250),
    ("Resistance-Proof",    "% Resist",          S, A, 2/250),
    ("Resistance-Away",     "% Resist",          S, A, 1/250),
    ("Accuracy-Sniper",     "% Accuracy",        I, A, 3/400),
    ("Accuracy-Shot",       "% Accuracy",        I, A, 2/400),
    ("Accuracy-Eye",        "% Accuracy",        I, A, 1/400),
    ("Critical Assailant",  " Critical",         A, W, 25/1000),
    ("Critical Striker (26)", " Critical",       A, W, 20/1000),
    ("Critical Striker (31)", " Critical",       A, W, 24/1000),
    ("Critical Hitter",     " Critical",         A, W, 18/1000),
    ("Defender",            " Critical Block",   I, W, 24/1000),
    ("Blocker",             " Critical Block",   I, W, 18/1000),
    ("Armor Breaker",       " Armor Piercing",   S, A, 5/2000),
    ("Armor Piercer",       " Armor Piercing",   S, A, 3/2000),
    ("Medic",               "% Outgoing Heal",   S, W, 13/2000),
    ("Healer",              "% Outgoing Heal",   S, W, 6/2000),
    ("Lively",              "% Incoming Heal",   I, A, 13/2000),
    ("Healthy",             "% Incoming Heal",   I, A, 6/2000),
    ("Health Bounty",       " Health",           A, W, 12/100),
    ("Health Gift",         " Health",           A, W, 10/100),
    ("Health Boost",        " Health",           A, W, 8/100),
    ("Add Health",          " Health",           A, W, 6/100),
    ("Mana Bounty",         " Mana",             I, W, 10/100),
    ("Mana Gift",           " Mana",             I, W, 8/100),
    ("Mana Boost",          " Mana",             I, W, 6/100),
    ("Extra Mana",          " Mana",             I, W, 4/100),
    ("Pip O'Plenty",        "% Power Pip",       S, I, 1/250),
    ("Pip Conserver",       " Pip Conversion",   A, W, 24/1000),
    ("Pip Saver",           " Pip Conversion",   A, W, 18/1000),
    ("Stun Recalcitrant",   "% Stun Resist",     S, I, 8/1000),
    ("Stun Resistant",      "% Stun Resist",     S, I, 4/1000),
    ("Epic Fishing Luck",   "% Fishing Luck",    I, W, 1/400),
    ("Fishing Luck",        "% Fishing Luck",    I, W, 1/400),
    ("Archmastery Boost",   "% Archmastery",     S, I, 1/25),
]

# Base stat caps (talents/gear can push a pet above these).
CAPS = {S: 255, I: 250, A: 260, W: 260, P: 250}
CAP_LABEL = {S: "Strength", I: "Intellect", A: "Agility", W: "Will", P: "Power"}


def value_of(coef: float, a: str, b: str, stats: dict) -> int:
    """The stat a talent grants for the given pet stats, rounded to the
    nearest whole number to match the in-game display (e.g. 8.6 -> 9,
    9.6 -> 10). Exact halves round up (22.5 -> 23), not to even. The game
    shows rounded values, not truncated ones."""
    raw = coef * (2 * stats[a] + 2 * stats[b] + stats[P])
    return int(Decimal(str(raw)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def all_values(stats: dict) -> list[tuple[str, str, int]]:
    """(label, unit, rounded_value) for every talent, in table order."""
    return [(label, unit, value_of(coef, a, b, stats))
            for (label, unit, a, b, coef) in TALENTS]