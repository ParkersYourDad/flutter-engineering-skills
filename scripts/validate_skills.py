#!/usr/bin/env python3
"""Validate Agent Skills metadata and local Markdown links without third-party packages."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def read_frontmatter(path: Path) -> Tuple[Optional[str], Optional[str], List[str]]:
    errors: List[str] = []
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

    fields: Dict[str, str] = {}
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


def check_local_links(path: Path) -> List[str]:
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
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}")
            continue

        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link: {raw_target}")
    return errors


def self_test() -> int:
    global ROOT
    previous_root = ROOT
    try:
        with tempfile.TemporaryDirectory() as directory:
            ROOT = Path(directory).resolve()
            (ROOT / "skills" / "demo-skill").mkdir(parents=True)
            (ROOT / "references").mkdir()
            skill = ROOT / "skills" / "demo-skill" / "SKILL.md"
            skill.write_text(
                "---\nname: demo-skill\ndescription: A valid test skill.\n---\n",
                encoding="utf-8",
            )
            (ROOT / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
            readme = ROOT / "README.md"
            readme.write_text(
                "[valid](references/guide.md)\n"
                "[external](https://example.com)\n"
                "[broken](references/missing.md)\n"
                "[escape](../outside.md)\n",
                encoding="utf-8",
            )

            name, description, errors = read_frontmatter(skill)
            if name != "demo-skill" or not description or errors:
                print("Skill validator self-test FAILED: valid frontmatter was rejected.")
                return 1

            link_errors = check_local_links(readme)
            if len(link_errors) != 2 or not any("broken local link" in e for e in link_errors) or not any("escapes repository" in e for e in link_errors):
                print("Skill validator self-test FAILED: expected broken-link and path-escape findings.")
                for error in link_errors:
                    print("- " + error)
                return 1

            skill.write_text("---\nname: Invalid_Name\n---\n", encoding="utf-8")
            name, _description, errors = read_frontmatter(skill)
            if name != "Invalid_Name" or len(errors) != 2:
                print("Skill validator self-test FAILED: invalid name/description was not rejected.")
                return 1
    finally:
        ROOT = previous_root

    print("Skill validator self-test PASSED (valid/invalid metadata, valid/external links, broken links, and repository path escape).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run built-in validator tests without scanning the repository")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    errors: list[str] = []
    skill_files = [ROOT / "SKILL.md"]
    skill_files.extend(sorted((ROOT / "skills").glob("*/SKILL.md")))

    if not (ROOT / "skills").is_dir():
        errors.append("skills/: directory is missing")

    seen_names: Dict[str, Path] = {}
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
        if ".git" not in path.parts:
            errors.extend(check_local_links(path))

    if errors:
        print("Skill validation FAILED:")
        for error in errors:
            print(f"- {error}")
        print(f"{len(errors)} issue(s) found.")
        return 1

    print("Skill validation PASSED.")
    print(f"- {len(skill_files)} skill entrypoints validated.")
    print(f"- {len(markdown_files)} Markdown files checked for broken local links.")
    print("- Frontmatter names/descriptions are valid and skill names are unique.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
