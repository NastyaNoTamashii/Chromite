"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__title__ = "Chromite"
__author__ = "NastyaNoTamashii"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present NastyaNoTamashii"
__version__ = "0.6.7"

from .formatting import Color, Style, ColorBG
from .io import (
    Write, Read, clear, cInject
)

from .table import Table, TableStyle
from .list import List

__all__ = ["Write", "Read", "Color", "ColorBG", "Style", "Table", "TableStyle", "List", "clear", "cInject"]