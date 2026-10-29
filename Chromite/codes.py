"""

Chromite/codes.py
~~~~~~~~~~~~~~~~~

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

import os
from ._errors import InvalidComposeError

# Initialize ANSI support in Windows consoles.
os.system("")

CSI       = "\x1b["
CSIX256   = "\x1b[38;5;" # "38;5;" — To activate the 256-color palette mode (8-bit).
CSIX256BG = "\x1b[48;5;" # "48;5;" — To activate the 256-color background palette mode (8-bit).
CSIRGB    = "\x1b[38;2;" # "38;5;" — To activate the True-color pallete mode (RGB).
CSIRGBBG  = "\x1b[48;2;" # "48;5;" — To activate the True-color background pallete mode (RGB).

class ANSIElement(str):
    """Custom string for ANSI codes."""
    kind = "style" # "fg" | "bg" | "style"
    fg_twin = None # For bg: the same color, but as the text color.
    def __new__(cls, value, kind="style", fg_twin=None):
        obj = super().__new__(cls, value)
        obj.kind, obj.fg_twin = kind, fg_twin
        return obj

def make_ansi(code: int) -> ANSIElement:
    """Make ANSI code."""
    if 40 <= code <= 47 or 100 <= code <= 107:
        return ANSIElement(f"{CSI}{code}m", "bg", ANSIElement(f"{CSI}{code - 10}m", "fg"))
    if 30 <= code <= 37 or 90 <= code <= 97:
        return ANSIElement(f"{CSI}{code}m", "fg")
    return ANSIElement(f"{CSI}{code}m")

RESET = make_ansi(0)

def make_ansi_x256(code: int, *, bg: bool = None) -> ANSIElement:
    """Make x256 ANSI code (8-bit)."""
    fg = ANSIElement(f"{CSIX256}{code}m", "fg")
    return ANSIElement(f"{CSIX256BG}{code}m", "bg", fg) if bg else fg

def make_ansi_rgb(r: int, g: int, b: int, *, bg: bool = None) -> ANSIElement:
    """Make RGB code."""
    fg = ANSIElement(f"{CSIRGB}{r};{g};{b}m", "fg")
    return ANSIElement(f"{CSIRGBBG}{r};{g};{b}m", "bg", fg) if bg else fg

def compose_to_ansi(compose) -> str:
    """ANSI sequence for 'compose': one element, a list/tuple of elements or None (-> empty string)."""
    if not compose:
        return ""
    if isinstance(compose, (list, tuple)):
        return "".join(str(s) for s in compose)
    return str(compose)

def apply_compose(content, compose) -> str:
    if not compose:
        return content
    if isinstance(compose, (ANSIElement, str)):
        return f"{compose}{content}{RESET}"
    if isinstance(compose, (list, tuple)):
        ansi_seq = "".join(str(c) for c in compose)
        return f"{ansi_seq}{content}{RESET}"
    return content

def validate_compose(compose) -> None:
    if (
        compose is None
        or isinstance(compose, ANSIElement)
        or (isinstance(compose, (list, tuple)) and all(isinstance(s, ANSIElement) for s in compose))
    ):
        return

    raise InvalidComposeError(f"compose must contain ANSIElement, got {type(compose).__name__}",
                              hint="use Color.*, ColorBG.* or Style.*")