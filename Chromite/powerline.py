"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import re
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement, compose_to_ansi
from .fmt import BaseCodes
from ._markup import parse_markup

__all__ = ['Powerline', 'Segment', 'Cap']

# Type Hint for styles: one element or list/tuple of elements
StyleType = Union[ANSIElement, List[ANSIElement], Tuple[ANSIElement, ...]]

def _bg_of(compose: StyleType) -> Optional[ANSIElement]:
    """
    Returns the background color of 'compose' (the last one, because that is the one
    the terminal actually shows), or None if there is no background.
    """
    if compose is None:
        return None
    items = compose if isinstance(compose, (list, tuple)) else [compose]
    return next((e for e in reversed(items) if getattr(e, "kind", None) == "bg"), None)

# Powerline Glyphs
class Cap:
    ARROW_RIGHT = "\ue0b0"
    ARROW_LEFT  = "\ue0b2"
    ROUND_RIGHT = "\ue0b4"
    ROUND_LEFT  = "\ue0b6"

class Segment:
    __slots__ = ("text", "compose", "cap_left", "cap_right",)

    def __init__(
        self,
        text: str,
        *,
        compose: StyleType = None,
        cap_left: Optional[str] = None,
        cap_right: Optional[str] = None,
    ):
        """
        Create a segment for powerline.

        >>> Segment(
        >>>    "\uf07b Some text",
        >>>    compose=[Color.Black, ColorBG.hex("#00d7ff")],
        >>>    cap_left=Cap.ROUND_LEFT
        >>> )

        :param text: Segment content ($markup$ and :emoji:).
        :param compose: Style or sequence of styles (Color, ColorBG, Style) applied to the one Segment.
        :param cap_left: A symbol-cap on the LEFT before the segment (Cap; Exemple: Cap.ROUND_LEFT).
        :param cap_right: A symbol-cap on the RIGHT after the segment (Cap; Exemple: Cap.ARROW_RIGHT).
        """
        self.text = text
        self.compose = compose
        self.cap_left = cap_left
        self.cap_right = cap_right

class Powerline:
    __slots__ = ("segments",)

    def __init__(self, segments: Optional[List[Segment]] = None):
        """
        Create a powerline from Segment classes.

        >>> builder = Powerline()
        >>> builder.add(Chromite.Segment(
        >>>    "\uf07b Some text",
        >>>    compose=[Color.Black, ColorBG.hex("#00d7ff")],
        >>>    cap_left=Cap.ROUND_LEFT
        >>> ))
        >>> builder.display() 

        :param segments: a Segment class
        """

        self.segments: List[Segment] = segments or []

    def add(self, segment: Segment) -> Powerline:
        self.segments.append(segment)
        return self

    def flush(self) -> str:
        if not self.segments:
            return ""

        result = []
        for i, seg in enumerate(self.segments):
            bg = _bg_of(seg.compose)
            cap_fg = (bg.fg_twin or "") if bg else ""

            next_seg = self.segments[i + 1] if i + 1 < len(self.segments) else None
            next_bg = _bg_of(next_seg.compose) if next_seg else None

            # Left cap.
            if seg.cap_left:
                result.append(f"{BaseCodes.RESET}{cap_fg}{seg.cap_left}")

            # The main body of the segment.
            result.append(f"{compose_to_ansi((seg.compose))} {parse_markup(seg.text)} {BaseCodes.RESET}")

            if seg.cap_right:
                if next_bg:
                    result.append(f"{next_bg}{cap_fg}{seg.cap_right}")
                else:
                    result.append(f"{cap_fg}{seg.cap_right}{BaseCodes.RESET}")

        result.append(f"{BaseCodes.RESET} ")
        return "".join(result)

    def display(self) -> None:
        """Immediately outputs "powerline" to the terminal."""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

    def __call__(self) -> None:
        return self.display()