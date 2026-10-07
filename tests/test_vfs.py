"""Тесты виртуальной файловой системы."""

import os
import tempfile
import unittest

from src.vfs import (VDir, VFile, VfsError, count_nodes, default_vfs,
                     get_vfs, load_vfs, summary, tree_lines)

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "vfs")


def sample(name):
    """Вернуть путь к примеру VFS из папки vfs."""
    return os.path.join(SAMPLES, name)


def load_text(text):
    """Записать XML во временный файл и загрузить его как VFS."""
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "vfs.xml")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return load_vfs(path)


class LoadTest(unittest.TestCase):
    """Проверки загрузки VFS из XML."""

    def test_text_file(self):
        """Текстовый файл хранится в байтах UTF-8."""
        root = load_text('<vfs><file name="a.txt">Привет</file></vfs>')
        self.assertEqual(root.children["a.txt"].data, "Привет".encode())

    def test_base64_file(self):
        """Двоичные данные декодируются из base64."""
        xml = '<vfs><file name="b" encoding="base64">AAECA/8=</file></vfs>'
        root = load_text(xml)
        self.assertEqual(root.children["b"].data, bytes([0, 1, 2, 3, 255]))

    def test_nested_dirs(self):
        """Вложенные каталоги загружаются рекурсивно."""
        xml = ('<vfs><dir name="a"><dir name="b">'
               '<file name="c"/></dir></dir></vfs>')
        root = load_text(xml)
        self.assertIn("c", root.children["a"].children["b"].children)

    def test_wrong_root(self):
        """Неверный корневой элемент - ошибка."""
        with self.assertRaises(VfsError):
            load_text("<root/>")

    def test_unknown_element(self):
        """Неизвестный элемент - ошибка."""
        with self.assertRaises(VfsError):
            load_text("<vfs><link/></vfs>")

    def test_duplicate_names(self):
        """Повторяющиеся имена в каталоге - ошибка."""
        with self.assertRaises(VfsError):
            load_text('<vfs><file name="a"/><file name="a"/></vfs>')

    def test_missing_name(self):
        """Файл без имени - ошибка."""
        with self.assertRaises(VfsError):
            load_text("<vfs><file/></vfs>")

    def test_bad_base64(self):
        """Неверный base64 - ошибка."""
        with self.assertRaises(VfsError):
            load_text('<vfs><file name="a" encoding="base64">!</file></vfs>')

    def test_unknown_encoding(self):
        """Неизвестная кодировка - ошибка."""
        with self.assertRaises(VfsError):
            load_text('<vfs><file name="a" encoding="hex">0</file></vfs>')

    def test_broken_xml(self):
        """Некорректный XML - ошибка."""
        with self.assertRaises(VfsError):
            load_text("<vfs><file")

    def test_missing_file(self):
        """Несуществующий файл - ошибка."""
        with self.assertRaises(VfsError):
            load_vfs(sample("no_such_file.xml"))


class SamplesTest(unittest.TestCase):
    """Проверки примеров VFS из репозитория."""

    def test_minimal(self):
        """Минимальная VFS: один файл."""
        self.assertEqual(count_nodes(load_vfs(sample("minimal.xml"))), (0, 1))

    def test_several_files(self):
        """Несколько файлов в корне."""
        root = load_vfs(sample("several_files.xml"))
        self.assertEqual(count_nodes(root), (0, 4))

    def test_deep(self):
        """Вложенность не меньше трёх уровней."""
        root = load_vfs(sample("deep.xml"))
        self.assertEqual(count_nodes(root), (5, 5))
        old = root.children["home"].children["user"].children["docs"]
        self.assertIn("draft.txt", old.children["old"].children)

    def test_broken_sample(self):
        """Некорректный пример даёт VfsError."""
        with self.assertRaises(VfsError):
            load_vfs(sample("broken.xml"))


class DefaultAndTreeTest(unittest.TestCase):
    """Проверки VFS по умолчанию и вывода дерева."""

    def test_default_without_path(self):
        """Без пути создаётся VFS по умолчанию."""
        self.assertEqual(count_nodes(get_vfs(None)), (1, 2))

    def test_default_content(self):
        """В VFS по умолчанию есть файл hello.txt."""
        self.assertIsInstance(default_vfs().children["hello.txt"], VFile)

    def test_tree_lines(self):
        """Дерево: каталоги со слэшем, вложенное с отступом."""
        root = VDir("")
        home = VDir("home")
        home.add(VFile("a.txt"))
        root.add(home)
        root.add(VFile("b.txt"))
        self.assertEqual(tree_lines(root), ["b.txt", "home/", "  a.txt"])

    def test_summary(self):
        """Строка отладочного вывода содержит числа."""
        text = summary(default_vfs())
        self.assertIn("каталогов: 1, файлов: 2", text)
