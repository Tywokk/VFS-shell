"""Точка входа: запуск графического эмулятора."""

import sys
import tkinter as tk

from src.commands import Shell
from src.config import parse_args
from src.eventlog import EventLog
from src.gui import App


def open_log(path):
    """Создать журнал событий; при ошибке завершить программу."""
    try:
        return EventLog(path)
    except OSError as err:
        sys.exit(f"Не удалось создать лог-файл: {err}")


def main(argv=None):
    """Разобрать параметры, создать окно и запустить цикл событий."""
    args = parse_args(argv)
    log = open_log(args.log)
    root = tk.Tk()
    app = App(root, Shell(log), args)
    app.show_debug()
    if args.script:
        root.after(0, app.run_script_file, args.script)
    root.mainloop()


if __name__ == "__main__":
    main()
