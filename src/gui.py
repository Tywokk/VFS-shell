"""Графический интерфейс эмулятора (tkinter)."""

import tkinter as tk
from tkinter import scrolledtext

from src.commands import CommandError, ExitRequest
from src.config import debug_lines, vfs_name

TITLE_TEMPLATE = "Эмулятор оболочки [VFS: {}]"
PROMPT = "user@vfs:~$"
COMMENT = "#"
STATUS_OK = "ok"
STATUS_ERROR = "error"
STATUS_EXIT = "exit"
ERROR_TAG = "error"
ERROR_COLOR = "#ff6060"
DEBUG_TAG = "debug"
DEBUG_COLOR = "#7fb0ff"
FONT = ("Courier", 11)


class App:
    """Окно эмулятора: область вывода и строка ввода с приглашением."""

    def __init__(self, root, shell, args):
        """Создать виджеты и привязать обработку Enter."""
        self.root = root
        self.shell = shell
        self.args = args
        root.title(TITLE_TEMPLATE.format(vfs_name(args.vfs)))
        self.output = scrolledtext.ScrolledText(
            root, height=24, width=80, state="disabled",
            bg="black", fg="#d0d0d0", font=FONT)
        self.output.tag_config(ERROR_TAG, foreground=ERROR_COLOR)
        self.output.tag_config(DEBUG_TAG, foreground=DEBUG_COLOR)
        self.output.pack(fill="both", expand=True)
        self._build_input_row()

    def _build_input_row(self):
        """Создать строку ввода с приглашением."""
        row = tk.Frame(self.root)
        row.pack(fill="x")
        tk.Label(row, text=PROMPT, font=FONT).pack(side="left")
        self.entry = tk.Entry(row, font=FONT)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus()

    def write(self, text, tag=None):
        """Добавить текст в конец области вывода."""
        self.output.config(state="normal")
        self.output.insert("end", text, tag)
        self.output.see("end")
        self.output.config(state="disabled")

    def show_debug(self):
        """Вывести все заданные параметры в окно и в консоль."""
        for line in debug_lines(self.args):
            print(line, flush=True)
            self.write(line + "\n", DEBUG_TAG)

    def run_command(self, line):
        """Показать и выполнить строку, вернуть статус выполнения."""
        self.write(f"{PROMPT} {line}\n")
        try:
            result = self.shell.execute(line)
        except ExitRequest:
            self.root.destroy()
            return STATUS_EXIT
        except CommandError as err:
            self.write(f"{err}\n", ERROR_TAG)
            return STATUS_ERROR
        if result:
            self.write(result + "\n")
        return STATUS_OK

    def on_enter(self, _event):
        """Выполнить строку, введённую пользователем."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.run_command(line)

    def run_script_file(self, path):
        """Прочитать стартовый скрипт из файла и выполнить его."""
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except (OSError, UnicodeDecodeError) as err:
            self.write(f"Не удалось прочитать скрипт: {err}\n", ERROR_TAG)
            return
        self.run_script(lines)

    def run_script(self, lines):
        """Выполнить строки скрипта; остановиться на первой ошибке."""
        for number, raw in enumerate(lines, start=1):
            line = raw.strip()
            if not line or line.startswith(COMMENT):
                continue
            status = self.run_command(line)
            if status == STATUS_ERROR:
                self.write(
                    f"Скрипт остановлен: ошибка в строке {number}\n",
                    ERROR_TAG)
            if status != STATUS_OK:
                return
