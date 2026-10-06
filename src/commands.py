"""Команды эмулятора: заглушки ls, cd и команда exit."""

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
    """Интерпретатор: разбирает строку и вызывает нужную команду."""

    def __init__(self):
        """Зарегистрировать доступные команды."""
        self.commands = {"ls": cmd_ls, "cd": cmd_cd, "exit": cmd_exit}

    def execute(self, line):
        """Выполнить строку ввода и вернуть текст вывода.

        Raises:
            CommandError: если команда неизвестна или завершилась ошибкой.
            ExitRequest: если введена команда exit.
        """
        name, args = parse(line)
        if not name:
            return ""
        handler = self.commands.get(name)
        if handler is None:
            raise CommandError(f"{name}: команда не найдена")
        return handler(args)
