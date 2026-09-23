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
