"""Журнал событий вызова команд в формате XML."""

import xml.etree.ElementTree as etree
from datetime import datetime

ROOT_TAG = "events"


class EventLog:
    """XML-журнал: каждое событие сразу сохраняется в файл."""

    def __init__(self, path):
        """Создать журнал; path=None отключает запись в файл.

        Raises:
            OSError: если лог-файл нельзя создать.
        """
        self.path = path
        self.root = etree.Element(ROOT_TAG)
        if path:
            self._save()

    def add(self, command, args, error=None):
        """Записать событие: время, команда, аргументы, ошибка."""
        event = etree.SubElement(self.root, "event")
        stamp = datetime.now().isoformat(timespec="seconds")
        etree.SubElement(event, "time").text = stamp
        etree.SubElement(event, "command").text = command
        arguments = etree.SubElement(event, "arguments")
        for value in args:
            etree.SubElement(arguments, "arg").text = value
        if error is not None:
            etree.SubElement(event, "error").text = error
        if self.path:
            self._save()

    def _save(self):
        """Записать весь журнал в файл."""
        tree = etree.ElementTree(self.root)
        etree.indent(tree)
        tree.write(self.path, encoding="utf-8", xml_declaration=True)
