"""Тесты параметров командной строки."""

import unittest

from src.config import UNSET, debug_lines, parse_args, vfs_name


class ConfigTest(unittest.TestCase):
    """Проверки разбора параметров и отладочного вывода."""

    def test_all_params(self):
        """Все три параметра читаются из командной строки."""
        args = parse_args(
            ["--vfs", "a.xml", "--log", "l.xml", "--script", "s.emu"])
        self.assertEqual(args.vfs, "a.xml")
        self.assertEqual(args.log, "l.xml")
        self.assertEqual(args.script, "s.emu")

    def test_defaults(self):
        """Без параметров везде None."""
        args = parse_args([])
        self.assertIsNone(args.vfs)
        self.assertIsNone(args.log)
        self.assertIsNone(args.script)

    def test_unknown_param_exits(self):
        """Неизвестный параметр - завершение с ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--bogus"])

    def test_debug_lines(self):
        """Отладочный вывод содержит все три параметра."""
        lines = debug_lines(parse_args(["--vfs", "v.xml"]))
        self.assertIn("v.xml", lines[0])
        self.assertIn(UNSET, lines[1])
        self.assertIn(UNSET, lines[2])

    def test_vfs_name(self):
        """Имя VFS берётся из пути или равно default."""
        self.assertEqual(vfs_name("x/y.xml"), "y.xml")
        self.assertEqual(vfs_name(None), "default")
