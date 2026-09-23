from Chromite import io, Write, Catch, Color

io.clear()

hello = Write('Hello. What is your name?\n\n', compose=[Color.yellow])
hello.display()

name = Catch('Name > ', compose=Color.yellow, catch_compose=Color.green)

print(Write(f'\nI love you, {name.up()}', compose=Color.red).flush())