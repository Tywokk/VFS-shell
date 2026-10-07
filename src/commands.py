"""Команды эмулятора: заглушки ls, cd и команда exit."""

from src.eventlog import EventLog
from src.parser import parse


class CommandError(Exception):
    """Ошибка выполнения команды, текст показывается пользователю."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора."""


def _stub(name, args):
    """Сформировать вывод заглушки: имя команды и аргументы."""
    shown = " ".join(args) if args else "(нет)"
    return f"{name}: заглушка, аргументы: {shown}"


def cmd_ls(args):
    """Заглушка команды ls."""
    return _stub("ls", args)


def cmd_cd(args):
    """Заглушка команды cd."""
    return _stub("cd", args)


def cmd_exit(args):
    """Завершить работу эмулятора (аргументы не принимаются)."""
    if args:
        raise CommandError("exit: слишком много аргументов")
    raise ExitRequest()


class Shell:
    """Интерпретатор: выполняет команды и записывает их в журнал."""

    def __init__(self, log=None):
        """Зарегистрировать команды; log - журнал событий."""
        self.log = log or EventLog(None)
        self.commands = {"ls": cmd_ls, "cd": cmd_cd, "exit": cmd_exit}

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
        handler = self.commands.get(name)
        if handler is None:
            raise CommandError(f"{name}: команда не найдена")
        return handler(args)
