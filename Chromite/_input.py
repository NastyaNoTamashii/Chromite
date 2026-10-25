"""

Chromite/_input.py
~~~~~~~~~~~~~~~~~~
Replacing the standard `builtins.input` with `Chromite.input`, which supports `compose`, `pos`, and more.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

from .io import Read

def input(
        prompt="",
        *,
        compose=None,
        value_compose=None,
        pos=None,
        type="text"
    ) -> str:
        """Drop-in replacement for the built-in input() with Chromite markup in the prompt."""
        return Read(prompt, compose=compose, value_compose=value_compose, pos=pos, type=type).execute().text