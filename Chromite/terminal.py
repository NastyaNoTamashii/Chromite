"""

Chromite/terminal.py
~~~~~~~~~~~~~~~~~~~~
Terminal Features.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['move_cursor', 'place', 'hide_cursor', 'show_cursor', 'save_cursor', 'restore_cursor', 'clear']

import os
from .codes import ANSIElement, CSI

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

def clear() -> None:
    """Clears the terminal screen."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except:
        print("\x1b[2J\x1b[3J\x1b[H", end="", flush=True)