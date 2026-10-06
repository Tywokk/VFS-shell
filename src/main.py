"""Точка входа: запуск графического эмулятора."""

import tkinter as tk

from src.commands import Shell
from src.gui import App


def main():
    """Создать окно, подключить интерпретатор и запустить цикл событий."""
    root = tk.Tk()
    App(root, Shell())
    root.mainloop()


if __name__ == "__main__":
    main()
