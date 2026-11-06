"""Построение графа зависимостей итеративным BFS."""
import json
import re
from collections import deque

from registry import dependency_name
from semver import latest


def read_fixture(path):
    """Прочитать и проверить тестовый граф."""
    with open(path, encoding="utf-8") as source:
        graph = json.load(source)
    if not isinstance(graph, dict):
        raise ValueError("test repository must be a JSON object")
    for name, children in graph.items():
        if not re.fullmatch(r"[A-Z]+", name):
            raise ValueError(f"invalid test package: {name}")
        if not isinstance(children, list) or any(
            not isinstance(child, str) or child not in graph
            for child in children
        ):
            raise ValueError(f"invalid dependencies for {name}")
    return graph


def registry_children(registry, node, include):
    """Загрузить обязательные зависимости общего назначения."""
    name, version = node
    record = registry.exact(name, version)
    for dep in record["deps"]:
        target = dependency_name(dep)
        if (
            not include(target) or dep.get("optional") or dep.get("target")
            or dep.get("kind") == "dev" or dep.get("registry")
        ):
            continue
        selected = latest(registry.records(target), dep["req"])
        yield selected["name"], selected["vers"]


def bfs(root, children, max_depth=None, exclude=None):
    """Вернуть смежность в порядке первого посещения пакетов."""
    graph = {root: []}
    queue = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        if max_depth is not None and depth >= max_depth:
            continue
        for child in dict.fromkeys(children(node)):
            if exclude and exclude in child[0]:
                continue
            graph[node].append(child)
            if child not in graph:
                graph[child] = []
                queue.append((child, depth + 1))
    return graph


def build_graph(args):
    """Подключить тестовый граф или реестр к обходу."""
    if args.test:
        fixture = read_fixture(args.repo)
        if args.package not in fixture:
            raise ValueError(f"test package not found: {args.package}")
        root = (args.package, None)

        def children(node):
            """Вернуть соседей в тестовом графе."""
            return ((name, None) for name in fixture[node[0]])
    else:
        from registry import Registry

        registry = Registry(args.repo)
        record = registry.exact(args.package, args.version)
        root = (record["name"], record["vers"])

        def children(node):
            """Вернуть соседей с выбранными версиями."""
            return registry_children(
                registry, node,
                lambda name: not args.exclude or args.exclude not in name,
            )

    return bfs(root, children, args.max_depth, args.exclude)
