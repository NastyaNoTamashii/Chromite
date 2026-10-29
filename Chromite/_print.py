"""

Chromite/_print.py
~~~~~~~~~~~~~~~~~~
Replacing the standard `builtins.print` with `Chromite.print`, which supports `compose`, `pos`, and more.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

import builtins
from .fmt import BaseCodes
from .io import Write

def print(
        *values,
        sep=" ", 
        end="\n",
        file=None,
        flush=False,
        compose=None,
        pos=None,
        align='left',
        width=None,
        markup=True
    ):
        """Drop-in replacement for the built-in print() with Chromite markup ($red$, :emoji:)."""
        text = (" " if sep is None else sep).join(map(str, values))
        out = Write(text, compose=compose, pos=pos, align=align, width=width, markup=markup).flush()
        reset = str(BaseCodes.RESET)
        if "\x1b[" in out and not out.endswith(reset):  # стиль из разметки не должен протекать дальше
            out += reset
        builtins.print(out, end=end, file=file, flush=flush)