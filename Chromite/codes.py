"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import os

# Initialize ANSI support in Windows consoles.
os.system("")

CSI       = "\033["
CSIX256   = "\033[38;5;" # "38;5;" — To activate the 256-color palette mode (8-bit).
CSIX256BG = "\033[48;5;" # "48;5;" — To activate the 256-color palette mode (8-bit).

class ANSIElement(str):
    """
    Custom string for ANSI codes.
    """
    pass

def make_ansi(code: int) -> ANSIElement:
    """Make ANSI code."""
    return ANSIElement(f"{CSI}{code}m")

def make_ansi_x256(code: int, *, bg: bool = None) -> ANSIElement:
    """Make x256 ANSI code (8-bit)."""
    if bg is True:
        return ANSIElement(f"{CSIX256BG}{code}m")
    return ANSIElement(f"{CSIX256}{code}m")

def move_cursor(x: int, y: int) -> ANSIElement:
    """Moves the cursor to position (x, y) / (col, row). Numbering starts at 1, 1."""
    return ANSIElement(f"{CSI}{y};{x}H")

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