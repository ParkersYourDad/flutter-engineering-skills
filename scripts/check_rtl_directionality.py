#!/usr/bin/env python3
"""Flag common physical-direction Flutter layout APIs in Dart source.

Narrow exception syntax (on the offending line):
  // rtl-lint: ignore -- reason this coordinate must remain physical
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = (ROOT / "lib", ROOT / "test", ROOT / "integration_test")
IGNORE_MARKER = "// rtl-lint: ignore --"
PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("EdgeInsets.only with physical horizontal edge", re.compile(r"\bEdgeInsets\.only\s*\([^)]*\b(?:left|right)\s*:", re.DOTALL)),
    ("physical Alignment edge/corner", re.compile(r"\bAlignment\.(?:topLeft|topRight|centerLeft|centerRight|bottomLeft|bottomRight)\b")),
    ("BorderRadius.only with physical corner", re.compile(r"\bBorderRadius\.only\s*\([^)]*\b(?:topLeft|topRight|bottomLeft|bottomRight)\s*:", re.DOTALL)),
    ("Positioned with physical horizontal edge", re.compile(r"\bPositioned\s*\([^)]*\b(?:left|right)\s*:", re.DOTALL)),
    ("physical TextAlign", re.compile(r"\bTextAlign\.(?:left|right)\b")),
)


def dart_files() -> Iterable[Path]:
    for root in SEARCH_ROOTS:
        if root.is_dir():
            yield from sorted(root.rglob("*.dart"))


def line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def main() -> int:
    violations: List[str] = []
    for path in dart_files():
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print("Cannot read {}: {}".format(path.relative_to(ROOT), exc), file=sys.stderr)
            return 2

        lines = source.splitlines()
        for description, pattern in PATTERNS:
            for match in pattern.finditer(source):
                start_line = line_number(source, match.start())
                end_line = line_number(source, match.end() - 1)
                covered_lines = range(start_line, end_line + 1)
                ignored = any(
                    1 <= number <= len(lines)
                    and IGNORE_MARKER in lines[number - 1]
                    and lines[number - 1].split(IGNORE_MARKER, 1)[1].strip()
                    for number in covered_lines
                )
                if ignored:
                    continue
                violations.append(
                    "{}:{}: {}. Prefer a Directional API or add a narrow same-line "
                    "exception: {}".format(path.relative_to(ROOT), start_line, description, IGNORE_MARKER)
                )

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
