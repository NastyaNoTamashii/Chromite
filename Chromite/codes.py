"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import os

# Initialize ANSI support in Windows consoles.
os.system("")

CSI       = "\x1b["
CSIX256   = "\x1b[38;5;" # "38;5;" — To activate the 256-color palette mode (8-bit).
CSIX256BG = "\x1b[48;5;" # "48;5;" — To activate the 256-color background palette mode (8-bit).
CSIRGB    = "\x1b[38;2;" # "48;5;" — To activate the True-color pallete mode (RGB).
CSIRGBBG  = "\x1b[48;2;" # "48;5;" — To activate the True-color background pallete mode (RGB).

class ANSIElement(str):
    """Custom string for ANSI codes."""
    pass

def make_ansi(code: int) -> ANSIElement:
    """Make ANSI code."""
    return ANSIElement(f"{CSI}{code}m")

def make_ansi_x256(code: int, *, bg: bool = None) -> ANSIElement:
    """Make x256 ANSI code (8-bit)."""
    if bg is True:
        return ANSIElement(f"{CSIX256BG}{code}m")
    return ANSIElement(f"{CSIX256}{code}m")

def make_ansi_rgb(r: int, g: int, b: int, *, bg: bool = None) -> ANSIElement:
    """Make RGB code."""
    if bg is True:
        return ANSIElement(f"{CSIRGBBG}{r};{g};{b}m")
    return ANSIElement(f"{CSIRGB}{r};{g};{b}m")

def move_cursor(x: int, y: int) -> ANSIElement:
    """Moves the cursor to position (x, y) / (col, row). Numbering starts at 1, 1."""
    return ANSIElement(f"{CSI}{y};{x}H")

def place(text: str, pos) -> str:
    """
    Puts 'text' at pos=(x, y), numbering from 0, 0.
    Every line of a multi-line text gets its own cursor move, so the x offset
    is kept after '\\n' and the lines do not overwrite each other.
    """
    if pos is None:
        return text
    x, y = pos
    return "\n".join(
        f"{move_cursor(max(1, x + 1), max(1, y + 1 + i))}{line}"
        for i, line in enumerate(text.split("\n"))
    )

def hide_cursor() -> ANSIElement:
    """Hides the cursor."""
    return ANSIElement(f"{CSI}?25l")

def show_cursor() -> ANSIElement:
    """Shows the cursor."""
    return ANSIElement(f"{CSI}?25h")

def save_cursor() -> ANSIElement:
    """Saves the current cursor position."""
    return ANSIElement(f"{CSI}s")

def restore_cursor() -> ANSIElement:
    """Restores the saved cursor position."""
    return ANSIElement(f"{CSI}u")