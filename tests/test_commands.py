"""Тесты команд ls, cd, tail и whoami."""

import os
import unittest

from src.commands import CommandError, Shell
from src.vfs import load_vfs

DEMO = os.path.join(os.path.dirname(__file__), "..", "vfs", "demo.xml")


def make_shell():
    """Создать оболочку с демонстрационной VFS (vfs/demo.xml)."""
    return Shell(vfs=load_vfs(DEMO))


def error_of(line, shell=None):
    """Выполнить команду, которая должна упасть, и вернуть текст ошибки."""
    try:
        (shell or make_shell()).execute(line)
    except CommandError as err:
        return str(err)
    raise AssertionError(f"ожидалась ошибка: {line}")


class LsTest(unittest.TestCase):
    """Проверки команды ls."""

    def test_root(self):
        """Без аргументов показывается текущий каталог без скрытых."""
        out = make_shell().execute("ls")
        self.assertEqual(out, "data.bin\nhome\nreadme.txt")

    def test_all(self):
        """Ключ -a добавляет скрытые файлы, . и .."""
        out = make_shell().execute("ls -a").split("\n")
        self.assertEqual(out[:3], [".", "..", ".hidden"])

    def test_long(self):
        """Ключ -l показывает тип и размер."""
        out = make_shell().execute("ls -l")
        self.assertIn("d      0 home", out)
        self.assertIn("-      5 data.bin", out)

    def test_combined_options(self):
        """Ключи можно писать слитно и по отдельности."""
        shell = make_shell()
        self.assertEqual(shell.execute("ls -la"), shell.execute("ls -a -l"))

    def test_path(self):
        """ls с путём показывает указанный каталог."""
        self.assertEqual(make_shell().execute("ls home"), "user")

    def test_several_paths(self):
        """Для нескольких путей выводятся заголовки."""
        out = make_shell().execute("ls home home/user/docs")
        self.assertEqual(out, "home:\nuser\n\nhome/user/docs:\nreport.txt")

    def test_file(self):
        """ls для файла печатает его имя."""
        self.assertEqual(make_shell().execute("ls readme.txt"), "readme.txt")

    def test_empty_dir(self):
        """Пустой каталог ничего не выводит."""
        self.assertEqual(make_shell().execute("ls home/user/empty"), "")

    def test_uses_current_dir(self):
        """После cd ls показывает новый каталог."""
        shell = make_shell()
        shell.execute("cd home/user")
        self.assertIn("lines.txt", shell.execute("ls"))

    def test_unknown_option(self):
        """Неизвестная опция - ошибка."""
        self.assertIn("неизвестная опция", error_of("ls -x"))

    def test_missing_path(self):
        """Несуществующий путь - ошибка."""
        self.assertEqual(error_of("ls nope"),
                         "ls: nope: нет такого файла или каталога")


class CdTest(unittest.TestCase):
    """Проверки команды cd."""

    def test_absolute(self):
        """Переход по абсолютному пути."""
        shell = make_shell()
        shell.execute("cd /home/user")
        self.assertEqual(shell.cwd_path(), "/home/user")

    def test_relative_and_parent(self):
        """Относительные пути, .. и ."""
        shell = make_shell()
        shell.execute("cd home/user/docs")
        shell.execute("cd .")
        self.assertEqual(shell.cwd_path(), "/home/user/docs")
        shell.execute("cd ../..")
        self.assertEqual(shell.cwd_path(), "/home")

    def test_parent_of_root(self):
        """cd .. в корне остаётся в корне."""
        shell = make_shell()
        shell.execute("cd ..")
        self.assertEqual(shell.cwd_path(), "/")

    def test_no_args(self):
        """cd без аргументов - переход в корень."""
        shell = make_shell()
        shell.execute("cd home")
        shell.execute("cd")
        self.assertEqual(shell.cwd_path(), "/")

    def test_missing_dir(self):
        """Несуществующий каталог - ошибка, каталог не меняется."""
        shell = make_shell()
        self.assertIn("нет такого", error_of("cd nope", shell))
        self.assertEqual(shell.cwd_path(), "/")

    def test_file(self):
        """cd в файл - ошибка."""
        self.assertIn("не является каталогом", error_of("cd readme.txt"))

    def test_too_many_args(self):
        """Больше одного аргумента - ошибка."""
        self.assertIn("слишком много", error_of("cd home home"))


class TailTest(unittest.TestCase):
    """Проверки команды tail."""

    def setUp(self):
        """Перейти в каталог с тестовыми файлами."""
        self.shell = make_shell()
        self.shell.execute("cd /home/user")

    def lines(self, command):
        """Выполнить команду и вернуть вывод списком строк."""
        return self.shell.execute(command).split("\n")

    def test_default_ten_lines(self):
        """По умолчанию выводятся последние 10 строк."""
        out = self.lines("tail lines.txt")
        self.assertEqual(out[0], "строка 3")
        self.assertEqual(out[-1], "строка 12")
        self.assertEqual(len(out), 10)

    def test_option_n(self):
        """-n задаёт число строк."""
        self.assertEqual(self.lines("tail -n 2 lines.txt"),
                         ["строка 11", "строка 12"])

    def test_zero_lines(self):
        """-n 0 ничего не выводит."""
        self.assertEqual(self.shell.execute("tail -n 0 lines.txt"), "")

    def test_more_than_file(self):
        """Если строк меньше, выводится весь файл."""
        out = self.lines("tail -n 100 short.txt")
        self.assertEqual(out, ["первая", "вторая", "третья"])

    def test_several_files(self):
        """Для нескольких файлов выводятся заголовки."""
        out = self.shell.execute("tail -n 1 short.txt docs/report.txt")
        expected = ("==> short.txt <==\nтретья\n\n"
                    "==> docs/report.txt <==\nОтчёт")
        self.assertEqual(out, expected)

    def test_absolute_path(self):
        """Файл можно указать абсолютным путём."""
        self.assertIn("Демонстрационная", self.shell.execute(
            "tail /readme.txt"))

    def test_no_file(self):
        """Без файла - ошибка."""
        self.assertIn("не указан файл", error_of("tail", self.shell))

    def test_missing_file(self):
        """Несуществующий файл - ошибка."""
        self.assertEqual(error_of("tail nope", self.shell),
                         "tail: nope: нет такого файла или каталога")

    def test_directory(self):
        """Каталог вместо файла - ошибка."""
        self.assertIn("это каталог", error_of("tail docs", self.shell))

    def test_binary_file(self):
        """Двоичный файл - ошибка."""
        self.assertIn("двоичный файл", error_of("tail /data.bin", self.shell))

    def test_bad_count(self):
        """Неверное значение -n - ошибка."""
        for line in ("tail -n abc lines.txt", "tail -n -1 lines.txt"):
            self.assertIn("неверное число", error_of(line, self.shell))

    def test_count_missing(self):
        """-n без значения - ошибка."""
        self.assertIn("требует число", error_of("tail -n", self.shell))

    def test_unknown_option(self):
        """Неизвестная опция - ошибка."""
        self.assertIn("неизвестная опция",
                      error_of("tail -x lines.txt", self.shell))


class WhoamiTest(unittest.TestCase):
    """Проверки команды whoami."""

    def test_name(self):
        """whoami печатает имя пользователя из приглашения."""
        self.assertEqual(make_shell().execute("whoami"), "user")

    def test_with_args_is_error(self):
        """whoami с аргументами - ошибка."""
        self.assertIn("слишком много", error_of("whoami x"))
