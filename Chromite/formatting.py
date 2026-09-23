"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import random
from .codes import ANSIElement, make_ansi

__all__ = ['color', 'color_bg', 'style']

class BaseCodes:
    RESET = make_ansi(0)

class Color(BaseCodes):
    black  = make_ansi(30)
    red    = make_ansi(31)
    green  = make_ansi(32)
    yellow = make_ansi(33)
    blue   = make_ansi(34)
    violet = make_ansi(35)
    cyan   = make_ansi(36)
    white  = make_ansi(37)
    pink   = make_ansi('38;5;206')

    light_red    = make_ansi(91)
    light_green  = make_ansi(92)
    light_yellow = make_ansi(93)
    light_blue   = make_ansi(94)
    light_violet = make_ansi(95)
    light_cyan   = make_ansi(96)
    light_yellow = make_ansi(97)

    @property
    def random(self) -> ANSIElement:
        """Returns a random text color each time."""
        return make_ansi(random.randint(30, 37))

class ColorBG(BaseCodes):
    black  = make_ansi(40)
    red    = make_ansi(41)
    green  = make_ansi(42)
    yellow = make_ansi(43)
    blue   = make_ansi(44)
    violet = make_ansi(45)
    cyan   = make_ansi(46)
    white  = make_ansi(47)

    light_red    = make_ansi(101)
    light_green  = make_ansi(102)
    light_yellow = make_ansi(103)
    light_blue   = make_ansi(104)
    light_violet = make_ansi(105)
    light_cyan   = make_ansi(106)
    light_yellow = make_ansi(107)

    @property
    def random(self) -> ANSIElement:
        """Returns a random background color each time."""
        return make_ansi(random.randint(40, 47))

class Style(BaseCodes):
    bold      = make_ansi(1)
    dim       = make_ansi(2)
    italic    = make_ansi(3)
    underline = make_ansi(4)
    blink     = make_ansi(5)
  # blink     = make_ansi(6) Also blink
    inversed  = make_ansi(7)
    hide      = make_ansi(8)
    strike    = make_ansi(9)
    
color = Color()
color_bg = ColorBG()
style = Style()