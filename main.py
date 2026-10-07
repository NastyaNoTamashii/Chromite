import Chromite
from Chromite import Color, ColorBG, Style

Chromite.clear()

Chromite.Write("$red$Welcome! :tada:$reset$", pos=(24, 1)).display()
print('\n\n')

name = Chromite.Read("Your name > ", compose=Color.Green, value_compose=Color.LightBlue).execute()

Chromite.Write(f"\nHi {name}! :wave:").display()
print('\n')

Chromite.Write('Color from RGB\n', compose=Color.rgb(225, 0, 0)).display()
Chromite.Write('Color from HEX\n', compose=ColorBG.hex("#6aff00")).display()
Chromite.Write('BG Color\n',       compose=ColorBG.DarkBlue).display()

Chromite.Write('$hex#F54927$HEX!$reset$ and $rgb(32,19,214)$RGB!$reset$\n').display()