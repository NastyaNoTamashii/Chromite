import Chromite
from Chromite import Color, Style

Chromite.clear()

Chromite.Write("Добро пожаловать в лялясистему", compose=[Color.pink, Style.bold], pos=(24, 1)).display()
Chromite.Write('Что бы войти в лялясистему нужно войти в аккаунт', compose=Style.italic, pos=(16, 4)).display()
print('\n\n')

# 1. Обычный текстовый ввод
login = Chromite.Catch("Логин > ", compose=Color.cyan, catch_compose=Color.green).up()

# 2. Ввод пароля со звездочками *****
password = Chromite.Catch(
    "Пароль > ", 
    compose=Color.yellow, 
    catch_compose=[Color.green, Style.regular],
    type="password"
).up()

# 3. Ввод пароля с кастомным символом маскировки (например, •)
pin = Chromite.Catch(
    "PIN-код > ",
    compose=Color.blue, 
    catch_compose=[Color.pink, Style.regular],
    type="pin"
).up()

# 4. Ввод числа (не позволит закоммитить Enter, пока пользователь не введет именно цифры)
age = Chromite.Catch("Возраст > ", compose=[Color.cyan, Style.regular], catch_compose=Color.yellow, type="int").up()

print(f"\nАвторизация для {login} прошла успешно!")
print('Были введены такие данные были:\n')

login = Chromite.cInject(login, Style.italic)
password = Chromite.cInject(password, Style.italic)
pin = Chromite.cInject(pin, Style.italic)
age = Chromite.cInject(age, Style.italic)

Chromite.Write(f'Login > {login}\n', compose=[Chromite.Color.cyan]).display()
Chromite.Write(f'Password > {password}\n', compose=[Chromite.Color.cyan]).display()
Chromite.Write(f'PIN-код > {pin}\n', compose=[Chromite.Color.cyan]).display()
Chromite.Write(f'Возраст > {age}', compose=[Chromite.Color.cyan]).display()