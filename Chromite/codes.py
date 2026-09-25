"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import os

# Initialize ANSI support in Windows consoles.
os.system("")

CSI = "\033["

class ANSIElement(str):
    """
    Custom string for ANSI codes.
    """
    pass

def make_ansi(code: int) -> ANSIElement:
    """Make ANSI code."""
    return ANSIElement(f"{CSI}{code}m")

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