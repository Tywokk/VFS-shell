"""Тесты XML-журнала."""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

from src.eventlog import EventLog


def read_event(path):
    """Прочитать первое событие из XML-лога."""
    return ET.parse(path).getroot().find("event")


class EventLogTest(unittest.TestCase):
    """Проверки записи событий."""

    def test_event_fields(self):
        """Событие содержит время, команду, аргументы и ошибку."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "log.xml")
            EventLog(path).add("cd", ["a", "b"], "boom")
            event = read_event(path)
        self.assertTrue(event.findtext("time"))
        self.assertEqual(event.findtext("command"), "cd")
        args = [a.text for a in event.find("arguments")]
        self.assertEqual(args, ["a", "b"])
        self.assertEqual(event.findtext("error"), "boom")

    def test_no_error_element(self):
        """Без ошибки элемента error нет."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "log.xml")
            EventLog(path).add("ls", [])
            event = read_event(path)
        self.assertIsNone(event.find("error"))

    def test_disabled_log(self):
        """Без пути файл не создаётся, ошибок нет."""
        with tempfile.TemporaryDirectory() as folder:
            EventLog(None).add("ls", [])
            self.assertEqual(os.listdir(folder), [])

    def test_bad_path(self):
        """Недоступный путь даёт OSError."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "no", "log.xml")
            with self.assertRaises(OSError):
                EventLog(path)
