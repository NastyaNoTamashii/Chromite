"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

__all__ = ['Write', 'Catch', 'cInject', 'clear']

import sys
from typing import Union, List, Tuple, Optional
from .codes import ANSIElement, move_cursor, show_cursor
from .formatting import BaseCodes

# Тип-хинт для стилей: один элемент или список/кортеж элементов
StyleType = Union[ANSIElement, List[ANSIElement], Tuple[ANSIElement, ...]]

PosType = Tuple[int, int]  # (x, y) или (col, row)

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import tty
    import termios
    WINDOWS = False

def _read_masked_input(mask_char: str) -> str:
    """Считывает ввод с маскировкой символов без стандартного эха терминала."""
    buf = []
    while True:
        if WINDOWS:
            ch = msvcrt.getch()
            if ch in (b"\r", b"\n"):
                print()
                break
            elif ch == b"\x08":  # Backspace
                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch not in (b"\x00", b"\xe0"):
                try:
                    char_str = ch.decode("utf-8")
                    buf.append(char_str)
                    sys.stdout.write(mask_char)
                    sys.stdout.flush()
                except UnicodeDecodeError:
                    pass
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            if ch in ("\r", "\n"):
                print()
                break
            elif ch in ("\x7f", "\x08"):  # Backspace
                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":  # Ctrl+C
                raise KeyboardInterrupt
            else:
                buf.append(ch)
                sys.stdout.write(mask_char)
                sys.stdout.flush()

    return "".join(buf)

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
    __slots__ = ("prompt", "compose", "catch_compose", "pos", "type")

    def __init__(
        self,
        prompt: str = "> ",
        *,
        compose: StyleType = None,
        catch_compose: StyleType = None,
        pos: Optional[PosType] = None,
        type: str = "text",
    ):
        """
        :param prompt: Prompt text.
        :param compose: Set style for prompt text.
        :param catch_compose: Стиль для вводимого текста и возвращаемого Write.
        :param pos: Позиция (x, y) для отрисовки поля ввода.
        :param type: Тип ввода ("text", "password", "pin", "hidden", "int").
        :param mask_char: Символ маскировки при type="password".
        """
        self.prompt = str(prompt)
        self.compose = compose
        self.catch_compose = catch_compose
        self.pos = pos
        self.type = type.lower()

        # Применяем стили к промпту
        if self.compose:
            if isinstance(self.compose, ANSIElement):
                self.prompt = f"{self.compose}{self.prompt}{BaseCodes.RESET}"
            elif isinstance(self.compose, (list, tuple)) and all(isinstance(comp, ANSIElement) for comp in self.compose):
                ansi_seq = "".join(str(comp) for comp in self.compose)
                self.prompt = f"{ansi_seq}{self.prompt}{BaseCodes.RESET}"

    def up(self) -> Write:
        """
        Перемещает курсор (если задан pos), активирует style для ввода,
        считывает текст с учетом type и сбрасывает стили.
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
                input_ansi_start = "".join(str(s) for s in self.catch_compose)

        # 3. Включаем отображение курсора и накладываем стиль на сам ввод
        full_prompt = f"{show_cursor()}{formatted_prompt}{input_ansi_start}"

        try:
            # 4. Обработка ввода в зависимости от type
            if self.type == "password":
                sys.stdout.write(full_prompt)
                sys.stdout.flush()
                user_input = _read_masked_input(mask_char='*')

            elif self.type == "pin":
                sys.stdout.write(full_prompt)
                sys.stdout.flush()
                user_input = _read_masked_input(mask_char='•')

            elif self.type == "hidden":
                sys.stdout.write(full_prompt)
                sys.stdout.flush()
                user_input = _read_masked_input(mask_char="")

            elif self.type in ("int", "number"):
                while True:
                    raw = input(full_prompt)
                    if raw.strip().isdigit():
                        user_input = raw
                        break
                    # Если введено не число — очищаем строку и повторяем
                    sys.stdout.write(f"\033[1A\033[2K")
                    sys.stdout.flush()

            else:
                # Стандартный текстовый ввод
                user_input = input(full_prompt)

        finally:
            # Сбрасываем стили терминала
            sys.stdout.write(str(BaseCodes.RESET))
            sys.stdout.flush()

        # Возвращаем объект Write, сохраняя в нем catch_compose
        return Write(user_input, compose=self.catch_compose)

    def __call__(self) -> Write:
        return self.up()

def cInject(text: str, compose: StyleType) -> str:
    return f"{compose}{text}{BaseCodes.RESET}"

def clear() -> None:
    """Clears the terminal screen."""
    print('\x1b[2J\x1b[H')