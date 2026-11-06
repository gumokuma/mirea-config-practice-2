"""Сопоставление опубликованных версий с требованиями Cargo."""
import re


def version_key(text):
    """Преобразовать SemVer в ключ сортировки."""
    release, _, prerelease = text.split("+", 1)[0].partition("-")
    parts = tuple(map(int, release.split(".")))
    identifiers = tuple(
        (0, int(part)) if part.isdigit() else (1, part)
        for part in prerelease.split(".") if part
    )
    return parts, not prerelease, identifiers


def comparator(text):
    """Разобрать один оператор и версию или шаблон."""
    match = re.fullmatch(
        r"(>=|<=|>|<|=|\^|~)?\s*([0-9]+(?:\.[0-9]+){0,2}|\*)"
        r"(\.\*)?(-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?",
        text.strip(),
    )
    if not match:
        raise ValueError(f"unsupported version requirement: {text}")
    operator, release, wildcard, prerelease = match.groups()
    if release == "*":
        return "*", (), None
    parts = tuple(map(int, release.split(".")))
    return ("=" if wildcard else operator or "^"), parts, prerelease


def compare(candidate, rule):
    """Проверить один оператор Cargo."""
    operator, parts, prerelease = rule
    if operator == "*":
        return True
    width = len(parts)
    release = ".".join(map(str, parts + (0,) * (3 - width)))
    lower = version_key(release + (prerelease or ""))
    partial = candidate[0][:width]
    if operator == "=":
        return candidate == lower if width == 3 else partial == parts
    if operator == ">":
        return candidate > lower if width == 3 else partial > parts
    if operator == "<":
        return candidate < lower if width == 3 else partial < parts
    if operator == ">=":
        return candidate >= lower if width == 3 else partial >= parts
    if operator == "<=":
        return candidate <= lower if width == 3 else partial <= parts
    if operator == "~":
        bound = min(width, 2)
    else:
        bound = next((i + 1 for i, n in enumerate(parts) if n), width)
    return candidate >= lower and candidate[0][:bound] == parts[:bound]


def latest(records, requirement):
    """Найти максимальную доступную версию для одной зависимости."""
    rules = [comparator(text) for text in requirement.split(",")]
    matches = []
    for record in records:
        if record.get("yanked"):
            continue
        key = version_key(record["vers"])
        if not key[1] and not any(
            pre and parts == key[0] for _, parts, pre in rules
        ):
            continue
        if all(compare(key, rule) for rule in rules):
            matches.append(record)
    if not matches:
        raise ValueError(f"no available version matches {requirement}")
    return max(matches, key=lambda record: version_key(record["vers"]))
