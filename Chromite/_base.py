"""

Chromite/_base.py
~~~~~~~~~~~~~~~~~
Initializing the library's basic functions.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['Renderable']

class Renderable:
    """Common interface: a subclass implements flush(); display(), str() and calling come for free."""
    __slots__ = ()

    def flush(self) -> str:
        """Returns the finished result as a string. Must be implemented by the subclass."""
        raise NotImplementedError

    def display(self) -> None:
        """Prints the finished result to the terminal right away, without a trailing line break."""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

    def __call__(self) -> None:
        return self.display()