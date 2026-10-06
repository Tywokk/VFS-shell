"""Тесты интерпретатора и команд-заглушек."""

import unittest

from src.commands import CommandError, ExitRequest, Shell


class ShellTest(unittest.TestCase):
    """Проверки выполнения команд."""

    def setUp(self):
        """Создать новый интерпретатор для каждого теста."""
        self.shell = Shell()

    def test_ls_stub_prints_name_and_args(self):
        """ls выводит своё имя и аргументы."""
        out = self.shell.execute("ls -l /tmp")
        self.assertIn("ls", out)
        self.assertIn("-l /tmp", out)

    def test_cd_stub_without_args(self):
        """cd без аргументов тоже работает."""
        self.assertIn("cd", self.shell.execute("cd"))

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        self.assertEqual(self.shell.execute(""), "")

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        with self.assertRaises(CommandError):
            self.shell.execute("foo bar")

    def test_exit(self):
        """exit запрашивает завершение."""
        with self.assertRaises(ExitRequest):
            self.shell.execute("exit")

    def test_exit_with_args_is_error(self):
        """exit с аргументами — ошибка."""
        with self.assertRaises(CommandError):
            self.shell.execute("exit 1")
