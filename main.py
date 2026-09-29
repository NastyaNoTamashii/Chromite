import Chromite
from Chromite import Color, ColorBG, Style

Chromite.clear()

Chromite.Write("Wellcome!", compose=[Color.Green, Style.Bold], pos=(24, 1)).display()
print('\n\n')

name = Chromite.Read("Your name > ", compose=Color.Blue, value_compose=Color.LightBlue).execute()

print(f"\nHi {name}!\n")

Chromite.Write('Color from RGB\n', compose=Color.rgb(225, 0, 0)).display()
Chromite.Write('Color from HEX\n', compose=Color.hex('#ff5733')).display()
Chromite.Write('BG Color\n',       compose=ColorBG.DarkBlue).display()