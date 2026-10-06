"""Графический интерфейс эмулятора (tkinter)."""

import tkinter as tk
from tkinter import scrolledtext

from src.commands import CommandError, ExitRequest

WINDOW_TITLE = "Эмулятор оболочки [VFS]"
PROMPT = "user@vfs:~$"
ERROR_TAG = "error"
ERROR_COLOR = "#ff6060"
FONT = ("Courier", 11)


class App:
    """Окно эмулятора: область вывода и строка ввода с приглашением."""

    def __init__(self, root, shell):
        """Создать виджеты и привязать обработку Enter."""
        self.root = root
        self.shell = shell
        root.title(WINDOW_TITLE)
        self.output = scrolledtext.ScrolledText(
            root, height=24, width=80, state="disabled",
            bg="black", fg="#d0d0d0", font=FONT)
        self.output.tag_config(ERROR_TAG, foreground=ERROR_COLOR)
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

    def on_enter(self, _event):
        """Выполнить введённую строку и показать результат."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"{PROMPT} {line}\n")
        try:
            result = self.shell.execute(line)
        except ExitRequest:
            self.root.destroy()
            return
        except CommandError as err:
            self.write(f"{err}\n", ERROR_TAG)
            return
        if result:
            self.write(result + "\n")
