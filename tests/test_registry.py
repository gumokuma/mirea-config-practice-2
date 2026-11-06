"""Проверка чтения формата sparse registry без доступа к сети."""
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from registry import Registry, dependency_name, index_path


class RegistryTests(unittest.TestCase):
    """Точные версии, пути индекса и переименования."""

    def test_index_paths(self):
        """Проверить все уровни адресации."""
        cases = {"A": "1/a", "AB": "2/ab", "Log": "3/l/log",
                 "Serde": "se/rd/serde"}
        for name, path in cases.items():
            self.assertEqual(index_path(name), path)

    def test_exact_version(self):
        """Из двух строк выбрать указанную версию."""
        data = (
            b'{"name":"log","vers":"0.4.21","deps":[]}\n'
            b'{"name":"log","vers":"0.4.22","deps":'
            b'[{"name":"alias","package":"other","req":"1"}]}\n'
        )
        registry = Registry("sparse+https://example.test/index/")
        with patch("registry.urlopen", return_value=io.BytesIO(data)) as get:
            record = registry.exact("log", "0.4.22")
            self.assertEqual(dependency_name(record["deps"][0]), "other")
            with self.assertRaisesRegex(ValueError, "version not found"):
                registry.exact("log", "0.4.23")
        get.assert_called_once_with(
            "https://example.test/index/3/l/log", timeout=15,
        )
