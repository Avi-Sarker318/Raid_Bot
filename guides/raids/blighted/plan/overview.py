"""Blighted Veil Raid — team layout, callouts and dryad deposits.

Import from `plan` (the package re-exports everything), not from here.

Guide sheet by Roaring Raptors & Battling Giraffes (template by Major).
"""

# ---- who plays what ------------------------------------------------------
# 8 players: 4 Outside (one per compass side) + 4 Inside ("Vanguard").
OUTSIDE_PLAYERS = ["North", "East", "South", "West"]

INSIDE_NOTE = (
    "Inside players are named for their school combo: **-ice** is any Ice "
    "build (main Ice, Fice, Bice, Lice, Mice or Dice), **Lyth/Mife** = "
    "Life + Myth, **Stire** = Storm + Fire, **Steath** = Storm + Death, "
    "**Stife** = Storm + Life, **Dyth** = Death + Myth. Gear for each is "
    "under 📐 Gear.")

# What each part of the raid is (short, shown on the team page).
RAID_FLOW = [
    ("🌐 Outside", "Make bombs, blow up mob shrines and open the Oni doors "
                   "for the Inside team. In the final phase, hold essences "
                   "and drop them in the pagoda urns on the Inside team's "
                   "callouts."),
    ("⚔️ Onis", "Inside pairs fight the six School Onis. Open all unlit "
                "doors first, then lit doors, before fighting the Onis. "
                "Try syncing your kills for the first two sets of fights."),
    ("🌸 Dryads", "Each Dryad needs two flowers/essences — see the Dryad "
                  "table. Flowers = HP Dryad for OS, Essence = Mana for VG."),
    ("🌱 Roots", "Two pairs (Spirit + Ele) work through a 10-turn plan, "
                 "swapping hanging effects between sigils and calling out "
                 "where each one lands. Ele goes 1 turn ahead."),
]

# ---- section intros (straight from the strategy tabs) --------------------
ONIS_INTRO = ("Open all unlit doors first, then lit doors, before fighting "
              "the Onis. Try syncing your kills for the first two sets of "
              "fights.")
ROOTS_INTRO = ("One set of scion cards are given to you — read the 📣 "
               "Callouts page to understand the callouts. **Ele should be 1 "
               "turn ahead.**")

# ---- hanging effects / callouts -----------------------------------------
EFFECT_SCHOOLS = [
    ("DoTs", "Fire"), ("Shields", "Ice"), ("Blades", "Storm"),
    ("HoTs", "Life"), ("Traps", "Myth"), ("Weakness", "Death"),
]

CALLOUT_HOW = (
    "Type your callout as soon as you click your spell. Your callout depends "
    "on the hanging effect that appears on your target. Call out the school "
    "linked to the effect, then the sigil slot it landed on.")

CALLOUT_EXAMPLES = [
    ("The World B on Ice (root)",
     "Clears DoTs to place DoTs on Ice Root. DoT = Fire, so call out the "
     "slot Ice Root is in: **Fire in Eye/Star**."),
    ("Storm King Art B on Life (root)",
     "Clears HoTs to place HoTs on yourself. HoT = Life, so call out the "
     "slot you are in: **Life in Key**."),
]

SWAP_RULES = (
    "Hanging effects only swap if **both sigils are in animation**. When you "
    "click your card, your sigil starts its swap animation. If the other "
    "sigil is also in animation, the hanging effect moves over and appears "
    "there next round. If the other sigil is in card select, the effect will "
    "not move — you will need to wait the following round.")

# ---- dryads --------------------------------------------------------------
DRYAD_KEY = ("Flowers = HP Dryad for OS  •  Essence = Mana for VG")

# (Dryad school, first flower/essence, second flower/essence)
DRYADS = [
    ("Fire", "Life", "Fire"),
    ("Ice", "Myth", "Ice"),
    ("Storm", "Death", "Storm"),
    ("Life", "Storm", "Life"),
    ("Myth", "Fire", "Myth"),
    ("Death", "Ice", "Death"),
]

# Maps live in assets/bvr/ (relative to assets/).
MAPS = {
    "1": ("bvr/floor1.png", "Elemental Plane (VG) — Floor 1"),
    "2": ("bvr/floor2.png", "Elemental Plane (VG) — Floor 2"),
}

# School → emoji / Oni name, shared by every Oni screen.
SCHOOL_EMOJI = {"Storm": "⚡", "Myth": "🟡", "Fire": "🔥", "Death": "💀",
                "Life": "🍃", "Ice": "❄️"}
ONI_NAMES = {"Storm": "Primal Oni", "Life": "Infernal Oni",
             "Fire": "Trickster Oni", "Myth": "Everwinter Oni",
             "Ice": "Doom Oni", "Death": "Turmoil Oni"}

# Short spellings used in the sheet's tables.
ABBREVIATIONS = (
    "**TC** treasure card • **IC** item card • **WC** willcast • "
    "**P1 / P2** first / second player of the pair as listed • "
    "**dp** Donate Power")
