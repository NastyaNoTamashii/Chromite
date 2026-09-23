"""

    Copyright (C) 2026 NastyaNoTamashii.

"""

import os

# Инициализируем поддержку ANSI в Windows-консолях
os.system("")

CSI = "\033["

class ANSIElement(str):
    """
    Custom string for ANSI codes.
    """
    pass

def make_ansi(code: int) -> ANSIElement:
    return ANSIElement(f"{CSI}{code}m")

# --- Новые функции для работы с курсором ---

def move_cursor(x: int, y: int) -> ANSIElement:
    """Перемещает курсор на позицию (x, y) / (col, row). Нумерация с 1,1."""
    return ANSIElement(f"{CSI}{y};{x}H")

def hide_cursor() -> ANSIElement:
    """Скрывает курсор"""
    return ANSIElement(f"{CSI}?25l")

def show_cursor() -> ANSIElement:
    """Показывает курсор"""
    return ANSIElement(f"{CSI}?25h")

def save_cursor() -> ANSIElement:
    """Сохраняет текущую позицию курсора"""
    return ANSIElement(f"{CSI}s")

def restore_cursor() -> ANSIElement:
    """Восстанавливает сохраненную позицию курсора"""
    return ANSIElement(f"{CSI}u")