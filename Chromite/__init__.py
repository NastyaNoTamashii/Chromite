"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__title__ = "Chromite"
__author__ = "NastyaNoTamashii"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present NastyaNoTamashii"
__version__ = "0.6.1"

from .formatting import color as _color, color_bg as _color_bg, style as _style
from .io import (
    Write, Catch, clear, cInject
)

from .table import Table
from .lists import List

Color = _color
ColorBG = _color_bg
Style = _style

__all__ = ["Write", "Catch", "Color", "ColorBG", "Style", "Table", "List", "clear", "cInject"]