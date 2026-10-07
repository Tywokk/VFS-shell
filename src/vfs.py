"""Виртуальная файловая система: хранится и обрабатывается в памяти."""

import base64
import xml.etree.ElementTree as ET

ROOT_TAG = "vfs"
DIR_TAG = "dir"
FILE_TAG = "file"
ENCODING_ATTR = "encoding"
BASE64 = "base64"
INDENT = "  "
SEP = "/"
CURRENT = "."
PARENT = ".."


class VfsError(Exception):
    """Ошибка загрузки или разбора VFS."""


class VFile:
    """Файл: имя и содержимое в байтах."""

    def __init__(self, name, data=b""):
        """Создать файл с именем и содержимым."""
        self.name = name
        self.data = data


class VDir:
    """Каталог: имя и вложенные файлы и каталоги."""

    def __init__(self, name):
        """Создать пустой каталог."""
        self.name = name
        self.children = {}

    def add(self, node):
        """Добавить файл или каталог; имена в каталоге не повторяются."""
        if node.name in self.children:
            raise VfsError(f"повторяющееся имя: {node.name}")
        self.children[node.name] = node


def read_name(element):
    """Взять имя из атрибута name; оно не должно быть пустым."""
    name = element.get("name")
    if not name or "/" in name:
        raise VfsError(f"<{element.tag}>: неверное или пустое имя")
    return name


def parse_file(element):
    """Создать файл из элемента <file> (текст или base64)."""
    name = read_name(element)
    text = element.text or ""
    encoding = element.get(ENCODING_ATTR)
    if encoding is None:
        return VFile(name, text.encode("utf-8"))
    if encoding != BASE64:
        raise VfsError(f"{name}: неизвестная кодировка {encoding}")
    try:
        data = base64.b64decode("".join(text.split()), validate=True)
    except ValueError:
        raise VfsError(f"{name}: неверные данные base64") from None
    return VFile(name, data)


def parse_dir(element, name):
    """Создать каталог из элемента со всем его содержимым."""
    directory = VDir(name)
    for child in element:
        if child.tag == DIR_TAG:
            directory.add(parse_dir(child, read_name(child)))
        elif child.tag == FILE_TAG:
            directory.add(parse_file(child))
        else:
            raise VfsError(f"неизвестный элемент <{child.tag}>")
    return directory


def load_vfs(path):
    """Загрузить VFS из XML-файла в память.

    Файл только читается, на диск ничего не распаковывается.

    Raises:
        VfsError: если файл недоступен или имеет неверный формат.
    """
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as err:
        raise VfsError(f"не удалось прочитать {path}: {err}") from err
    if root.tag != ROOT_TAG:
        raise VfsError(f"корневой элемент должен быть <{ROOT_TAG}>")
    return parse_dir(root, "")


def default_vfs():
    """Создать VFS по умолчанию прямо в памяти."""
    root = VDir("")
    home = VDir("home")
    home.add(VFile("readme.txt", "Добро пожаловать в VFS\n".encode()))
    root.add(home)
    root.add(VFile("hello.txt", b"hello\n"))
    return root


def get_vfs(path):
    """Загрузить VFS из файла или создать по умолчанию, если пути нет."""
    if path is None:
        return default_vfs()
    return load_vfs(path)


def normalize(cwd, path):
    """Вернуть список имён абсолютного пути.

    Args:
        cwd: текущий каталог, список имён от корня.
        path: абсолютный (с /) или относительный путь; поддерживаются
            "." и "..", выше корня подняться нельзя.
    """
    parts = [] if path.startswith(SEP) else list(cwd)
    for name in path.split(SEP):
        if name == PARENT:
            if parts:
                parts.pop()
        elif name and name != CURRENT:
            parts.append(name)
    return parts


def lookup(root, parts):
    """Найти узел по списку имён от корня; None, если его нет."""
    node = root
    for name in parts:
        if not isinstance(node, VDir) or name not in node.children:
            return None
        node = node.children[name]
    return node


def tree_lines(directory, depth=0):
    """Вернуть строки дерева каталога с отступами по уровню."""
    lines = []
    for name in sorted(directory.children):
        node = directory.children[name]
        if isinstance(node, VDir):
            lines.append(INDENT * depth + name + "/")
            lines.extend(tree_lines(node, depth + 1))
        else:
            lines.append(INDENT * depth + name)
    return lines


def count_nodes(directory):
    """Вернуть пару (число вложенных каталогов, число файлов)."""
    dirs = 0
    files = 0
    for node in directory.children.values():
        if isinstance(node, VDir):
            sub_dirs, sub_files = count_nodes(node)
            dirs += 1 + sub_dirs
            files += sub_files
        else:
            files += 1
    return dirs, files


def summary(root):
    """Вернуть строку отладочного вывода о загруженной VFS."""
    dirs, files = count_nodes(root)
    return f"[debug] VFS: каталогов: {dirs}, файлов: {files}"
