"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import re
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement
from .fmt import BaseCodes
from ._markup import parse_markup

__all__ = ['Powerline', 'Segment', 'Segment']

# Type Hint for styles: one element or list/tuple of elements
StyleType = Union[ANSIElement, List[ANSIElement], Tuple[ANSIElement, ...]]

def _extract_fg_bg(compose: StyleType) -> Tuple[str, str]:
    """Extracts and separates the ANSI sequences for text color and background color."""
    if compose is None:
        return "", ""
    
    if isinstance(compose, (list, tuple)):
        combined = "".join(str(s) for s in compose)
    else:
        combined = str(compose)

    bg_codes = "".join(re.findall(r"\033\[(?:48;[0-9;]+|4[0-7])m", combined))
    fg_codes = "".join(re.findall(r"\033\[(?:38;[0-9;]+|3[0-7]|1|2|3|4|7|9[0-7]|10[0-7])m", combined))
    
    return fg_codes, bg_codes

# Powerline Glyphs
class Caps:
    ARROW_RIGHT = ""
    ARROW_LEFT  = ""
    ROUND_RIGHT = ""
    ROUND_LEFT  = ""

class Segment:
    __slots__ = ("text", "compose", "cap_left", "cap_right",)

    def __init__(
        self,
        text: str,
        *,
        compose: StyleType = None,
        cap_left: Optional[str] = None,
        cap_right: Optional[str] = Caps.ARROW_RIGHT,
    ):
        """
        :param text: Segment content ($markup$ and :emoji:).
        :param compose: Style or sequence of styles (Color, ColorBG, Style) applied to the one Segment.
        :param cap_left: A symbol-cap on the LEFT before the segment (Caps; Exemple: Caps.ROUND_LEFT).
        :param cap_right: A symbol-cap on the RIGHT after the segment (Caps; Exemple: Caps.ARROW_RIGHT).
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
        >>> builder.add(Segment(
        >>>    f" ...", 
        >>>    compose=[Color.Black, ColorBG.hex("#00d7ff")],
        >>>    cap_left=Caps.ROUND_LEFT
        >>> ))
        >>> builder.display() 

        :param segments: a Segment class
        """

        self.segments: List[Segment] = segments or []

    def add(self, segment: Segment) -> "Powerline":
        self.segments.append(segment)
        return self

    def flush(self) -> str:
        if not self.segments:
            return ""

        result = []
        for i, seg in enumerate(self.segments):
            _, bg_code = _extract_fg_bg(seg.compose)
            
            # Text styling.
            if isinstance(seg.compose, (list, tuple)):
                style_seq = "".join(str(s) for s in seg.compose)
            elif seg.compose:
                style_seq = str(seg.compose)
            else:
                style_seq = ""

            content = parse_markup(seg.text)

            # Left cap.
            if seg.cap_left:
                if bg_code:
                    cap_fg = bg_code.replace("\033[4", "\033[3")
                    result.append(f"{BaseCodes.RESET}{cap_fg}{seg.cap_left}")
                else:
                    result.append(f"{BaseCodes.RESET}{seg.cap_left}")

            # The main body of the segment.
            result.append(f"{style_seq} {content} ")

            # Right cap and transitions between segments.
            next_seg = self.segments[i + 1] if i + 1 < len(self.segments) else None

            if seg.cap_right:
                _, next_bg_code = _extract_fg_bg(next_seg.compose) if next_seg else ("", "")

                if next_seg and next_bg_code:
                    # Transition to the next background:
                    # Arrow color = current background; background under the arrow = next background
                    sep_fg = bg_code.replace("\033[4", "\033[3") if bg_code else ""
                    result.append(f"{next_bg_code}{sep_fg}{seg.cap_right}")
                elif bg_code:
                    # The last segment in the chain with the background is the background reset.
                    sep_fg = bg_code.replace("\033[4", "\033[3")
                    result.append(f"{BaseCodes.RESET}{sep_fg}{seg.cap_right}{BaseCodes.RESET}")
                else:
                    result.append(f"{BaseCodes.RESET}{seg.cap_right}")

        result.append(f"{BaseCodes.RESET} ")
        return "".join(result)

    def display(self) -> None:
        """Immediately outputs "powerline" to the terminal."""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

    def __call__(self) -> None:
        return self.display()