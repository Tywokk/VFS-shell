"""Команды эмулятора: ls, cd, tail, whoami, служебная tree и exit."""

from src.config import USER_NAME
from src.eventlog import EventLog
from src.parser import parse
from src.vfs import (SEP, VDir, default_vfs, lookup, normalize,
                     tree_lines)

LS_OPTIONS = "al"
HIDDEN_PREFIX = "."
DEFAULT_TAIL_LINES = 10
SINGLE = 1
MAX_CD_ARGS = 1
NUL = b"\0"


class CommandError(Exception):
    """Ошибка выполнения команды, текст показывается пользователю."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора."""


def parse_ls_options(args):
    """Разделить аргументы ls на опции (-a, -l) и пути.

    Returns:
        Кортеж (множество опций, список путей).

    Raises:
        CommandError: если встретилась неизвестная опция.
    """
    options = set()
    paths = []
    for arg in args:
        if arg.startswith("-") and arg != "-":
            for char in arg[1:]:
                if char not in LS_OPTIONS:
                    raise CommandError(
                        f"ls: неизвестная опция -- '{char}'")
                options.add(char)
        else:
            paths.append(arg)
    return options, paths


def ls_entry(name, node, long_format):
    """Вернуть строку ls для одной записи (имя или подробную)."""
    if not long_format:
        return name
    if isinstance(node, VDir):
        kind, size = "d", 0
    else:
        kind, size = "-", len(node.data)
    return f"{kind} {size:>6} {name}"


def ls_dir_lines(directory, options):
    """Вернуть строки содержимого каталога с учётом -a и -l."""
    names = sorted(directory.children)
    entries = [(name, directory.children[name]) for name in names]
    if "a" in options:
        entries = [(".", directory), ("..", directory)] + entries
    else:
        entries = [e for e in entries if not e[0].startswith(HIDDEN_PREFIX)]
    return [ls_entry(name, node, "l" in options) for name, node in entries]


def ls_block(shell, path, options, titled):
    """Вернуть вывод ls для одного пути (файла или каталога)."""
    node = shell.find(path)
    if node is None:
        raise CommandError(f"ls: {path}: нет такого файла или каталога")
    if not isinstance(node, VDir):
        return ls_entry(path, node, "l" in options)
    lines = ls_dir_lines(node, options)
    if titled:
        lines.insert(0, f"{path}:")
    return "\n".join(lines)


def cmd_ls(shell, args):
    """ls [-a] [-l] [путь...]: показать содержимое каталога или файл."""
    options, paths = parse_ls_options(args)
    targets = paths or [shell.cwd_path()]
    titled = len(targets) > SINGLE
    blocks = [ls_block(shell, path, options, titled) for path in targets]
    return "\n\n".join(blocks)


def cmd_cd(shell, args):
    """cd [путь]: сменить каталог; без пути - перейти в корень."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: слишком много аргументов")
    path = args[0] if args else SEP
    parts = normalize(shell.cwd, path)
    node = lookup(shell.vfs, parts)
    if node is None:
        raise CommandError(f"cd: {path}: нет такого файла или каталога")
    if not isinstance(node, VDir):
        raise CommandError(f"cd: {path}: не является каталогом")
    shell.cwd = parts
    return ""


def parse_line_count(value):
    """Преобразовать значение опции -n в число строк."""
    if value is None:
        raise CommandError("tail: опция -n требует число")
    if not value.isdecimal():
        raise CommandError(f"tail: неверное число строк: {value}")
    return int(value)


def parse_tail_args(args):
    """Разобрать аргументы tail: число строк и список файлов."""
    count = DEFAULT_TAIL_LINES
    files = []
    items = iter(args)
    for arg in items:
        if arg == "-n":
            count = parse_line_count(next(items, None))
        elif arg.startswith("-") and arg != "-":
            raise CommandError(f"tail: неизвестная опция: {arg}")
        else:
            files.append(arg)
    return count, files


def read_text(path, data):
    """Декодировать содержимое файла в текст UTF-8.

    Raises:
        CommandError: если файл двоичный.
    """
    error = CommandError(f"tail: {path}: двоичный файл")
    if NUL in data:
        raise error
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise error from None


def tail_block(shell, path, count, titled):
    """Вернуть последние count строк файла (с заголовком при titled)."""
    node = shell.find(path)
    if node is None:
        raise CommandError(f"tail: {path}: нет такого файла или каталога")
    if isinstance(node, VDir):
        raise CommandError(f"tail: {path}: это каталог")
    lines = read_text(path, node.data).splitlines()
    text = "\n".join(lines[max(len(lines) - count, 0):])
    return f"==> {path} <==\n{text}" if titled else text


def cmd_tail(shell, args):
    """tail [-n N] файл...: показать последние N строк (по умолчанию 10)."""
    count, files = parse_tail_args(args)
    if not files:
        raise CommandError("tail: не указан файл")
    titled = len(files) > SINGLE
    blocks = [tail_block(shell, path, count, titled) for path in files]
    return "\n\n".join(blocks)


def cmd_whoami(shell, args):
    """whoami: вывести имя текущего пользователя."""
    if args:
        raise CommandError("whoami: слишком много аргументов")
    return USER_NAME


def cmd_tree(shell, args):
    """Служебная команда tree: показать всё содержимое VFS."""
    if args:
        raise CommandError("tree: слишком много аргументов")
    return "\n".join([SEP] + tree_lines(shell.vfs))


def cmd_exit(shell, args):
    """Завершить работу эмулятора (аргументы не принимаются)."""
    if args:
        raise CommandError("exit: слишком много аргументов")
    raise ExitRequest()


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "tail": cmd_tail,
    "whoami": cmd_whoami,
    "tree": cmd_tree,
    "exit": cmd_exit,
}


class Shell:
    """Интерпретатор: выполняет команды и записывает их в журнал."""

    def __init__(self, log=None, vfs=None):
        """Создать оболочку; log - журнал, vfs - файловая система."""
        self.log = log or EventLog(None)
        self.vfs = vfs or default_vfs()
        self.cwd = []

    def cwd_path(self):
        """Вернуть текущий каталог строкой (корень - это /)."""
        return SEP + SEP.join(self.cwd)

    def find(self, path):
        """Найти узел VFS по пути (от корня или от текущего каталога)."""
        return lookup(self.vfs, normalize(self.cwd, path))

    def execute(self, line):
        """Выполнить строку ввода и вернуть текст вывода.

        Каждая вызванная команда записывается в журнал.

        Raises:
            CommandError: если команда неизвестна или завершилась ошибкой.
            ExitRequest: если введена команда exit.
        """
        name, args = parse(line)
        if not name:
            return ""
        try:
            output = self._call(name, args)
        except ExitRequest:
            self.log.add(name, args)
            raise
        except CommandError as err:
            self.log.add(name, args, str(err))
            raise
        self.log.add(name, args)
        return output

    def _call(self, name, args):
        """Найти команду по имени и вызвать её."""
        handler = COMMANDS.get(name)
        if handler is None:
            raise CommandError(f"{name}: команда не найдена")
        return handler(self, args)
