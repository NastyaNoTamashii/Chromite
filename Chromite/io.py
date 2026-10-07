"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['Write', 'Read', 'cInject', 'clear']

import sys, re
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement, move_cursor, show_cursor
from .formatting import BaseCodes, Color, ColorBG, Style
from ._markup import parse_markup

# Type Hint for styles: one element or list/tuple of elements
StyleType = Union[ANSIElement, List[ANSIElement], Tuple[ANSIElement, ...]]

PosType = Tuple[int, int]  # (x, y) or (col, row)

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import tty
    import termios
    WINDOWS = False

def _read_masked_input(mask_char: str) -> str:
    """Reads input with character masking, without standard terminal echo."""
    buf = []
    while True:
        if WINDOWS:
            ch = msvcrt.getch()
            if ch in (b"\r", b"\n"):
                print()
                break
            elif ch == b"\x08":  # Backspace
                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch not in (b"\x00", b"\xe0"):
                try:
                    char_str = ch.decode("utf-8")
                    buf.append(char_str)
                    sys.stdout.write(mask_char)
                    sys.stdout.flush()
                except UnicodeDecodeError:
                    pass
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            if ch in ("\r", "\n"):
                print()
                break
            elif ch in ("\x7f", "\x08"):  # Backspace
                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":  # Ctrl+C
                raise KeyboardInterrupt
            else:
                buf.append(ch)
                sys.stdout.write(mask_char)
                sys.stdout.flush()

    return "".join(buf)

class Write:
    __slots__ = ("text", "compose", "pos",)

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

        self._validate_compose(compose)

    def _validate_compose(self, compose: StyleType) -> None:
        if compose is None:
            return
        if isinstance(compose, ANSIElement):
            return
        if isinstance(compose, (list, tuple)) and all(isinstance(comp, ANSIElement) for comp in compose):
            return
        raise TypeError("The 'compose' component must have a Chromite object. (Color, ColorBG, Style etc.)")

    def _text_processing(self) -> str:
        """Assembles and returns the styled string with position codes."""
        text = self.text
        if self.compose:
            if isinstance(self.compose, ANSIElement):
                style = str(self.compose)
            else:
                style = "".join(str(c) for c in self.compose)
            text = f"{style}{text}{BaseCodes.RESET}"

        if self.pos is not None:
            x, y = self.pos
            text = f"{move_cursor(max(1, x + 1), max(1, y + 1))}{text}"

        return text

    def flush(self) -> str:
        """Returns the processed string text."""
        return self._text_processing()

    def display(self) -> None:
        """Immediately outputs text to the terminal."""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

    def __call__(self) -> None:
        return self.display()

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

        self._validate_compose(self.compose)
        self._validate_compose(self.value_compose)

    def _validate_compose(self, style: StyleType) -> None:
        if style is None or isinstance(style, ANSIElement):
            return
        if isinstance(style, (list, tuple)) and all(isinstance(s, ANSIElement) for s in style):
            return
        raise TypeError("The 'compose' component must have a Chromite object. (Color, ColorBG, Style etc.)")

    def _input_style(self) -> str:
        """Applying styles to text."""
        if not self.compose:
            return self.prompt
        if isinstance(self.compose, ANSIElement):
            return f"{self.compose}{self.prompt}{BaseCodes.RESET}"
        if isinstance(self.compose, (list, tuple)):
            ansi_seq = "".join(str(s) for s in self.compose)
            return f"{ansi_seq}{self.prompt}{BaseCodes.RESET}"
        return self.prompt

    def _prepare_prompt(self) -> str:
        """Assembles an ANSI string for the prompt and cursor position."""
        formatted_prompt = self._input_style()
        
        if self.pos is not None:
            x, y = self.pos
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            formatted_prompt = f"{ansi_pos}{formatted_prompt}"
        
        input_ansi_start = ""
        if self.value_compose:
            if isinstance(self.value_compose, ANSIElement):
                input_ansi_start = str(self.value_compose)
            elif isinstance(self.value_compose, (list, tuple)):
                input_ansi_start = "".join(str(s) for s in self.value_compose)

        return f"{show_cursor()}{formatted_prompt}{input_ansi_start}"

    def _input_type(self) -> str:
        """Processing of input text based on the specified input data type. (password, pin, int etc.)."""
        full_prompt = self._prepare_prompt()

        if self.type == "password":
            sys.stdout.write(full_prompt)
            sys.stdout.flush()
            return _read_masked_input(mask_char='*')

        elif self.type == "pin":
            sys.stdout.write(full_prompt)
            sys.stdout.flush()
            return _read_masked_input(mask_char='•')

        elif self.type == "hidden":
            sys.stdout.write(full_prompt)
            sys.stdout.flush()
            return _read_masked_input(mask_char="")

        elif self.type in ("int", "number"):
            while True:
                raw = input(full_prompt).strip()
                try:
                    int(raw)
                    return raw
                except ValueError:
                    sys.stdout.write("\033[1A\033[2K")
                    sys.stdout.flush()

        else:
            return input(full_prompt)

    def execute(self) -> Write:
        """Main method: initiates the interaction process."""
        try:
            user_input = self._input_type()
        finally:
            sys.stdout.write(str(BaseCodes.RESET))
            sys.stdout.flush()

        return Write(user_input, compose=self.value_compose, markup=False)

    def __call__(self) -> Write:
        return self.execute()

def cInject(text: str, compose: StyleType) -> str:
    return f"{compose}{text}{BaseCodes.RESET}"

def clear() -> None:
    """Clears the terminal screen."""
    print('\x1b[2J\x1b[H')