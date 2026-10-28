"""

Chromite/_text.py
~~~~~~~~~~~~~~~~~
Functions to work with text.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

import re
import unicodedata
from .fmt import BaseCodes

# Character width
# ANSI codes (SGR styles/colors and OSC references) take up 0 columns
_ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")
_TOKEN = re.compile(_ANSI.pattern + "|.", re.S)  # ANSI code (entire code or a single character)
_ZWJ, _VS16 = "\u200d", "\ufe0f"  # emoji joiner / emoji presentation selector

def clusters(s):
    """Splits a string into [fragment, width] pieces. This is the single source of
    truth for width: _w measures with it and _put draws with it, so they never disagree.

    - ANSI codes: width 0.
    - Wide characters (CJK, most emoji): width 2.
    - Combining marks, invisible format characters (zero-width space, ZWJ, variation
      selectors) and skin tone modifiers are glued to the previous character.
    - Emoji sequences (ZWJ, VS16, skin tone) are one piece. VS16 widens a narrow
      character to 2 columns, as modern terminals do."""
    out, last, join = [], None, False  # last: last visible piece; join: previous char was ZWJ
    for tok in _TOKEN.findall(s):
        if len(tok) > 1:  # ANSI code
            out.append([tok, 0])
            continue
        glue = (join or unicodedata.category(tok) in ("Mn", "Me", "Cf")
                or "\U0001f3fb" <= tok <= "\U0001f3ff")
        if glue and last:
            last[0] += tok
            if tok == _VS16 and last[1] == 1:
                last[1] = 2
        elif glue:  # invisible character with nothing to attach to
            out.append([tok, 0])
        else:
            last = [tok, 2 if unicodedata.east_asian_width(tok) in "WF" else 1]
            out.append(last)
        join = tok == _ZWJ and last is not None
    return out

def w(s):
    """Number of terminal columns the string occupies when printed."""
    return sum(w for _, w in clusters(s))

def cut(line: str, width: int) -> str:
    out, used = [], 0
    for frag, w in clusters(line):    # ANSI-коды имеют ширину 0
        if used + w > width:
            break
        out.append(frag)
        used += w
    return ''.join(out) + BaseCodes.RESET

def align(text, width, align):
    gap = width - w(text)
    if align == "right":
        return " " * gap + text
    if align == "center":
        return " " * (gap // 2) + text + " " * (gap - gap // 2)
    return text + " " * gap