"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__title__ = "Chromite"
__author__ = "NastyaNoTamashii"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present NastyaNoTamashii"
__version__ = "0.6.9"

from .fmt import Color, Style, ColorBG, link
from .io import (
    Write, Read, clear, cInject
)

from .table import Table, TableStyle
from .list import List
from .powerline import Powerline, Segment, Cap
from .tree import Tree, TreeStyle, Branch

__all__ = [
    "Write", "Read", "Color", "ColorBG", "link", "Style",
    "Table", "TableStyle", "List", "Powerline", "Segment", "Cap",
    "clear", "cInject", "Tree", "TreeStyle", "Branch"
]