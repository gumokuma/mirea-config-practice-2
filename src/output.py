"""Представления графа зависимостей."""
from collections import deque


def label(node):
    """Отобразить имя и, если есть, точную версию пакета."""
    name, version = node
    return f"{name}@{version}" if version else name


def load_order(graph):
    """Вернуть порядок зависимостей и узлы, заблокированные циклом."""
    remaining = {node: len(children) for node, children in graph.items()}
    dependents = {node: [] for node in graph}
    for node, children in graph.items():
        for child in children:
            dependents[child].append(node)
    ready = deque(node for node in graph if remaining[node] == 0)
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for parent in dependents[node]:
            remaining[parent] -= 1
            if remaining[parent] == 0:
                ready.append(parent)
    return order, [node for node in graph if remaining[node]]


def plantuml(graph):
    """Сформировать PlantUML с уникальным идентификатором каждой версии."""
    ids = {node: f"p{i}" for i, node in enumerate(graph)}
    lines = ["@startuml", "left to right direction"]
    for node, alias in ids.items():
        lines.append(f'component "{label(node)}" as {alias}')
    for node, children in graph.items():
        for child in children:
            lines.append(f"{ids[node]} --> {ids[child]}")
    return "\n".join([*lines, "@enduml"])


def ascii_tree(graph):
    """Развернуть вершину один раз, помечая повторные ссылки."""
    root = next(iter(graph))
    lines = [label(root)]
    seen = {root}
    stack = []
    enqueue_children(stack, graph[root], "")
    while stack:
        node, prefix, last = stack.pop()
        branch = "`-- " if last else "|-- "
        if node in seen:
            lines.append(prefix + branch + label(node) + " [seen]")
            continue
        lines.append(prefix + branch + label(node))
        seen.add(node)
        indent = "    " if last else "|   "
        enqueue_children(stack, graph[node], prefix + indent)
    return "\n".join(lines)


def enqueue_children(stack, children, prefix):
    """Положить потомков в стек в обратном порядке вывода."""
    for index in range(len(children) - 1, -1, -1):
        stack.append((children[index], prefix, index == len(children) - 1))
