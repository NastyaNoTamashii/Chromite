import Chromite
from Chromite import Color, Style

Chromite.clear()

Chromite.Write("Wellcome!", compose=[Color.Pink, Style.Bold], pos=(24, 1)).display()
print('\n\n')

name = Chromite.Catch("Your name > ", compose=Color.Cyan, catch_compose=Color.Yellow).up()

print(f"\nHi {name}!")