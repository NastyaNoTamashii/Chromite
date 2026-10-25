"""

Chromite/io.py
~~~~~~~~~~~~~~
Main library files: Write, Read.

Copyright (C) 2026 NastyaNoTamashii.
License: MIT
Author: NastyaNoTamashii

"""

__all__ = ['Write', 'Read', 'cInject', 'clear']

import sys
from typing import Optional
from .terminal import show_cursor, place
from .codes import ANSIElement, validate_compose, apply_compose
from .fmt import BaseCodes
from ._base import Renderable
from ._markup import parse_markup
from ._types import StyleType, PosType

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import tty
    import termios
    WINDOWS = False

def _read_masked_input(mask_char: str) -> str:
    """Reads input with character masking, without standard terminal echo."""
    if not sys.stdin.isatty():
        return sys.stdin.readline().rstrip("\n")
    buf = []

    def erase():
        if mask_char:
            print("\b \b", end="", flush=True)

    def add(ch):
        buf.append(ch)
        if mask_char:
            print(mask_char, end="", flush=True)

    if WINDOWS:
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print(); break
            if ch == "\x03": # Ctrl+C
                raise KeyboardInterrupt
            if ch in ("\x00", "\xe0"):
                msvcrt.getwch() # Second arrow key/F key code.
                continue
            if ch == "\x08": # Backspace
                if buf: buf.pop(); erase()
            elif ch.isprintable():
                add(ch)
    else:
        fd = sys.stdin.fileno()
        old = tty.setcbreak(fd, termios.TCSADRAIN)
        try:
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print(); break
                if ch in ("\x7f", "\x08"): # Backspace
                    if buf: buf.pop(); erase()
                elif ch == "\x1b": # Arrows: \x1b[A, \x1b[3~ ...
                    if sys.stdin.read(1) == "[":
                        while not "@" <= sys.stdin.read(1) <= "~":
                            pass
                elif ch.isprintable():
                    add(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return "".join(buf)

class Write(Renderable):
    __slots__ = ("text", "compose", "pos", "markup",)

    def __init__(
        self, 
        text: str, 
        *, 
        compose: StyleType = None, 
        pos: Optional[PosType] = None,
        markup: bool = True,
    ):
        """
        :param text: The raw text string to be processed and rendered to the terminal.
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to the entire text string.
        :param pos: Optional (x, y) coordinates for precise terminal cursor positioning before writing.
        :param markup: If True, parses inline markup (:emoji: tags and $style$ color codes) before rendering.
        """
        self.text = parse_markup(str(text)) if markup else str(text)
        self.compose = compose
        self.pos = pos

        validate_compose(self.compose)

    def flush(self) -> str:
        """Returns the finished text as a string, with the style (compose) and the cursor position (pos) applied. Nothing is printed. Calling it several times gives the same result."""
        text = apply_compose(self.text, self.compose)
        return place(text, self.pos)

class Read:
    __slots__ = ("prompt", "compose", "value_compose", "pos", "type",)

    def __init__(
        self,
        prompt: str = "> ",
        *,
        compose: StyleType = None,
        value_compose: StyleType = None,
        pos: Optional[PosType] = None,
        type: str = "text",
    ):
        """
        :param prompt: Prompt text displayed before the user input field. Supports inline markup (:emoji: and $style$).
        :param compose: ANSI style or sequence of styles (Color, ColorBG, Style) applied to the prompt label.
        :param value_compose: ANSI style or sequence of styles applied to user input text and retained in the returned Write object.
        :param pos: Optional (x, y) coordinates for precise terminal cursor positioning where the prompt starts.
        :param type: Input rendering mode ("text", "password", "pin", "hidden", "int" / "number").
        """
        self.prompt = parse_markup(str(prompt))
        self.compose = compose
        self.value_compose = value_compose
        self.pos = pos
        self.type = type.lower()

        validate_compose(self.compose)
        validate_compose(self.value_compose)

    def _prepare_prompt(self) -> str:
        """Assembles an ANSI string for the prompt and cursor position."""
        formatted_prompt = apply_compose(self.prompt, self.compose)
        
        input_ansi_start = ""
        if self.value_compose:
            if isinstance(self.value_compose, ANSIElement):
                input_ansi_start = str(self.value_compose)
            elif isinstance(self.value_compose, (list, tuple)):
                input_ansi_start = "".join(str(s) for s in self.value_compose)

        return place(f"{show_cursor()}{formatted_prompt}{input_ansi_start}", self.pos)

    def _input_type(self) -> str:
        """Processing of input text based on the specified input data type. (password, pin, int etc.)."""
        full_prompt = self._prepare_prompt()

        if self.type == "password":
            print(full_prompt, end="", flush=True)
            return _read_masked_input(mask_char='*')

        elif self.type == "pin":
            print(full_prompt, end="", flush=True)
            return _read_masked_input(mask_char='•')

        elif self.type == "hidden":
            print(full_prompt, end="", flush=True)
            return _read_masked_input(mask_char="")

        elif self.type in ("int", "number"):
            while True:
                raw = input(full_prompt).strip()
                try:
                    int(raw)
                    return raw
                except ValueError:
                    print("\x1b[1A\x1b[2K", end="", flush=True)

        else:
            return input(full_prompt)

    def execute(self) -> Write:
        """Main method: initiates the interaction process."""
        try:
            user_input = self._input_type()
        finally:
            print(str(BaseCodes.RESET), end="", flush=True)

        return Write(user_input, compose=self.value_compose, markup=False)

    def __call__(self) -> Write:
        return self.execute()

def cInject(text: str, compose: StyleType) -> str:
    return f"{compose}{text}{BaseCodes.RESET}"