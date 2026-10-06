import Chromite
from Chromite import Color, ColorBG, Style

Chromite.clear()

Chromite.Write("$BrightRed$Welcome! :tada:$reset$", pos=(24, 1)).display()
print('\n\n')

name = Chromite.Read("Your name > ", compose=Color.Green, value_compose=Color.LightBlue).execute()

Chromite.Write(f"\nHi {name}! :wave:").display()
print('\n')

Chromite.Write('Color from RGB\n', compose=Color.rgb(225, 0, 0)).display()
Chromite.Write('Color from HEX\n', compose=Color.hex('#ff5733')).display()
Chromite.Write('BG Color\n',       compose=ColorBG.DarkBlue).display()