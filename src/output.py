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
