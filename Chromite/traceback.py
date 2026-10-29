"""

Chromite/traceback.py
~~~~~~~~~~~~~~~~~~~~~
Pretty errors: DoError (a block that can be shown), show_error(), install() and catch().

Copyright (C) 2026 NastyaNoTamashii.

"""

from __future__ import annotations

__all__ = ['DoError', 'show_error', 'install', 'uninstall', 'catch']

import sys
import linecache
import threading
import traceback as _tb          # the standard one (absolute import)
from types import TracebackType

from ._base import Renderable
from ._errors import ChromiteError
from .fmt import Color, Style
from .syntax import Syntax

_RESET = str(Style.RESET)


class DoError(Renderable):
    __slots__ = ("title", "message", "hint", "file", "line", "func", "frames", "context")

    def __init__(
        self,
        title: str,
        message: str = "",
        *,
        hint: str | None = None,
        file: str | None = None,
        line: int | None = None,
        func: str | None = None,
        frames: list[tuple[str, int, str]] | None = None,
        context: int = 2,
    ):
        """
        A formatted error block.

        :param title: Error type name, e.g. "ValueError".
        :param message: What happened.
        :param hint: How to fix it (optional).
        :param file: File where it happened (with `line` shows a code snippet).
        :param line: Line number (1-based).
        :param func: Function name.
        :param frames: Earlier calls [(file, line, func), ...] shown dimmed.
        :param context: How many lines of code to show before/after the error line.
        """
        self.title, self.message, self.hint = title, message, hint
        self.file, self.line, self.func = file, line, func
        self.frames = frames or []
        self.context = context

    @classmethod
    def from_exception(cls, exc: BaseException, tb: TracebackType | None = None) -> "DoError":
        tb = tb if tb is not None else exc.__traceback__
        frames = [(f.filename, f.lineno or 0, f.name) for f in _tb.extract_tb(tb)
                  if f.filename != __file__]   # hide our own wrapper frames
        file, line, func = frames.pop() if frames else (None, None, None)
        message = getattr(exc, "message", None) if isinstance(exc, ChromiteError) else None
        return cls(
            type(exc).__name__,
            message if message is not None else str(exc),
            hint=getattr(exc, "hint", None),
            file=file, line=line, func=func, frames=frames,
        )

    def _snippet(self) -> list[str]:
        start = max(1, self.line - self.context)
        out = []
        for n in range(start, self.line + self.context + 1):
            src = linecache.getline(self.file, n).rstrip("\n")
            if not src and n > self.line:
                break
            code = Syntax.python(src) if src else ""
            if n == self.line:
                out.append(f"{Color.Red}❯{_RESET} {Color.Red}{n:>4}{_RESET} │ {code}")
            else:
                out.append(f"  {Style.Dim}{n:>4}{_RESET} │ {code}")
        return out

    def flush(self) -> str:
        red, dim, bold = Color.Red, Style.Dim, Style.Bold
        lines = [f"{red}{bold}✖ {self.title}{_RESET}" + (f": {self.message}" if self.message else "")]

        if self.file and self.line:
            where = f"{self.file}:{self.line}" + (f" in {self.func}" if self.func else "")
            lines.append(f"{dim}  at {where}{_RESET}")
            lines.append("")
            lines += self._snippet()

        if self.frames:
            lines.append("")
            lines.append(f"{dim}  called from:{_RESET}")
            for f, ln, fn in reversed(self.frames):
                lines.append(f"{dim}    {f}:{ln} in {fn}{_RESET}")

        if self.hint:
            lines.append("")
            lines.append(f"{Color.Yellow}  ➜ {self.hint}{_RESET}")

        return "\n".join(lines) + "\n"

    def display(self) -> None:
        print(self.flush(), end="", file=sys.stderr, flush=True)


def show_error(exc: BaseException) -> None:
    """Prints an exception as a pretty block (to stderr)."""
    DoError.from_exception(exc).display()


# ---- the interceptor ----------------------------------------------------------

def _hook(exc_type, exc, tb):
    try:
        DoError.from_exception(exc, tb).display()
    except Exception:
        # If drawing itself failed, do not lose the original error.
        sys.__excepthook__(exc_type, exc, tb)

def _thread_hook(args):
    if args.exc_type is SystemExit:
        return
    _hook(args.exc_type, args.exc_value, args.exc_traceback)

def install() -> None:
    """Every uncaught error (main thread and other threads) will be drawn by Chromite."""
    sys.excepthook = _hook
    threading.excepthook = _thread_hook

def uninstall() -> None:
    """Returns the standard error output."""
    sys.excepthook = sys.__excepthook__
    threading.excepthook = threading.__excepthook__

class catch:
    """
    Context manager AND decorator: catches the error, draws it and goes on (or exits).

    >>> with catch():
    >>>     risky()

    >>> @catch(exit_code=1)
    >>> def main(): ...
    """
    def __init__(self, *, exit_code: int | None = None, reraise: bool = False):
        self.exit_code, self.reraise = exit_code, reraise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None or isinstance(exc, (KeyboardInterrupt, SystemExit)):
            return False
        DoError.from_exception(exc, tb).display()
        if self.reraise:
            return False
        if self.exit_code is not None:
            sys.exit(self.exit_code)
        return True

    def __call__(self, func):
        def wrapper(*a, **kw):
            with self:
                return func(*a, **kw)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper