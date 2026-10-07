"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['List']

from typing import List as PyList, Union, Optional, Tuple
from .codes import move_cursor, ANSIElement
from .formatting import BaseCodes
from .io import parse_markup

# Type Hint for styles: one element or list/tuple of elements
StyleType = Union[ANSIElement, PyList[ANSIElement], Tuple[ANSIElement, ...]]

PosType = Tuple[int, int]  # (x, y) or (col, row)

class List:
    __slots__ = ("items", "bullet", "ordered", "compose", "bullet_compose", "pos",)

    def __init__(
        self,
        items: PyList[str],
        *,
        bullet: str = "•",
        ordered: bool = False,
        compose: StyleType = None,
        bullet_compose: StyleType = None,
        pos: Optional[PosType] = None
    ):
        """
        :param items: A list of text strings or items to be rendered in the list.
        :param bullet: Symbol used as a bullet marker for unordered lists (e.g. "•", "-", "x").
        :param ordered: If True, renders a numbered list (1., 2., ...); if False, renders a bulleted list using 'bullet'.
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to the list item text.
        :param bullet_compose: ANSI style or sequence of styles applied specifically to the bullet/number markers.
        :param pos: Optional (x, y) coordinates for precise terminal cursor positioning.
        """
        self.items = items
        self.bullet = bullet
        self.ordered = ordered
        self.compose = compose
        self.bullet_compose = bullet_compose
        self.pos = pos

    def flush(self) -> str:
        lines = []
        for index, item in enumerate(self.items):
            # Specify the marker (number or bullet).
            prefix = f"{index + 1}." if self.ordered else self.bullet

            # Apply the style to the bullet if 'bullet_compose' is provided.
            if self.bullet_compose:
                if isinstance(self.bullet_compose, (list, tuple)):
                    b_style = "".join(str(s) for s in self.bullet_compose)
                else:
                    b_style = str(self.bullet_compose)
                prefix = f"{b_style}{prefix}{BaseCodes.RESET}"

            # Apply markup parsing and style to the text if 'compose' is provided.
            item_text = parse_markup(str(item))
            if self.compose:
                if isinstance(self.compose, (list, tuple)):
                    t_style = "".join(str(s) for s in self.compose)
                else:
                    t_style = str(self.compose)
                item_text = f"{t_style}{item_text}{BaseCodes.RESET}"

            lines.append(f"{prefix} {item_text}")

        res = "\n".join(lines)

        # Position support pos=(x, y).
        if self.pos is not None:
            x, y = self.pos
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            # When positioning a multi-line list, we offset each line or use an initial cursor move.
            res = f"{ansi_pos}" + res.replace("\n", f"\n{ansi_pos}")

        return res

    def display(self) -> None:
        print(self.flush())

    def __str__(self) -> str:
        return self.flush()

    # Classmethods.
    @classmethod
    def pointed(cls, items: PyList[str], **kwargs) -> "List":
        return cls(items, ordered=False, **kwargs)

    @classmethod
    def numbered(cls, items: PyList[str], **kwargs) -> "List":
        return cls(items, ordered=True, **kwargs)