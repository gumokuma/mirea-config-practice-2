"""Проверки порядка загрузки."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from output import load_order


class OutputTests(unittest.TestCase):
    """Проверки представлений графа."""

    def test_order(self):
        """Общие зависимости предшествуют своим родителям."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(load_order(graph), (list("DBCA"), []))

    def test_blocked_order(self):
        """Цикл блокирует собственные вершины и их родителей."""
        graph = {"A": ["B", "C"], "B": ["B"], "C": []}
        self.assertEqual(load_order(graph), (["C"], ["A", "B"]))
