"""

Chromite/list.py
~~~~~~~~~~~~~~~~
Creating useful lists.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['List']

from typing import List as PyList, Union, Optional, Tuple
from .terminal import place
from .codes import validate_compose, apply_compose
from ._base import Renderable
from ._markup import parse_markup
from ._types import StyleType, PosType

class List(Renderable):
    __slots__ = ("items", "bullet", "ordered", "compose", "bullet_compose", "pos", "markup",)

    def __init__(
        self,
        items: PyList[str],
        *,
        bullet: str = "•",
        ordered: bool = False,
        compose: StyleType = None,
        bullet_compose: StyleType = None,
        pos: Optional[PosType] = None,
        markup: bool = False
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
        self.markup = markup

        validate_compose(self.compose)

    def flush(self) -> str:
        """Returns the finished list as a single string: markers, item text with markup and styles applied, items separated by line breaks, and cursor positioning if pos is set."""
        lines = []
        for index, item in enumerate(self.items):

            prefix = f"{index + 1}." if self.ordered else self.bullet
            prefix = apply_compose(prefix, self.bullet_compose)

            item_text = item
            if self.markup is True:
                item_text = parse_markup(str(item))
            item_text = apply_compose(item_text, self.compose)

            lines.append(f"{prefix} {item_text}")

        return place("\n".join(lines), self.pos)

    # Classmethods.
    @classmethod
    def pointed(cls, items: PyList[str], **kwargs) -> "List":
        return cls(items, ordered=False, **kwargs)

    @classmethod
    def numbered(cls, items: PyList[str], **kwargs) -> "List":
        return cls(items, ordered=True, **kwargs)