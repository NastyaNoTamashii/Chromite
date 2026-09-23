import Chromite

text = Chromite.Write("Hello, World!", style=[Chromite.Color.red, Chromite.Style.bold])

table = Chromite.Table.createTable(
    [["Product", "Cost"],{"Strawberry": "2$","Blueberry":"2,71$","Banana":"1,63$","Apple":"30¢","Limon":"2$",}]
)

table = Chromite.sjoin(table, Chromite.Color.green)

print(text.flush())  # Выводит обработанную строку без стилей
print(table)  # Выводит обработанную строку без стилей