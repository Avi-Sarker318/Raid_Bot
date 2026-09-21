"""Table rendering helpers for guide embeds.

Turns a raid's turn-table dicts into something Discord can display:
`table_fields` renders them as inline embed fields (mobile-friendly),
`grid` renders them as an aligned monospace code block.
"""


_ANSI = {"🟠": "\u001b[0;33m", "🟣": "\u001b[0;35m"}   # gold, magenta
_ANSI_RESET = "\u001b[0m"


def _colorize(cell: str) -> tuple[str, str]:
    """Turn 🟠/🟣 markers into ANSI-coloured text.

    '🟠Blade 🟣Pass' -> the words are coloured and the circles removed.
    Returns (rendered_cell, plain_cell); the plain form is what column
    widths are measured against, since ANSI codes take no screen space.
    """
    if not any(m in cell for m in _ANSI):
        return cell, cell
    out, plain = "", ""
    i = 0
    while i < len(cell):
        ch = cell[i]
        if ch in _ANSI:
            # colour the run of text that follows, up to the next marker
            j = i + 1
            while j < len(cell) and cell[j] not in _ANSI:
                j += 1
            word = cell[i + 1:j]
            out += _ANSI[ch] + word + _ANSI_RESET
            plain += word
            i = j
        else:
            out += ch
            plain += ch
            i += 1
    return out, plain


def _dwidth(s: str) -> int:
    """Display width of a string in a monospace font. Emoji and other wide
    glyphs take two character cells, so plain len() misaligns any table
    containing them."""
    w = 0
    for ch in s:
        o = ord(ch)
        if o < 0x2500:                       # ASCII / latin — single width
            w += 1
        elif 0xFE00 <= o <= 0xFE0F:          # variation selectors: no width
            continue
        elif (0x1F300 <= o <= 0x1FAFF or     # emoji blocks
              0x2600 <= o <= 0x27BF or       # misc symbols / dingbats
              0x1F000 <= o <= 0x1F2FF or
              0x2B00 <= o <= 0x2BFF):
            w += 2
        else:
            w += 1
    return w


def _dpad(s: str, width: int) -> str:
    """Left-justify to a display width (emoji-aware)."""
    return s + " " * max(0, width - _dwidth(s))


def _role_icon(role: str) -> str:
    """Small visual markers that make turn cards easier to scan."""
    name = role.lower()
    if "support" in name:
        return "🛡️"
    if "storm" in name:
        return "⚡"
    if "tank" in name:
        return "🧱"
    if "hitter" in name:
        return "💥"
    if "player" in name or name.startswith("p"):
        return "👤"
    return "🔹"


def table_fields(table: dict) -> list[tuple[str, str, bool]]:
    """Render a fight as full-width turn cards.

    Each round is one Discord field and every role appears in the table's
    declared order. This is much easier to follow during a live raid than
    several narrow inline fields, especially on mobile.
    """
    turn_label = table.get("turn", "Turn")
    cols = list(table["cols"])
    rows = table["rows"]

    out: list[tuple[str, str, bool]] = []
    if table.get("name"):
        out.append((f"📋 {table['name']}", "​", False))

    # Show the pulling/role order once before the turns.
    order = "  →  ".join(f"{_role_icon(col)} **{col}**" for col in cols)
    if order:
        out.append(("👥 Role order", order, False))

    for r in rows:
        if len(r) < len(cols) + 1:
            note_label = f"🎯 {turn_label} {r[0]}" if len(r) > 1 else "📌 Fight note"
            out.append((note_label, str(r[-1]), False))
            continue

        lines = []
        for i, col in enumerate(cols, start=1):
            val = "—" if r[i] is None else str(r[i]).strip()
            if not val:
                val = "—"
            lines.append(f"{_role_icon(col)} **{col}:** {val}")

        label = str(r[0]).strip()
        out.append((f"🎯 {turn_label} {label}", "\n".join(lines), False))
    return out


def grid(table: dict) -> str:
    """Clean monospace table in a code block. Columns are space-aligned with
    a simple dashed header rule. Mid-fight notes (rows with just one value)
    are pulled out and listed under the table as bullets so they never break
    the column alignment. Long cells are wrapped to keep the table narrow."""
    turn = table.get("turn", "Turn")
    cols = [turn] + list(table["cols"])
    rows = table["rows"]

    data_rows = [list(r) for r in rows if len(r) == len(cols)]
    notes = [r[-1] for r in rows if len(r) < len(cols)]

    # Cap each column so one very long cell can't stretch the whole table
    # off-screen. This is generous — only genuinely huge cells get moved to
    # a note beneath the table, so turn plans stay readable in the grid.
    MAXW = 32
    for r in data_rows:
        for i in range(1, len(r)):        # never trim the first column
            if _dwidth(_colorize(r[i])[1]) > MAXW:
                notes.append(f"{cols[0]} {r[0]} — {cols[i]}: "
                             f"{_colorize(r[i])[1]}")
                r[i] = "(see below)"

    # Pre-render each cell: coloured version for display, plain for widths.
    rendered = [[_colorize(c) for c in r] for r in data_rows]
    head = [(c, c) for c in cols]
    any_colour = any(r[i][0] != r[i][1]
                     for r in rendered for i in range(len(cols)))

    widths = [max(_dwidth(cols[i]),
                  *(_dwidth(r[i][1]) for r in rendered)) if rendered
              else _dwidth(cols[i])
              for i in range(len(cols))]

    def line(cells):
        # cells are (display, plain); pad using the PLAIN width so the
        # invisible colour codes don't throw the columns off
        parts = []
        for i, (disp, plain) in enumerate(cells):
            parts.append(disp + " " * max(0, widths[i] - _dwidth(plain)))
        return "  ".join(parts)

    sep = "  ".join("-" * w for w in widths)
    body = "\n".join([line(head), sep] + [line(r) for r in rendered])

    out = ""
    name = table.get("name")
    if name:
        out += f"**{name}**\n"
    # 'ansi' code block so the colours render; plain block when unneeded.
    out += f"```{'ansi' if any_colour else ''}\n{body}\n```"
    for n in notes:
        out += f"\n• {n}"
