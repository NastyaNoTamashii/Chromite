import Chromite

Chromite.clear()

# 1. Обычный текстовый ввод
login = Chromite.Catch("Логин > ", compose=Chromite.Color.cyan).up()

# 2. Ввод пароля со звездочками *****
password = Chromite.Catch(
    "Пароль > ", 
    compose=Chromite.Color.yellow, 
    catch_compose=Chromite.Color.green,
    type="password"
).up()

# 3. Ввод пароля с кастомным символом маскировки (например, •)
pin = Chromite.Catch(
    "PIN-код > ",
    compose=Chromite.Color.blue, 
    catch_compose=Chromite.Color.pink,
    type="pin"
).up()

# 4. Ввод числа (не позволит закоммитить Enter, пока пользователь не введет именно цифры)
age = Chromite.Catch("Возраст > ", compose=Chromite.Color.cyan, type="int").up()

print(f"\nАвторизация для {login.flush()} прошла успешно!")
print('Были введены такие данные были:')
Chromite.Write(f'Login > {login}\n', compose=[Chromite.Color.cyan, Chromite.Style.bold]).display()
Chromite.Write(f'Password > {password}\n', compose=[Chromite.Color.cyan, Chromite.Style.bold]).display()
Chromite.Write(f'PIN-код > {pin}\n', compose=[Chromite.Color.cyan, Chromite.Style.bold]).display()
Chromite.Write(f'Возраст > {age}', compose=[Chromite.Color.cyan, Chromite.Style.bold]).display()
