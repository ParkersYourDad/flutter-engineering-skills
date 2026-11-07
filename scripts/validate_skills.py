#!/usr/bin/env python3
"""Validate Agent Skills metadata and local Markdown links without third-party packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(?<!!)\\[[^\\]]+\\]\\(([^)]+)\\)")


def read_frontmatter(path: Path) -> tuple[str | None, str | None, list[str]]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return None, None, [f"{path.relative_to(ROOT)}: cannot read file: {exc}"]

    if not lines or lines[0].strip() != "---":
        return None, None, [f"{path.relative_to(ROOT)}: missing YAML frontmatter"]

    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, None, [f"{path.relative_to(ROOT)}: unterminated YAML frontmatter"]

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            errors.append(f"{path.relative_to(ROOT)}: invalid frontmatter line: {line}")
            continue
        fields[key.strip()] = value.strip().strip("'\"")

    name = fields.get("name")
    description = fields.get("description")

    if not name:
        errors.append(f"{path.relative_to(ROOT)}: frontmatter name is required")
    elif len(name) > 64 or not NAME_RE.fullmatch(name):
        errors.append(f"{path.relative_to(ROOT)}: invalid skill name: {name!r}")

    if not description:
        errors.append(f"{path.relative_to(ROOT)}: frontmatter description is required")
    elif len(description) > 1024:
        errors.append(f"{path.relative_to(ROOT)}: description exceeds 1024 characters")

    return name, description, errors


def check_local_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip()
        if target.startswith(("https://", "http://", "mailto:", "tel:")):
            continue
        target = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target:
            continue

        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(
                f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}"
            )
            continue

        if not resolved.exists():
            errors.append(
                f"{path.relative_to(ROOT)}: broken local link: {raw_target}"
            )
    return errors


def main() -> int:
    errors: list[str] = []
    skill_files = [ROOT / "SKILL.md"]
    skill_files.extend(sorted((ROOT / "skills").glob("*/SKILL.md")))

    if not (ROOT / "skills").is_dir():
        errors.append("skills/: directory is missing")

    seen_names: dict[str, Path] = {}
    for path in skill_files:
        name, _description, file_errors = read_frontmatter(path)
        errors.extend(file_errors)
        if name:
            if name in seen_names:
                errors.append(
                    f"duplicate skill name {name!r}: "
                    f"{seen_names[name].relative_to(ROOT)} and {path.relative_to(ROOT)}"
                )
            seen_names[name] = path

            if path.parent != ROOT and path.parent.name != name:
                errors.append(
                    f"{path.relative_to(ROOT)}: directory name must match frontmatter name {name!r}"
                )

    markdown_files = sorted(ROOT.rglob("*.md"))
    for path in markdown_files:
        if ".git" in path.parts:
            continue
        errors.extend(check_local_links(path))

    if errors:
        print("Skill validation FAILED:")
        for error in errors:
            print(f"- {error}")
        print(f"{len(errors)} issue(s) found.")
        return 1

    print(f"Skill validation PASSED.")
    print(f"- {len(skill_files)} skill entrypoints validated.")
    print(f"- {len(markdown_files)} Markdown files checked for broken local links.")
    print("- Frontmatter names/descriptions are valid and skill names are unique.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
