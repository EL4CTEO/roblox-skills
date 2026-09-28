#!/usr/bin/env python3
"""Build single-file skills for Roblox Studio Assistant.

Roblox Assistant skills are one Markdown document each (frontmatter: name, description, enabled).
This inlines every file from a skill's references/ directory as an appendix and rewrites links to
point at the appended sections.

Usage: python3 scripts/build-assistant.py [--out dist/assistant] [--no-references] [skill ...]
Then in Studio: Assistant → … → Assistant Settings → Skills → Add, and paste a generated file
(or ask Assistant: "rbx-create-skill" with the file contents).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = text.index("\n---\n", 4)
    fields = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, text[end + 5 :]


def anchor(path: str) -> str:
    return "reference-" + re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-")


def build(skill_dir: Path, include_refs: bool) -> str:
    fields, body = split_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
    refs = sorted((skill_dir / "references").glob("*.md")) if include_refs else []

    for ref in refs:
        rel = f"references/{ref.name}"
        body = body.replace(f"]({rel})", f"](#{anchor(rel)})")

    parts = [
        "---",
        f"name: {fields['name']}",
        f"description: {fields['description']}",
        "enabled: true",
        "---",
        body.strip(),
    ]
    for ref in refs:
        rel = f"references/{ref.name}"
        content = ref.read_text(encoding="utf-8").strip()
        content = re.sub(r"^# ", "### ", content, count=1)  # demote the reference title
        parts.append(f'\n---\n\n<a id="{anchor(rel)}"></a>\n\n## Appendix: {rel}\n\n{content}')
    return "\n".join(parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "assistant"))
    ap.add_argument("--no-references", action="store_true", help="only SKILL.md bodies (smaller)")
    ap.add_argument("skills", nargs="*")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dirs = sorted(d for d in SKILLS.iterdir() if (d / "SKILL.md").exists())
    if args.skills:
        dirs = [d for d in dirs if d.name in args.skills]
        missing = set(args.skills) - {d.name for d in dirs}
        if missing:
            print(f"unknown skills: {', '.join(sorted(missing))}", file=sys.stderr)
            return 1
    for d in dirs:
        target = out / f"{d.name}.md"
        target.write_text(build(d, not args.no_references), encoding="utf-8")
        print(f"{target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
