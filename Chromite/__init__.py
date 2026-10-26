"""

Chromite/__init__.py
~~~~~~~~~~~~~~~~~~~~
A large library with functionality for working with the terminal and creating TUI applications.

Currently under development...

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__title__ = "Chromite"
__author__ = "NastyaNoTamashii"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present NastyaNoTamashii"
__version__ = "0.7.0"

from .io import (
    Write, Read, cInject
)

from .terminal import (
    clear, show_cursor, save_cursor,
    hide_cursor, move_cursor, restore_cursor
)

from .fmt import Color, Style, ColorBG, link
from .table import Table, TableStyle
from .list import List
from .powerline import Powerline, Segment, Cap
from .tree import Tree, TreeStyle, Branch
from .syntax import Syntax, make_editor
from ._print import print
from ._input import input

__all__ = [
    "Write", "Read", "cInject", # .io

    "clear", "show_cursor", "save_cursor", # .terminal
    "hide_cursor", "move_cursor", "restore_cursor",

    "Color", "Style", "ColorBG", "link", # .fmt
    "Table", "TableStyle", # .table
    "List", # .list
    "Powerline", "Segment", "Cap", # .powerline
    "Tree", "TreeStyle", "Branch", # .tree
    "Syntax", "make_editor" # .syntax
]