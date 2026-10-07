"""Права доступа: режимы chmod и запись в виде rwxr-xr-x."""

import re

FILE_MODE = 0o644
DIR_MODE = 0o755
ALL_PERMS = 0o7
PERM_LETTERS = "rwxrwxrwx"
OCTAL_DIGITS = "01234567"
MAX_OCTAL_DIGITS = 3
SHIFTS = {"u": 6, "g": 3, "o": 0}
PERM_BITS = {"r": 4, "w": 2, "x": 1}
SYMBOLIC = re.compile(r"([ugoa]*)([-+=])([rwx]+)")


def mode_string(mode):
    """Вернуть права в виде rwxr-xr-x по числу, например 0o755."""
    text = ""
    last = len(PERM_LETTERS) - 1
    for position, letter in enumerate(PERM_LETTERS):
        bit = 1 << (last - position)
        text += letter if mode & bit else "-"
    return text


def octal_mode(text):
    """Преобразовать восьмеричную запись (755) в число; None, если неверна."""
    if len(text) > MAX_OCTAL_DIGITS:
        return None
    if any(char not in OCTAL_DIGITS for char in text):
        return None
    return int(text, 8)


def symbolic_mode(text, current):
    """Применить символьный режим (u+x, go-w, a=r) к текущим правам.

    Без указания, для кого (+x), режим применяется ко всем.
    Возвращает None, если запись неверна.
    """
    match = SYMBOLIC.fullmatch(text)
    if match is None:
        return None
    who, operation, perms = match.groups()
    targets = "ugo" if not who or "a" in who else who
    bits = 0
    mask = 0
    for target in targets:
        mask |= ALL_PERMS << SHIFTS[target]
        for perm in perms:
            bits |= PERM_BITS[perm] << SHIFTS[target]
    if operation == "+":
        return current | bits
    if operation == "-":
        return current & ~bits
    return (current & ~mask) | bits


def apply_mode(text, current):
    """Вернуть новые права по режиму chmod; None, если режим неверный.

    Режим - число из 1-3 восьмеричных цифр (755) или символьная запись.
    """
    if text.isdecimal():
        return octal_mode(text)
    return symbolic_mode(text, current)
