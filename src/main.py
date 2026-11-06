"""Точка входа CLI для анализа индекса Cargo."""
import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit

VERSION = (
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def parse_args(argv=None):
    """Разобрать и проверить настройки."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True)
    parser.add_argument("--repo", default="https://index.crates.io")
    parser.add_argument("--version", required=True)
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--ascii", action="store_true", dest="ascii_tree")
    parser.add_argument("--max-depth", type=int)
    parser.add_argument("--exclude")
    args = parser.parse_args(argv)
    name = r"[A-Z]+" if args.test else r"[A-Za-z0-9_-]+"
    if not re.fullmatch(name, args.package):
        parser.error("invalid --package")
    if not re.fullmatch(VERSION, args.version):
        parser.error("--version must be an exact SemVer version")
    if args.max_depth is not None and args.max_depth < 0:
        parser.error("--max-depth must be non-negative")
    if args.exclude is not None and not args.exclude.strip():
        parser.error("--exclude must not be empty")
    if args.test:
        if not Path(args.repo).is_file():
            parser.error("--test requires --repo to name an existing file")
    else:
        try:
            url = urlsplit(args.repo.removeprefix("sparse+"))
        except ValueError:
            parser.error("invalid --repo URL")
        if url.scheme not in {"http", "https"} or not url.hostname:
            parser.error("--repo must be an HTTP(S) Cargo index URL")
    return args


def main():
    """Вывести настройки прототипа."""
    for key, value in vars(parse_args()).items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
