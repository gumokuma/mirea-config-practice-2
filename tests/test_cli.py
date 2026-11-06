"""Проверки параметров командной строки."""
import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from main import parse_args


class CliTests(unittest.TestCase):
    """Ошибочные и корректные параметры."""

    def test_defaults(self):
        """Проверить конфигурацию без необязательных аргументов."""
        args = parse_args(["--package", "log", "--version", "0.4.22"])
        self.assertEqual(args.repo, "https://index.crates.io")
        self.assertIsNone(args.max_depth)

    def test_invalid_arguments(self):
        """Ошибки параметров должны возвращать код 2."""
        base = ["--package", "log", "--version", "0.4.22"]
        invalid = [
            ["--package", "../log"], ["--version", "latest"],
            ["--repo", "file:///tmp/index"], ["--test"],
            ["--ascii", "yes"], ["--max-depth", "-1"], ["--exclude", ""],
        ]
        for extra in invalid:
            with self.subTest(extra=extra), contextlib.redirect_stderr(
                io.StringIO()
            ), self.assertRaises(SystemExit) as failure:
                parse_args(base + extra)
            self.assertEqual(failure.exception.code, 2)
