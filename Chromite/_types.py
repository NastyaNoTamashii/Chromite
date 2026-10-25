"""

Chromite/_types.py
~~~~~~~~~~~~~~~~~~
Initializing Library Variable Types. 

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

from typing import Tuple
from .codes import ANSIElement

# One element or a list/tuple of elements: Color.Red, [Color.Red, Style.Bold]
type StyleType = ANSIElement | list[ANSIElement] | tuple[ANSIElement, ...]

type PosType = Tuple[int, int]  # (x, y) or (col, row)