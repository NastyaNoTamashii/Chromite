import Chromite
from Chromite import Color, ColorBG, Style, Table

Chromite.clear()

Chromite.Write("$red$Welcome! :tada:$reset$", pos=(24, 1)).display()
print('\n\n')

name = Chromite.Read("Your name > ", compose=Color.Green, value_compose=Color.LightBlue).execute()
age = Chromite.Read("Your age > ", compose=Color.Green, value_compose=Color.LightBlue).execute()

print('\n')

table = Table(style = Chromite.TableStyle.Rounded)

table.add_column("Name", compose=Color.Gold)
contacts = table.add_column("Contacts :tada:")
table.add_column("Email", parent=contacts)
chats = table.add_column("Messengers", parent=contacts)
table.add_column("Telegram", parent=chats)
table.add_column("WhatsApp", parent=chats)
table.add_column("Age", align="right")

table.add_row("Oleg", "oleg@gmail.com", "@oleg", "+38(098)000-00-00", 25, compose=Color.Red)
table.add_row("Natalka", "natalka@outlook.com", "@natalka", None, 31)
table.add_row(name, "yourmail@mail.com", f"@{name}", "+0(00)000-00-00", age, compose=[Color.LightBlue, Style.Underline])

table.display()

Chromite.Write(f"\nHi {name}! :wave:").display()
print('\n')