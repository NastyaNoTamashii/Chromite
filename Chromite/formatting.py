"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import random
from .codes import ANSIElement, make_ansi, make_ansi_x256, make_ansi_rgb

__all__ = ['color', 'color_bg', 'style']

class BaseCodes:
    RESET = make_ansi(0)

class Color(BaseCodes):
    """Colors with True-color support (RGB)."""
    Black        = make_ansi_rgb(0  , 0  , 0  )
    Gray         = make_ansi_rgb(128, 128, 128)
    LightGray    = make_ansi_rgb(211, 211, 211)
    Silver       = make_ansi_rgb(192, 192, 192)
    White        = make_ansi_rgb(255, 255, 255)
    SkyBlue      = make_ansi_rgb(135, 206, 235)
    LightBlue    = make_ansi_rgb(173, 216, 230)
    BrightBlue   = make_ansi_rgb(0  , 0  , 255)
    DarkBlue     = make_ansi_rgb(0  , 0  , 139)
    Blue         = make_ansi_x256(4)
    LightRed     = make_ansi_rgb(255, 204, 203)
    Red          = make_ansi_x256(9)
    BrightRed    = make_ansi_rgb(255, 0  , 0  ) 
    DarkRed      = make_ansi_rgb(139, 0  , 0  )
    LightGreen   = make_ansi_rgb(144, 238, 144)
    Green        = make_ansi_rgb(0  , 128, 0  )
    DarkGreen    = make_ansi_rgb(0  , 100, 0  )
    Lime         = make_ansi_rgb(50 , 205, 50 )
    BrightLime   = make_ansi_rgb(0  , 255, 0  )
    LightYellow  = make_ansi_rgb(255, 249, 196)
    Yellow       = make_ansi_x256(3)
    BrightYellow = make_ansi_rgb(255, 255, 0  )
    Gold         = make_ansi_rgb(255, 215, 0  )
    Cyan         = make_ansi_x256(6)
    BrightCyan   = make_ansi_rgb(0  , 255, 255) 
    Orange       = make_ansi_rgb(255, 165, 0  )
    DarkOrange   = make_ansi_rgb(255, 140, 0  )
    Magenta      = make_ansi_rgb(180, 40 , 180)
    BrightMagenta= make_ansi_rgb(255, 0  , 255)
    Pink         = make_ansi_rgb(255, 192, 203)
    Purple       = make_ansi_rgb(128, 0  , 128)

    @staticmethod
    def rgb(r: int, b: int, g: int) -> ANSIElement:
        """Returns the text color from the rgb-color palette (red, blue, green)."""
        if any(not (0 <= x <= 255) for x in (r, g, b)):
            raise ValueError("256-color index must be between 0 and 255.")
        return make_ansi_rgb(r, g, b)
    
    @staticmethod
    def hex(hex: str) -> ANSIElement:
        """Returns the text color from the HEX palette."""
        hex = hex.lstrip('#')
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        return make_ansi_rgb(rgb[0], rgb[1], rgb[2])
    
    @staticmethod
    def x256(code: int) -> ANSIElement:
        """Returns the text color from the 256-color palette (0–255)."""
        if not 0 <= code <= 255:
            raise ValueError("256-color index must be between 0 and 255.")
        return make_ansi_x256(f"{code}")
    
    @property
    def Random(self) -> ANSIElement:
        """Returns a random text color each time."""
        return make_ansi_x256(random.randint(0, 255))

class ColorBG(BaseCodes):
    Black        = make_ansi_rgb(0  , 0  , 0  , bg=True)
    Gray         = make_ansi_rgb(128, 128, 128, bg=True)
    LightGray    = make_ansi_rgb(211, 211, 211, bg=True)
    Silver       = make_ansi_rgb(192, 192, 192, bg=True)
    White        = make_ansi_rgb(255, 255, 255, bg=True)
    SkyBlue      = make_ansi_rgb(135, 206, 235, bg=True)
    LightBlue    = make_ansi_rgb(173, 216, 230, bg=True)
    BrightBlue   = make_ansi_rgb(0  , 0  , 255, bg=True)
    DarkBlue     = make_ansi_rgb(0  , 0  , 139, bg=True)
    Blue         = make_ansi_x256(4, bg=True)
    LightRed     = make_ansi_rgb(255, 204, 203, bg=True)
    Red          = make_ansi_x256(9, bg=True)
    BrightRed    = make_ansi_rgb(255, 0  , 0  , bg=True) 
    DarkRed      = make_ansi_rgb(139, 0  , 0  , bg=True)
    LightGreen   = make_ansi_rgb(144, 238, 144, bg=True)
    Green        = make_ansi_rgb(0  , 128, 0  , bg=True)
    DarkGreen    = make_ansi_rgb(0  , 100, 0  , bg=True)
    Lime         = make_ansi_rgb(50 , 205, 50 , bg=True)
    BrightLime   = make_ansi_rgb(0  , 255, 0  , bg=True)
    LightYellow  = make_ansi_rgb(255, 249, 196, bg=True)
    Yellow       = make_ansi_x256(3, bg=True)
    BrightYellow = make_ansi_rgb(255, 255, 0  , bg=True)
    Gold         = make_ansi_rgb(255, 215, 0  , bg=True)
    Cyan         = make_ansi_x256(6, bg=True)
    BrightCyan   = make_ansi_rgb(0  , 255, 255, bg=True) 
    Orange       = make_ansi_rgb(255, 165, 0  , bg=True)
    DarkOrange   = make_ansi_rgb(255, 140, 0  , bg=True)
    Magenta      = make_ansi_rgb(180, 40 , 180, bg=True)
    BrightMagenta= make_ansi_rgb(255, 0  , 255, bg=True)
    Pink         = make_ansi_rgb(255, 192, 203, bg=True)
    Purple       = make_ansi_rgb(128, 0  , 128, bg=True)

    @staticmethod
    def rgb(r: int, b: int, g: int) -> ANSIElement:
        """Returns the text color from the rgb-color palette (red, blue, green)."""
        if any(not (0 <= x <= 255) for x in (r, g, b)):
            raise ValueError("256-color index must be between 0 and 255.")
        return make_ansi_rgb(r, g, b, bg = True)
    
    @staticmethod
    def hex(hex: str) -> ANSIElement:
        """Returns the text color from the HEX palette."""
        hex = hex.lstrip('#')
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        return make_ansi_rgb(rgb[0], rgb[1], rgb[2], bg = True)
    
    @staticmethod
    def x256(code: int) -> ANSIElement:
        """Returns the text color from the 256-color palette (0–255)."""
        if not 0 <= code <= 255:
            raise ValueError("256-color index must be between 0 and 255.")
        return make_ansi_x256(f"{code}", bg = True)

    @property
    def Random(self) -> ANSIElement:
        """Returns a random background color each time."""
        return make_ansi_x256(random.randint(0, 255), bg = True)

class Style(BaseCodes):
    Bold      = make_ansi(1)
    Dim       = make_ansi(2)
    Italic    = make_ansi(3)
    Underline = make_ansi(4)
    Blink     = make_ansi(5)
  # Blink     = make_ansi(6) Also blink
    Inversed  = make_ansi(7)
    Hide      = make_ansi(8)
    Strike    = make_ansi(9)
    Regular   = make_ansi(22)
    
color = Color()
color_bg = ColorBG()
style = Style()