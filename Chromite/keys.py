"""

Chromite/keys.py
~~~~~~~~~~~~~~~~
Reading key presses and key combinations: read_key, wait_key, confirm, pause, Hotkeys.

Key names are plain strings: "a", "y", "enter", "backspace", "tab", "escape", "up", "down",
"left", "right", "home", "end", "delete", "insert", "pageup", "pagedown", "f1".."f12",
"ctrl-s", "alt-x", "shift-up", "ctrl-alt-left" ...

Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['read_key', 'iter_keys', 'wait_key', 'confirm', 'pause', 'Hotkeys', 'STOP']

import os
import sys
import time
from contextlib import contextmanager
from typing import Callable, Iterator, Optional

from ._markup import parse_markup

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import select
    import termios
    import tty
    WINDOWS = False

# How long to wait after ESC to understand "Escape pressed alone" vs "start of arrow sequence".
_ESC_WAIT = 0.05

_SIMPLE = {"\r": "enter", "\n": "enter", "\t": "tab", "\x7f": "backspace", "\x08": "backspace", "\x00": "ctrl-space"}
_MODS = {2: "shift", 3: "alt", 4: "alt-shift", 5: "ctrl", 6: "ctrl-shift", 7: "ctrl-alt", 8: "ctrl-alt-shift"}
_LETTERS = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end",
            "P": "f1", "Q": "f2", "R": "f3", "S": "f4"}
_TILDE = {1: "home", 2: "insert", 3: "delete", 4: "end", 5: "pageup", 6: "pagedown", 7: "home", 8: "end",
          11: "f1", 12: "f2", 13: "f3", 14: "f4", 15: "f5", 17: "f6", 18: "f7", 19: "f8",
          20: "f9", 21: "f10", 23: "f11", 24: "f12"}
# Windows: the code after the prefix \x00 / \xe0.
_WIN = {"H": "up", "P": "down", "M": "right", "K": "left", "G": "home", "O": "end", "S": "delete",
        "R": "insert", "I": "pageup", "Q": "pagedown", "\x85": "f11", "\x86": "f12",
        **{chr(59 + i): f"f{i + 1}" for i in range(10)}}   # ';'..'D' = F1..F10

def _name(ch: str) -> str:
    """The name of a single character: control codes become ctrl-<letter>."""
    if ch in _SIMPLE:
        return _SIMPLE[ch]
    if "\x01" <= ch <= "\x1a":
        return "ctrl-" + chr(ord(ch) + 96)
    return ch

# Unix

def _unix_char(fd: int, timeout: Optional[float]) -> Optional[str]:
    """One character (UTF-8 aware) or None on timeout. Works on the raw fd, so select() is reliable."""
    if timeout is not None and not select.select([fd], [], [], timeout)[0]:
        return None
    b = os.read(fd, 1)
    if not b:
        raise EOFError
    first = b[0]
    need = 1 if first < 0x80 else 2 if first >> 5 == 0b110 else 3 if first >> 4 == 0b1110 else 4 if first >> 3 == 0b11110 else 1
    while len(b) < need:
        b += os.read(fd, 1)
    return b.decode("utf-8", "replace")

def _unix_key(fd: int, timeout: Optional[float]) -> Optional[str]:
    ch = _unix_char(fd, timeout)
    if ch is None:
        return None
    if ch != "\x1b":
        return _name(ch)
    nxt = _unix_char(fd, _ESC_WAIT)
    if nxt is None:
        return "escape"
    if nxt not in ("[", "O"):
        return "alt-" + _name(nxt).lower() if len(nxt) == 1 else "escape"
    seq = ""
    while True:                                    # parameters and the final byte
        c = _unix_char(fd, _ESC_WAIT)
        if c is None:
            return "unknown"
        seq += c
        if "@" <= c <= "~":
            break
    final, params = seq[-1], seq[:-1].split(";")
    mod = ""
    if len(params) > 1 and params[1].isdigit():
        mod = _MODS.get(int(params[1]), "") + "-"
    if final == "~" and params[0].isdigit():
        base = _TILDE.get(int(params[0]))
    else:
        base = _LETTERS.get(final)
    return f"{mod}{base}" if base else "unknown"

# Windows

def _windows_key(timeout: Optional[float]) -> Optional[str]:
    if timeout is not None:
        end = time.monotonic() + timeout
        while not msvcrt.kbhit():
            if time.monotonic() >= end:
                return None
            time.sleep(0.01)
    ch = msvcrt.getwch()
    # \x00 / \xe0 is the prefix of arrows/F-keys, but "à" is also "\xe0":
    # a real prefix is always followed by a second code that is already in the buffer.
    if ch in ("\x00", "\xe0") and msvcrt.kbhit():
        return _WIN.get(msvcrt.getwch(), "unknown")
    return _name(ch)

# ----

_depth = 0
_saved = None

@contextmanager
def _raw_mode():
    """'One key at a time, no echo' mode. Can be nested; the old mode is restored by the outermost."""
    global _depth, _saved
    if WINDOWS or not sys.stdin.isatty():
        yield
        return
    fd = sys.stdin.fileno()
    if _depth == 0:
        _saved = termios.tcgetattr(fd)
        tty.setcbreak(fd, termios.TCSADRAIN)
        # Ctrl+S / Ctrl+Q are flow control (XOFF/XON) by default and would freeze the output
        # instead of reaching us; Ctrl+V is "literal next". Switch both off.
        attrs = termios.tcgetattr(fd)
        attrs[0] &= ~termios.IXON
        attrs[3] &= ~termios.IEXTEN
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)
    _depth += 1
    try:
        yield
    finally:
        _depth -= 1
        if _depth == 0:
            termios.tcsetattr(fd, termios.TCSADRAIN, _saved)

# public

def read_key(*, timeout: Optional[float] = None) -> Optional[str]:
    """
    Waits for ONE key press and returns its name ("a", "enter", "ctrl-s", "f5", ...).
    Returns None if `timeout` (seconds) has passed. Ctrl+C raises KeyboardInterrupt.
    If stdin is not a terminal (pipe), reads one character from it; EOFError at the end.
    """
    if not sys.stdin.isatty():
        ch = sys.stdin.read(1)
        if not ch:
            raise EOFError
        return _name(ch)
    with _raw_mode():
        key = _windows_key(timeout) if WINDOWS else _unix_key(sys.stdin.fileno(), timeout)
    if key == "ctrl-c":
        raise KeyboardInterrupt
    return key

def iter_keys() -> Iterator[str]:
    """
    Endless generator of key presses. The terminal mode is kept for the whole loop
    (no keys are lost or echoed between presses) and restored when the loop ends.

    >>> for key in iter_keys():
    >>>     if key == "enter": break
    """
    with _raw_mode():
        while True:
            yield read_key()

def wait_key(*keys: str, prompt: str = "", ignore_case: bool = True, timeout: Optional[float] = None) -> Optional[str]:
    """
    Waits until one of `keys` is pressed and returns it as it was passed to the function.
    Without `keys` any key is accepted. Returns None on timeout.

    >>> wait_key("y", "n", prompt="Continue? ($green$y$r$/n) ")
    """
    norm = (lambda s: s.lower()) if ignore_case else (lambda s: s)
    wanted = {norm(k): k for k in keys}

    if prompt:
        print(parse_markup(prompt), end="", flush=True)

    end = None if timeout is None else time.monotonic() + timeout

    with _raw_mode():
        while True:
            left = None if end is None else max(0.0, end - time.monotonic())
            key = read_key(timeout=left)
            if key is None:
                return None
            if not wanted:
                return key
            if norm(key) in wanted:
                return wanted[norm(key)]

def pause(prompt: str = "Press any key to continue...") -> None:
    """Prints `prompt` and waits for any key."""
    wait_key(prompt=prompt)
    print()

def confirm(prompt: str = "Continue?", *, default: Optional[bool] = None) -> bool:
    """
    Yes/no question with one key. Enter returns `default` (if it is None, Enter is ignored).
    The hint is [Y/n], [y/N] or [y/n] depending on the default.
    """
    hint = {True: "[Y/n]", False: "[y/N]", None: "[y/n]"}[default]
    keys = ("y", "n") + (("enter",) if default is not None else ())
    answer = wait_key(*keys, prompt=f"{prompt} {hint} ")
    result = default if answer == "enter" else answer == "y"
    print("y" if result else "n")
    return result

STOP = object()   # return it from a Hotkeys handler to finish Hotkeys.run()

class Hotkeys:
    __slots__ = ("ignore_case",)

    def __init__(self, *, ignore_case: bool = False):
        """
        Calls functions on key presses.

        >>> hk = Hotkeys()
        >>> @hk.on("ctrl-s")
        >>> def save(): ...
        >>> @hk.on("q", "escape")
        >>> def quit(): return STOP
        >>> hk.run()
        """
        self.ignore_case = ignore_case
        self._handlers: dict[str, Callable] = {}

    def _norm(self, key: str) -> str:
        return key.lower() if self.ignore_case else key

    def on(self, *keys: str) -> Callable:
        """Decorator: the function is called when any of `keys` is pressed."""
        def decorator(func):
            for k in keys:
                self._handlers[self._norm(k)] = func
            return func
        return decorator

    def run(self) -> None:
        """Blocking loop. Ends when a handler returns STOP (or on Ctrl+C -> KeyboardInterrupt)."""
        for key in iter_keys():
            handler = self._handlers.get(self._norm(key))
            if handler and handler() is STOP:
                break