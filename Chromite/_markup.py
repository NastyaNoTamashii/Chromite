"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import re
from .formatting import BaseCodes, Color, ColorBG, Style
from ._emoji_map import EMOJI_MAP

def _resolve_style_tag(tag_name: str) -> str:
    """Dynamically resolves $style$ and $bg_style$ into ANSI codes."""
    tag_raw = tag_name.strip()
    tag_lower = tag_raw.lower()

    if tag_lower in ("reset", "r", "no_color", "/"):
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