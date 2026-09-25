"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['Write', 'Catch', 'cInject', 'clear']

import sys
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement, move_cursor, show_cursor
from .formatting import BaseCodes

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
        pos: Optional[PosType] = None
    ):
        """
        :param text: Text
        :param compose: Set style for text.
        :param pos: Set position (x, y).
        """
        self.text = str(text)
        self.compose = compose
        self._validate_compose(compose)
        self.pos = pos

    def _validate_compose(self, compose: StyleType) -> None:
        if compose is None:
            return
        if isinstance(compose, ANSIElement):
            return
        if isinstance(compose, (list, tuple)) and all(isinstance(comp, ANSIElement) for comp in compose):
            return
        raise TypeError("Style must be an ANSIElement or a collection of ANSIElements (from Chromite).")

    def flush(self) -> str:
        """Assembles and returns the styled string with position codes."""
        if self.compose:
            if isinstance(self.compose, ANSIElement):
                self.text = f"{self.compose}{self.text}{BaseCodes.RESET}"
            elif isinstance(self.compose, (list, tuple)):
                ansi_sequence = "".join(str(comp) for comp in self.compose)
                self.text = f"{ansi_sequence}{self.text}{BaseCodes.RESET}"
            
        """Returns a string."""
        if self.pos is not None:
            x, y = self.pos
            # Converting to 1-based terminal coordinates (1, 1 — top-left corner)
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            return f"{ansi_pos}{self.text}"
        
        return self.text

    def display(self) -> None:
        """Immediately outputs text to the terminal"""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

class Catch:
    __slots__ = ("prompt", "compose", "catch_compose", "pos", "type")

    def __init__(
        self,
        prompt: str = "> ",
        *,
        compose: StyleType = None,
        catch_compose: StyleType = None,
        pos: Optional[PosType] = None,
        type: str = "text",
    ):
        """
        :param prompt: Prompt text.
        :param compose: Set style for prompt text.
        :param catch_compose: Style for the input text and the value returned by Write.
        :param pos: Position (x, y) for rendering the input field.
        :param type: Input type ("text", "password", "pin", "hidden", "int").
        """
        self.prompt = str(prompt)
        self.compose = compose
        self.catch_compose = catch_compose
        self.pos = pos
        self.type = type.lower()

        self._validate_style(self.compose)
        self._validate_style(self.catch_compose)

    def _validate_style(self, style: StyleType) -> None:
        if style is None or isinstance(style, ANSIElement):
            return
        if isinstance(style, (list, tuple)) and all(isinstance(s, ANSIElement) for s in style):
            return
        raise TypeError("Style must be an ANSIElement or a collection of ANSIElements (from Chromite).")

    def _apply_style(self, text: str, style: StyleType) -> str:
        """Вспомогательный метод для применения стилей."""
        if not style:
            return text
        if isinstance(style, ANSIElement):
            return f"{style}{text}{BaseCodes.RESET}"
        if isinstance(style, (list, tuple)):
            ansi_seq = "".join(str(s) for s in style)
            return f"{ansi_seq}{text}{BaseCodes.RESET}"
        return text

    def up(self) -> Write:
        """
        Moves the cursor (if `pos` is specified), activates the input style,
        reads the text according to `type`, and resets the styles.
        """
        formatted_prompt = self._apply_style(self.prompt, self.compose)

        # If coordinates are specified, add cursor position
        if self.pos is not None:
            x, y = self.pos
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            formatted_prompt = f"{ansi_pos}{self.prompt}"

        # Preparing the ANSI code for the input style.
        input_ansi_start = ""
        if self.catch_compose:
            if isinstance(self.catch_compose, ANSIElement):
                input_ansi_start = str(self.catch_compose)
            elif isinstance(self.catch_compose, (list, tuple)):
                input_ansi_start = "".join(str(s) for s in self.catch_compose)

        # Enable the cursor display and apply a style to the input itself.
        full_prompt = f"{show_cursor()}{formatted_prompt}{input_ansi_start}"

        try:
            # 4. Обработка ввода в зависимости от type
            if self.type == "password":
                sys.stdout.write(full_prompt)
                sys.stdout.flush()
                user_input = _read_masked_input(mask_char='*')

            elif self.type == "pin":
                sys.stdout.write(full_prompt)
                sys.stdout.flush()
                user_input = _read_masked_input(mask_char='•')

            elif self.type == "hidden":
                sys.stdout.write(full_prompt)
                sys.stdout.flush()
                user_input = _read_masked_input(mask_char="")

            elif self.type in ("int", "number"):
                while True:
                    raw = input(full_prompt)
                    if raw.strip().isdigit():
                        user_input = raw
                        break

                    # If the input is not a number, clear the string and repeat.
                    sys.stdout.write(f"\033[1A\033[2K")
                    sys.stdout.flush()

            else:
                # Standard text input.
                user_input = input(full_prompt)

        finally:
            # Resetting terminal styles.
            sys.stdout.write(str(BaseCodes.RESET))
            sys.stdout.flush()

        # Return the Write object, storing catch_compose within it.
        return Write(user_input, compose=self.catch_compose)

    def __call__(self) -> Write:
        return self.up()

def cInject(text: str, compose: StyleType) -> str:
    return f"{compose}{text}{BaseCodes.RESET}"

def clear() -> None:
    """Clears the terminal screen."""
    print('\x1b[2J\x1b[H')