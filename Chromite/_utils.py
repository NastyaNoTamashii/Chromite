"""

Chromite/_utils.py
~~~~~~~~~~~~~~~~~~
Internal Utilities for Chromite.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['classproperty']

class classproperty:
    """Like @property, but works on the class itself."""
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)