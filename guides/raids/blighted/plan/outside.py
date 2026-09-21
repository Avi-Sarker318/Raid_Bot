"""Blighted Veil Raid — Outside team (North / East / South / West).

Import from `plan` (the package re-exports everything), not from here.

Source: the Outside team slide deck.
"""

WISPS = [
    "Scattered along pathways to mob spawners.",
    "Grabbing one costs **3% of your max HP** — running an HP build does "
    "not matter.",
    "They absorb mobs and convert them into **essences**.",
    "Turn essences in at the **essence forge** to craft school spawn bombs "
    "(used to blow up mob spawners).",
    "Or deposit them into **essence urns** to send a mob to the Inside "
    "team (gives them mana wisps if needed).",
    "In the **final phase**, turn essences in at the center pagoda tower to "
    "shift hanging effects for the raid boss fight.",
]

SHRINES = [
    "Scattered across the map, each tied to a specific school.",
    "They continuously spawn mobs at regular intervals.",
    "Destroy one by hitting it with a specific school's mana bomb. "
    "**Don't stand directly in front** — stand to the side or behind.",
    "Destroying a shrine drops a **statue**. Place it on a torii gate to "
    "let a specific mob through the gates.",
]

# (door you want to open, bomb to grab, spawner it blows up)
BOMB_CHAIN = [
    ("Life", "Storm", "Life"),
    ("Fire", "Life", "Fire"),
    ("Myth", "Fire", "Myth"),
    ("Ice", "Myth", "Ice"),
    ("Death", "Ice", "Death"),
    ("Storm", "Death", "Storm"),
]

# (Oni door, mob school that opens it)
TORII_GATES = [
    ("Primal Oni", "Storm"), ("Infernal Oni", "Life"),
    ("Trickster Oni", "Fire"), ("Everwinter Oni", "Myth"),
    ("Doom Oni", "Ice"), ("Turmoil Oni", "Death"),
]
TORII_HOW = ("Anyone puts a statue down on the red wall to let the matching "
             "mob in.")

BUTTONS = [
    "Once the **last wave of Onis** is cleared, touchstone-like buttons "
    "appear near the gates.",
    "Press **X** on all of them quickly — together with your allies — to "
    "summon Stable or Potent Binding Wisps. They reset roughly every minute.",
    "**Stable** wisps absorb 3 mobs, **Potent** ones absorb 5. Both let you "
    "absorb multiple enemies during the final phase without taking extra "
    "health loss. The wisps spawn around the central pagoda tower.",
    "**Potent:** click all elemental or all spiritual tokens, whichever "
    "there are more of. Example: double Storm, but then it's Myth / Death / "
    "Life (and vice versa).",
]

# essence → what it swaps at the pagoda urns
SWAPS = [
    ("Storm", "Blades"), ("Life", "HoTs"), ("Fire", "DoTs"),
    ("Myth", "Traps"), ("Ice", "Shields"), ("Death", "Weaknesses"),
]

# Which two Oni tablets are lit → what to do (same for all four players).
DOOR_INTRO = ("Check which two Oni tablets are lit, then re-blow the "
              "spawners you don't need and let each needed mob through a "
              "**green** torii gate once (place the shrine statue on the "
              "gate to turn it green).")
DOOR_LOGIC = [
    {"lit": ("Storm", "Myth"), "reblow": ("Fire", "Death"),
     "skip": ("Death", "Fire"),
     "mobs": [("Ice", "Doom"), ("Life", "Infernal"),
              ("Myth", "Everwinter"), ("Storm", "Primal")]},
    {"lit": ("Ice", "Life"), "reblow": ("Myth", "Storm"),
     "skip": ("Myth", "Storm"),
     "mobs": [("Life", "Infernal"), ("Fire", "Trickster"),
              ("Ice", "Doom"), ("Death", "Turmoil")]},
    {"lit": ("Fire", "Death"), "reblow": ("Ice", "Life"),
     "skip": ("Ice", "Life"),
     "mobs": [("Storm", "Primal"), ("Fire", "Trickster"),
              ("Myth", "Everwinter"), ("Death", "Turmoil")]},
]

WRONG_ESSENCE = ("Grabbed the wrong essence? Ask teammates if they need it. "
                 "If not, deposit it in the **Essence Urns** by the central "
                 "Pagoda Tower.")
MOB_REASON = ("*Letting a mob spawn first is in case we need it for the Oni "
              "spawning.*")

PLAYERS = {
    "North": {
        "summary": "Storm Bomb → Life Spawner, then Life Bomb → Fire "
                   "Spawner",
        "opening": [
            "Make a **Storm Bomb** → blow up the **Life Spawner**. Place "
            "your essence in the **East** Essence Forge to make the bomb, "
            "then grab it and blow up the spawner.",
            "Grab **1 Life Essence** and let **1 mob spawn** before blowing "
            "up the spawner.",
            "Grab the **Shrine Statue** after blowing up the spawner.",
            "Place the Life Essence in the **East** Essence Forge to make a "
            "**Life Bomb** → blow up the **Fire Spawner**. Grab **1 Fire "
            "Essence** and let **1 mob spawn** first.",
            "Make a **Fire Bomb** and leave it in the **East** Essence Forge.",
        ],
        "after": "Go back to North, defend, and let in the **Storm** mob if "
                 "needed.",
        "final": [("Storm Essence", "Storm in Key"),
                  ("Fire Essence", "Fire in Ice root slot")],
    },
    "East": {
        "summary": "Fire Bomb → Myth Spawner",
        "opening": [
            "Make a **Fire Bomb** → blow up the **Myth Spawner**. Place "
            "your essence in the **South** Essence Forge to make the bomb, "
            "then grab it and blow up the spawner.",
            "Grab **1 Myth Essence** and let **1 mob spawn** before blowing "
            "up the spawner.",
            "Grab the **Shrine Statue** after blowing up the spawner.",
            "Make a **Myth Bomb** and leave it in the **South** Essence "
            "Forge.",
        ],
        "after": "Go back to East, defend, and let in **Life / Fire / Myth** "
                 "mobs if needed.",
        "final": [("Ice Essence", "Ice in dagger")],
    },
    "South": {
        "summary": "Myth Bomb → Ice Spawner, then Ice Bomb → Death Spawner",
        "opening": [
            "Make a **Myth Bomb** → blow up the **Ice Spawner**. Place your "
            "essence in the **West** Essence Forge to make the bomb, then "
            "grab it and blow up the spawner.",
            "Grab **1 Ice Essence** and let **1 mob spawn** before blowing "
            "up the spawner.",
            "Grab the **Shrine Statue** after blowing up the spawner.",
            "Place the Ice Essence in the **West** Essence Forge to make an "
            "**Ice Bomb** → blow up the **Death Spawner**. Grab **1 Death "
            "Essence** and let **1 mob spawn** first.",
            "Make a **Death Bomb** and leave it in the **West** Essence "
            "Forge.",
        ],
        "after": "Go back to South, defend, and let in the **Myth** mob if "
                 "needed.",
        "final": [("Life Essence", "Life in Key"),
                  ("Myth Essence", "Myth in Sun")],
        "final_note": "Time to lock in and be **QUICK** — these will most "
                      "likely be back to back in quick succession!",
    },
    "West": {
        "summary": "Death Bomb → Storm Spawner",
        "opening": [
            "Make a **Death Bomb** → blow up the **Storm Spawner**. Place "
            "your essence in the **North** Essence Forge to make the bomb, "
            "then grab it and blow up the spawner.",
            "Grab **1 Storm Essence** and let **1 mob spawn** before blowing "
            "up the spawner.",
            "Grab the **Shrine Statue** after blowing up the spawner.",
            "Make a **Storm Bomb** and leave it in the **North** Essence "
            "Forge.",
        ],
        "after": "Go back to West, defend, and let in **Ice / Death / "
                 "Storm** mobs if needed.",
        "final": [("Death Essence", "Death in Life root slot")],
    },
}

FINAL_HOW = ("Grab the essence **immediately** and defend the pagoda from "
             "mobs. Hold it until you see the Inside team call it, then "
             "deposit it in that specific urn in the center of the tower "
             "and go back to defending.")
