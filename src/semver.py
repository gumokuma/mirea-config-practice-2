"""Сопоставление опубликованных версий с требованиями Cargo."""
import re
from operator import eq, ge, gt, le, lt


FULL_VERSION_PARTS = 3
TILDE_PREFIX_PARTS = 2
COMPARISONS = {"=": eq, ">": gt, "<": lt, ">=": ge, "<=": le}


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
    release = ".".join(map(str, parts + (0,) * (FULL_VERSION_PARTS - width)))
    lower = version_key(release + (prerelease or ""))
    comparison = COMPARISONS.get(operator)
    if comparison is not None:
        if width == FULL_VERSION_PARTS:
            return comparison(candidate, lower)
        return comparison(candidate[0][:width], parts)
    if operator == "~":
        bound = min(width, TILDE_PREFIX_PARTS)
    else:
        bound = next((i + 1 for i, n in enumerate(parts) if n), width)
    return candidate >= lower and candidate[0][:bound] == parts[:bound]


def prerelease_allowed(key, rules):
    """Допустить предварительную версию при совпадении ядра SemVer."""
    release, stable, _ = key
    return stable or any(pre and parts == release for _, parts, pre in rules)


def latest(records, requirement):
    """Найти максимальную доступную версию для одной зависимости."""
    rules = [comparator(text) for text in requirement.split(",")]
    matches = []
    for record in records:
        if record.get("yanked"):
            continue
        key = version_key(record["vers"])
        if not prerelease_allowed(key, rules):
            continue
        if all(compare(key, rule) for rule in rules):
            matches.append(record)
    if not matches:
        raise ValueError(f"no available version matches {requirement}")
    return max(matches, key=lambda record: version_key(record["vers"]))
