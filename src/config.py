"""Параметры командной строки эмулятора."""

import argparse
import os

UNSET = "(не задан)"
DEFAULT_VFS_NAME = "default"


def parse_args(argv=None):
    """Разобрать параметры командной строки.

    Возвращает объект с полями vfs, log и script.
    Если параметр не указан, в поле лежит None.
    """
    parser = argparse.ArgumentParser(
        prog="emulator", description="Эмулятор оболочки UNIX с VFS")
    parser.add_argument("--vfs", help="путь к физическому расположению VFS")
    parser.add_argument("--log", help="путь к лог-файлу (XML)")
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args(argv)


def debug_lines(args):
    """Вернуть строки отладочного вывода всех параметров."""
    return [
        f"[debug] vfs    = {args.vfs or UNSET}",
        f"[debug] log    = {args.log or UNSET}",
        f"[debug] script = {args.script or UNSET}",
    ]


def vfs_name(path):
    """Вернуть имя VFS для заголовка окна."""
    if path:
        return os.path.basename(path)
    return DEFAULT_VFS_NAME
