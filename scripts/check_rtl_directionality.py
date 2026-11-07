#!/usr/bin/env python3
"""Flag common physical-direction Flutter layout APIs in Dart source.

Copy this script into a consuming app's scripts/ directory, then run:
  python3 scripts/check_rtl_directionality.py --root .
Narrow exception syntax (beside the physical argument):
  // rtl-lint: ignore -- reason this coordinate must remain physical
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable, List, Tuple

IGNORE_MARKER = "// rtl-lint: ignore --"
SEARCH_DIRS = ("lib", "test", "integration_test")
PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("EdgeInsets.only with physical horizontal edge", re.compile(r"\bEdgeInsets\.only\s*\([^)]*\b(?:left|right)\s*:", re.DOTALL)),
    ("physical Alignment edge/corner", re.compile(r"\bAlignment\.(?:topLeft|topRight|centerLeft|centerRight|bottomLeft|bottomRight)\b")),
    ("BorderRadius.only with physical corner", re.compile(r"\bBorderRadius\.only\s*\([^)]*\b(?:topLeft|topRight|bottomLeft|bottomRight)\s*:", re.DOTALL)),
    ("Positioned with physical horizontal edge", re.compile(r"\bPositioned\s*\([^)]*\b(?:left|right)\s*:", re.DOTALL)),
    ("physical TextAlign", re.compile(r"\bTextAlign\.(?:left|right)\b")),
)


def dart_files(root: Path) -> Iterable[Path]:
    for directory in SEARCH_DIRS:
        search_root = root / directory
        if search_root.is_dir():
            yield from sorted(search_root.rglob("*.dart"))


def line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def scan(root: Path) -> List[str]:
    violations: List[str] = []
    for path in dart_files(root):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return ["Cannot read {}: {}".format(path, exc)]

        lines = source.splitlines()
        for description, pattern in PATTERNS:
            for match in pattern.finditer(source):
                start_line = line_number(source, match.start())
                argument_line = line_number(source, match.end() - 1)
                exception = lines[argument_line - 1] if 1 <= argument_line <= len(lines) else ""
                ignored = (
                    IGNORE_MARKER in exception
                    and bool(exception.split(IGNORE_MARKER, 1)[1].strip())
                )
                if not ignored:
                    violations.append(
                        "{}:{}: {}. Prefer a Directional API or add a narrow "
                        "same-line exception: {}".format(
                            path.relative_to(root), start_line, description, IGNORE_MARKER
                        )
                    )
    return violations


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "lib").mkdir()
        (root / "test").mkdir()
        (root / "integration_test").mkdir()

        (root / "lib" / "directional.dart").write_text(
            "const padding = EdgeInsetsDirectional.only(start: 8);\\n"
            "const alignment = AlignmentDirectional.centerStart;\\n"
            "const radius = BorderRadiusDirectional.only(topStart: Radius.circular(8));\\n"
            "const textAlign = TextAlign.start;\\n",
            encoding="utf-8",
        )
        if scan(root):
            print("RTL checker self-test FAILED: directional APIs were flagged.")
            return 1

        (root / "test" / "physical.dart").write_text(
            "EdgeInsets.only(left: 8);\\n"
            "Alignment.centerRight;\\n"
            "BorderRadius.only(topLeft: Radius.circular(8));\\n"
            "Positioned(right: 0);\\n"
            "TextAlign.left;\\n",
            encoding="utf-8",
        )
        violations = scan(root)
        if len(violations) != 5:
            print("RTL checker self-test FAILED: expected 5 findings, got {}.".format(len(violations)))
            for violation in violations:
                print("- " + violation)
            return 1

        (root / "test" / "physical.dart").write_text(
            "EdgeInsets.only(left: 8, // rtl-lint: ignore -- physical media scrubber\\n"
            ");\\n",
            encoding="utf-8",
        )
        if scan(root):
            print("RTL checker self-test FAILED: a valid narrow exception was rejected.")
            return 1

    print("RTL checker self-test PASSED (directional APIs, five violations, and narrow exception).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Flutter app root to scan (default: current directory)")
    parser.add_argument("--self-test", action="store_true", help="run built-in checker tests without scanning an app")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    root = args.root.resolve()
    if not root.is_dir():
        print("Flutter project root does not exist: {}".format(root), file=sys.stderr)
        return 2

    violations = scan(root)
    if violations:
        print("RTL directionality check FAILED:")
        for violation in violations:
            print("- " + violation)
        print("{} violation(s) found.".format(len(violations)))
        return 1

    print("RTL directionality check PASSED.")
    print("- Scanned Dart files under lib/, test/, and integration_test/ when present.")
    print("- No common physical-direction layout APIs found without a same-line exception.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
