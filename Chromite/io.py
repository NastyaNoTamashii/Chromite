"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['Write', 'Catch', 'sjoin', 'clear']

import sys
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement, move_cursor, show_cursor
from .formatting import BaseCodes

# Тип-хинт для стилей: один элемент или список/кортеж элементов
StyleType = Union[ANSIElement, List[ANSIElement], Tuple[ANSIElement, ...]]

PosType = Tuple[int, int]  # (x, y) или (col, row)

class Write:
    __slots__ = ("text", "compose", "pos",)

    def __init__(
        self, 
        text: str, 
        *, 
        compose: StyleType = None, 
        pos: Optional[PosType] = None
    ):
        """
        :param text: Text
        :param compose: Set style for text.
        :param pos: Set position (x, y).
        """
        self.text = str(text)
        self.pos = pos

        if compose:
            # 1. Если передан один правильный ANSI-стиль
            if isinstance(compose, ANSIElement):
                self.text = f"{compose}{self.text}{BaseCodes.RESET}"
            
            # 2. Если передана коллекция стилей (например: style=[color.red, style.bold])
            elif isinstance(compose, (list, tuple)) and all(isinstance(comp, ANSIElement) for comp in compose):
                ansi_sequence = "".join(compose)
                self.text = f"{ansi_sequence}{self.text}{BaseCodes.RESET}"
            
            # 3. Если подсунули левую строку или не тот объект
            else:
                raise TypeError("Style must be an ANSIElement or a collection of ANSIElements (from Chromite).")

    def render_list(self, items: list) -> None:
        """Красиво выводит нумерованный список в консоль"""
        for index, item in enumerate(items):
            print(f"{index}. {item}")
    
    def flush(self) -> str:
        """Возвращает строку с учетом позиционирования курсора"""
        if self.pos is not None:
            x, y = self.pos
            # Приводим к 1-based координатам терминала (1, 1 — верхний левый угол)
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            return f"{ansi_pos}{self.text}"
        return self.text

    def display(self) -> None:
        """Сразу выводит текст в консоль"""
        print(self.flush(), end="", flush=True)

    def __str__(self) -> str:
        return self.flush()

class Catch:
    __slots__ = ("prompt", "compose", "catch_compose", "pos",)

    def __init__(self,
            prompt: str = "> ",
            *,
            compose: StyleType = None, 
            catch_compose: StyleType = None,
            pos: Optional[PosType] = None
    ):
        """
        :param prompt: Prompt text.
        :param compose: Set style for text.
        :param catch_composeХ: (Опционально) Стиль для обработанного результата.
        :param pos: Позиция (x, y) для отрисовки поля ввода.
        """
        self.prompt = str(prompt)
        self.compose = compose
        self.catch_compose = catch_compose
        self.pos = pos

        if self.compose:
            if isinstance(self.compose, ANSIElement):
                self.prompt = f"{self.compose}{self.prompt}{BaseCodes.RESET}"
            elif isinstance(self.compose, (list, tuple)) and all(isinstance(comp, ANSIElement) for comp in self.compose):
                ansi_seq = "".join(self.compose)
                self.prompt = f"{ansi_seq}{self.prompt}{BaseCodes.RESET}"

    def up(self) -> Write:
        """
        Перемещает курсор (если задан pos), активирует style для ввода,
        считывает текст и сбрасывает стили.
        """
        formatted_prompt = self.prompt
        
        # 1. Если заданы координаты, добавляем перемещение курсора
        if self.pos is not None:
            x, y = self.pos
            ansi_pos = move_cursor(max(1, x + 1), max(1, y + 1))
            formatted_prompt = f"{ansi_pos}{self.prompt}"

        # 2. Подготавливаем ANSI-код для стиля ввода
        input_ansi_start = ""
        if self.catch_compose:
            if isinstance(self.catch_compose, ANSIElement):
                input_ansi_start = str(self.catch_compose)
            elif isinstance(self.catch_compose, (list, tuple)) and all(isinstance(s, ANSIElement) for s in self.catch_compose):
                input_ansi_start = "".join(self.catch_compose)

        # 3. Включаем отображение курсора и накладываем стиль на сам ввод
        # Мы печатаем prompt + start_code БЕЗ перехода на новую строку (end="")
        full_prompt = f"{show_cursor()}{formatted_prompt}{input_ansi_start}"

        try:
            # Запрашиваем ввод
            user_input = input(full_prompt)

        finally:
            # Обязательно сбрасываем стили терминала после нажатия Enter, 
            # чтобы последующий вывод в консоли не "поплыл" цветным
            sys.stdout.write(str(BaseCodes.RESET))
            sys.stdout.flush()

        # Возвращаем объект Write, сохраняя в нем catch_compose
        return Write(user_input, compose=self.catch_compose)

    def __call__(self) -> Write:
        return self.up()

def sjoin(text: str, compose: StyleType) -> str:
    return f"{compose}{text}{BaseCodes.RESET}"

def clear() -> None:
    """Clears the terminal screen."""
    print('\x1b[2J\x1b[H')