"""Проверки порядка загрузки."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from output import ascii_tree, load_order, plantuml


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

    def test_visualizations(self):
        """PlantUML сохраняет обратное ребро, а дерево завершает обход."""
        a, b = ("A", None), ("B", None)
        graph = {a: [b], b: [a]}
        diagram = plantuml(graph)
        self.assertIn('component "A" as p0', diagram)
        self.assertIn("p1 --> p0", diagram)
        self.assertTrue(diagram.endswith("@enduml"))
        self.assertIn("A [seen]", ascii_tree(graph))
