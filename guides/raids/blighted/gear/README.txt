Blighted Veil Raid gear guides — one module per role/group.

Each module exposes GEAR = {
    "order": 1,                 # position in the /guide gear picker
    "title": "🔵 -ice Gear",
    "intro": "...",
    "builds": {
        "ice": {"label": "Ice", "link": <WizBuilder url or None>,
                "slots": [[slot, item, jewels(, note)], ...],
                "min_stats": "High HP • 193 Ice DMG • ..."},
        ...
    },
}

loader.py picks every module up automatically — drop in a new file and it
shows up under 📐 Gear in the Blighted Veil guide.
