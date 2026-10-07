"""Тесты интерпретатора и команд-заглушек."""

import unittest

from src.commands import CommandError, ExitRequest, Shell
from src.eventlog import EventLog


def first_event(log):
    """Вернуть первое событие журнала."""
    return log.root.find("event")


class ShellTest(unittest.TestCase):
    """Проверки выполнения команд."""

    def test_ls_stub_prints_name_and_args(self):
        """ls выводит своё имя и аргументы."""
        out = Shell().execute("ls -l /tmp")
        self.assertIn("ls", out)
        self.assertIn("-l /tmp", out)

    def test_cd_stub_without_args(self):
        """cd без аргументов тоже работает."""
        self.assertIn("cd", Shell().execute("cd"))

    def test_empty_line(self):
        """Пустая строка ничего не выводит."""
        self.assertEqual(Shell().execute(""), "")

    def test_unknown_command(self):
        """Неизвестная команда - ошибка."""
        with self.assertRaises(CommandError):
            Shell().execute("foo bar")

    def test_exit(self):
        """exit запрашивает завершение."""
        with self.assertRaises(ExitRequest):
            Shell().execute("exit")

    def test_exit_with_args_is_error(self):
        """exit с аргументами - ошибка."""
        with self.assertRaises(CommandError):
            Shell().execute("exit 1")


class ShellLogTest(unittest.TestCase):
    """Проверки записи команд в журнал."""

    def test_success_is_logged(self):
        """Успешная команда пишется в журнал без ошибки."""
        log = EventLog(None)
        Shell(log).execute("ls -l")
        event = first_event(log)
        self.assertEqual(event.findtext("command"), "ls")
        self.assertIsNone(event.find("error"))

    def test_error_is_logged(self):
        """Ошибка команды пишется в журнал с текстом."""
        log = EventLog(None)
        with self.assertRaises(CommandError):
            Shell(log).execute("foo")
        self.assertIn("не найдена", first_event(log).findtext("error"))

    def test_exit_is_logged(self):
        """Команда exit тоже пишется в журнал."""
        log = EventLog(None)
        with self.assertRaises(ExitRequest):
            Shell(log).execute("exit")
        self.assertEqual(first_event(log).findtext("command"), "exit")

    def test_empty_line_not_logged(self):
        """Пустая строка в журнал не попадает."""
        log = EventLog(None)
        Shell(log).execute("   ")
        self.assertIsNone(first_event(log))
