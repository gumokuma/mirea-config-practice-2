"""Чтение строк JSON из разреженного индекса Cargo."""
import json
from functools import cache
from urllib.request import urlopen


def index_path(name):
    """Построить относительный путь записи crate."""
    name = name.lower()
    if len(name) <= 2:
        return f"{len(name)}/{name}"
    if len(name) == 3:
        return f"3/{name[0]}/{name}"
    return f"{name[:2]}/{name[2:4]}/{name}"


class Registry:
    """Предоставляет записи версий из HTTP-индекса."""

    def __init__(self, url):
        self.url = url.removeprefix("sparse+").rstrip("/")

    @cache
    def records(self, name):
        """Получить и кэшировать строки индекса пакета."""
        with urlopen(f"{self.url}/{index_path(name)}", timeout=15) as reply:
            return [json.loads(line) for line in reply if line.strip()]

    def exact(self, name, version):
        """Вернуть запись версии, указанной пользователем."""
        for record in self.records(name):
            if record["vers"] == version:
                return record
        raise ValueError(f"version not found: {name}@{version}")


def dependency_name(dependency):
    """Вернуть имя crate с учётом переименования."""
    return dependency.get("package") or dependency["name"]
