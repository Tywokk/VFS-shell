"""Тесты разбора режимов chmod и записи прав."""

import unittest

from src.modes import apply_mode, mode_string

FULL = 0o777


class ModeStringTest(unittest.TestCase):
    """Проверки записи прав в виде rwxr-xr-x."""

    def test_typical(self):
        """Типичные права записываются привычным образом."""
        self.assertEqual(mode_string(0o755), "rwxr-xr-x")
        self.assertEqual(mode_string(0o644), "rw-r--r--")

    def test_edges(self):
        """Нет прав и все права."""
        self.assertEqual(mode_string(0), "---------")
        self.assertEqual(mode_string(FULL), "rwxrwxrwx")


class ApplyModeTest(unittest.TestCase):
    """Проверки разбора режимов."""

    def test_octal(self):
        """Восьмеричные режимы длиной от одной до трёх цифр."""
        self.assertEqual(apply_mode("755", 0), 0o755)
        self.assertEqual(apply_mode("7", FULL), 0o7)

    def test_bad_octal(self):
        """Неверные цифры и слишком длинная запись."""
        self.assertIsNone(apply_mode("888", 0))
        self.assertIsNone(apply_mode("1234", 0))

    def test_plus(self):
        """+ добавляет права."""
        self.assertEqual(apply_mode("u+x", 0o644), 0o744)
        self.assertEqual(apply_mode("+x", 0o644), 0o755)

    def test_minus(self):
        """- убирает права."""
        self.assertEqual(apply_mode("go-r", 0o644), 0o600)

    def test_equals(self):
        """= заменяет права выбранных категорий."""
        self.assertEqual(apply_mode("a=r", 0o755), 0o444)
        self.assertEqual(apply_mode("g=rw", 0o755), 0o765)

    def test_several_targets(self):
        """Можно указать несколько категорий и прав сразу."""
        self.assertEqual(apply_mode("ug+rwx", 0), 0o770)

    def test_bad_symbolic(self):
        """Неверные записи дают None."""
        for text in ("u+q", "x", "u+", "u+x,g+r", ""):
            self.assertIsNone(apply_mode(text, 0))
