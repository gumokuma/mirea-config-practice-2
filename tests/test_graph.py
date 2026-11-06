"""Проверки обхода графа и подбора версий."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from graph import bfs, read_fixture
from semver import latest

FIXTURE = Path(__file__).parent / "fixtures" / "graph.json"


class GraphTests(unittest.TestCase):
    """Цикл, общая зависимость, глубина и фильтр."""

    def test_bfs(self):
        """Вершины добавляются по уровням и повторно не раскрываются."""
        fixture = read_fixture(FIXTURE)

        def children(node):
            """Преобразовать имена в вершины."""
            return [(name, None) for name in fixture[node[0]]]

        root = ("A", None)
        graph = bfs(root, children)
        self.assertEqual([node[0] for node in graph], list("ABCDE"))
        self.assertEqual(graph[("D", None)], [("B", None)])
        limited = bfs(root, children, max_depth=1, exclude="B")
        self.assertEqual(limited, {root: [("C", None)], ("C", None): []})
        self.assertEqual(bfs(("F", None), children), {("F", None): []})

    def test_semver(self):
        """Учесть числовой порядок, yanked и ограничения версий."""
        versions = ["0.2.1", "0.2.10", "0.2.11", "0.3.0-beta", "0.3.0"]
        records = [
            {"vers": version, "yanked": version == "0.2.11"}
            for version in versions
        ]
        for requirement in ("0.2", "~0.2", "0.2.*", ">=0.2, <0.3"):
            self.assertEqual(latest(records, requirement)["vers"], "0.2.10")
        self.assertEqual(latest(records, "=0.2.1")["vers"], "0.2.1")
