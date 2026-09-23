import sys
from typing import Union, List, Tuple
from .codes import ANSIElement
from .formatting import BaseCodes

# Тип-хинт для стилей: один элемент или список/кортеж элементов
StyleType = Union[ANSIElement, List[ANSIElement], Tuple[ANSIElement, ...]]

class Write:
    __slots__ = ("text",)

    def __init__(self, text: str, *, style: StyleType = None):
        self.text = str(text)

        if style:
            # 1. Если передан один правильный ANSI-стиль
            if isinstance(style, ANSIElement):
                self.text = f"{style}{self.text}{BaseCodes.RESET}"
            
            # 2. Если передана коллекция стилей (например: style=[color.red, style.bold])
            elif isinstance(style, (list, tuple)) and all(isinstance(s, ANSIElement) for s in style):
                ansi_sequence = "".join(style)
                self.text = f"{ansi_sequence}{self.text}{BaseCodes.RESET}"
            
            # 3. Если подсунули левую строку или не тот объект
            else:
                raise TypeError("Style must be an ANSIElement or a collection of ANSIElements (from Chromite).")

    def to_lower(self) -> "Write":    
        """Приводит текст к нижнему регистру (вернули self для чейнинга)"""
        self.text = self.text.lower()
        return self

    def translit(self) -> "Write":
        """Транслитерация текста (заготовка под твою функцию)"""
        # Сюда добавишь логику транслита
        return self

    def render_list(self, items: list) -> None:
        """Красиво выводит нумерованный список в консоль"""
        for index, item in enumerate(items):
            print(f"{index}. {item}")

    def flush(self) -> str:
        """Возвращает обработанную строку"""
        return self.text
    
    def display(self) -> None:
        """Сразу выводит текст в консоль без явного print()"""
        print(self.text)

def sjoin(text: str, style: StyleType) -> str:
    return f"{style}{text}{BaseCodes.RESET}"

def clear() -> None:
    """Clears the terminal screen."""
    print('\x1b[2J\x1b[H')