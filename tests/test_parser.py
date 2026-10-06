"""Тесты парсера ввода."""

import unittest

from src.parser import parse


class ParseTest(unittest.TestCase):
    """Проверки разбора строки на команду и аргументы."""

    def test_command_with_args(self):
        """Команда и аргументы делятся по пробелам."""
        self.assertEqual(parse("ls -l /home"), ("ls", ["-l", "/home"]))

    def test_extra_spaces(self):
        """Лишние пробелы игнорируются."""
        self.assertEqual(parse("  cd   a  "), ("cd", ["a"]))

    def test_empty(self):
        """Пустой ввод даёт пустую команду."""
        self.assertEqual(parse("   "), ("", []))
