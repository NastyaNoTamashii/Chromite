"""

Chromite/_errors.py
~~~~~~~~~~~~~~~~~~~
Exception classes of the library. Depends on nothing (floor 1).

Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['ChromiteError', 'InvalidComposeError', 'InvalidAlignError', 'UnknownLanguageError']

class ChromiteError(Exception):
    """
    Base class for all Chromite errors.

    :param message: What went wrong.
    :param hint: Optional advice how to fix it (shown by the pretty error view).
    """
    def __init__(self, message: str = "", *, hint: str | None = None):
        super().__init__(message)
        self.message = message
        self.hint = hint
        if hint:
            self.add_note(f"hint: {hint}")

class InvalidComposeError(ChromiteError, TypeError):
    """compose contains something that is not an ANSIElement."""

class InvalidAlignError(ChromiteError, ValueError):
    """align must be 'left', 'right' or 'center'."""

class UnknownLanguageError(ChromiteError, ValueError):
    """Syntax highlighting is not available for this language."""