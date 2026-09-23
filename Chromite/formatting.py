import random
from .codes import ANSIElement, make_ansi

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

    @property
    def random(self) -> ANSIElement:
        """Returns a random background color each time."""
        return make_ansi(random.randint(40, 47))

class Style(BaseCodes):
    bold     = make_ansi(1)
    italic   = make_ansi(3)
    url      = make_ansi(4)
    link     = make_ansi(5)
    selected = make_ansi(7)

color = Color()
color_bg = ColorBG()
style = Style()
