"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['Write', 'Read', 'cInject', 'clear']

import sys, re
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement, move_cursor, show_cursor
from .formatting import BaseCodes, Color, ColorBG, Style
from ._emoji_map import EMOJI_MAP

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

def _resolve_style_tag(tag_name: str) -> str:
    """Dynamically resolves $style$ and $bg_style$ into ANSI codes."""
    tag_raw = tag_name.strip()
    tag_lower = tag_raw.lower()

    if tag_lower in ("reset", "r", "no_color"):
        return str(BaseCodes.RESET)
    
    # HEX: $hex#ffffff$ or $hex#fff$
    if tag_lower.startswith("hex#"):
        hex_code = tag_raw[3:]
        try:
            return str(Color.hex(hex_code))
        except Exception:
            return f"${tag_name}$"

    # RGB: $rgb(255,0,0)$ or $rgb255,0,0$
    if tag_lower.startswith("rgb"):
        rgb_code = re.sub(r"[^\d,]", "", tag_raw )
        parts = rgb_code.split(",")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            try:
                r, g, b = map(int, parts)
                return str(Color.rgb(r, g, b))
            except Exception:
                pass
        return f"${tag_name}$"
            
    """
    For all background styles.
    Exemple:
    - $bg_red$
    - $bg_hex#ffffff$
    - $bg_rgb(255,255,255)
    """
    if tag_lower.startswith("bg_"):
        bg_target = tag_lower[3:]
        bg_raw = tag_raw[3:]

        # Background HEX: $bg_hex#ffffff$ or $bg_hex#fff$
        if bg_target.startswith("hex#"):
            hex_code = bg_raw[4:]
            try:
                return str(ColorBG.hex(hex_code))
            except Exception:
                return f"${tag_name}$"

        # Background RGB: $bg_rgb(255,0,0)$ or $bg_rgb255,0,0$
        if bg_target.startswith("rgb"):
            rgb_code = re.sub(r"[^\d,]", "", bg_raw)
            parts = rgb_code.split(",")
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                try:
                    r, g, b = map(int, parts)
                    return str(ColorBG.rgb(r, g, b))
                except Exception:
                    pass
            return f"${tag_name}$"

        # 3. Background Named Colors: $bg_red$
        for attr in dir(ColorBG):
            if attr.lower() == bg_target and not attr.startswith("_"):
                return str(getattr(ColorBG, attr))

        return f"${tag_name}$"

    # For colors. Exemple $red$
    for attr in dir(Color):
        if attr.lower() == tag_lower and not attr.startswith("_"):
            return str(getattr(Color, attr))

    # For styles. Exemple $bold$
    for attr in dir(Style):
        if attr.lower() == tag_lower and not attr.startswith("_"):
            return str(getattr(Style, attr))

    return f"${tag_name}$"

def parse_markup(text: str) -> str:
    """
    Converts :emoji: and $style$ into actual Unicode emojis and style/color codes.
    """
    if not text or not isinstance(text, str):
        return text

    # Replace :emoji:
    def replace_emoji(match):
        name = match.group(1)
        return EMOJI_MAP.get(name, match.group(0))

    # Replace $style$
    def replace_style(match):
        name = match.group(1)
        return _resolve_style_tag(name)

    # :tag:
    text = re.sub(r":([a-zA-Z0-9_]+):", replace_emoji, text)
    # $tag$
    text = re.sub(r"\$([a-zA-Z0-9_#,\(\)]+)\$", replace_style, text)

    return text

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
        self.text = parse_markup(str(text))
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
        if self.pos is not None:
            x, y = self.pos
            # Converting to 1-based terminal coordinates (1, 1 — top-left corner)
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            return f"{ansi_pos}{self.text}"
        
        if self.compose:
            if isinstance(self.compose, ANSIElement):
                self.text = f"{self.compose}{self.text}{BaseCodes.RESET}"
            elif isinstance(self.compose, (list, tuple)):
                ansi_sequence = "".join(str(comp) for comp in self.compose)
                self.text = f"{ansi_sequence}{self.text}{BaseCodes.RESET}"
            
        return self.text

    def flush(self) -> str:
        """Returns the processed string text."""
        self.text = self._text_processing()

        return self.text

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
        :param prompt: Prompt text.
        :param compose: Set style for prompt text.
        :param value_compose: Style for the input text and the value returned by Write.
        :param pos: Position (x, y) for rendering the input field.
        :param type: Input type ("text", "password", "pin", "hidden", "int").
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
                raw = input(full_prompt)
                if raw.strip().isdigit():
                    return raw
                sys.stdout.write(f"\033[1A\033[2K")
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

        return Write(user_input, compose=self.value_compose)

    def __call__(self) -> Write:
        return self.execute()

def cInject(text: str, compose: StyleType) -> str:
    return f"{compose}{text}{BaseCodes.RESET}"

def clear() -> None:
    """Clears the terminal screen."""
    print('\x1b[2J\x1b[H')