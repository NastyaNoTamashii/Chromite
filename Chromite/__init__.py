"""
    Copyright (C) 2026 NastyaNoTamashii.
"""

__title__ = "Chromite"
__author__ = "NastyaNoTamashii"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present NastyaNoTamashii"
__version__ = "0.4"

from .formatting import color, color_bg, style
from .io import (
    Write, Catch, clear, sjoin
)

from .table import Table

Color = color
ColorBG = color_bg
Style = style

__all__ = ["Write", "Catch", "Color", "ColorBG", "Style", "Table", "clear", "sjoin"]