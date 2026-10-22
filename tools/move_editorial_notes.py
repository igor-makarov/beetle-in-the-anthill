#!/usr/bin/env python3
"""Move editorial HTML comments out of the transcript body and into the YAML
frontmatter, where they stay in the archive file but stop rendering as visible
escaped text on the site.

An HTML comment in the body is a paragraph to site/build.py, which escapes and
displays it. A comment line in the YAML frontmatter is ignored by the YAML
parser, so the note is preserved on disk and hidden from readers.

Usage: python3 move_editorial_notes.py [--dry-run] <repo-root>
"""
import argparse
import re
import sys
from pathlib import Path

# A comment block: <!-- ... --> possibly spanning lines, at the start of a line.
COMMENT = re.compile(r"^[ \t]*<!--.*?-->[ \t]*$", re.MULTILINE | re.DOTALL)
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def convert(text):
    """Return (new_text, notes_moved)."""
    match = FRONTMATTER.match(text)
    if not match:
        return text, 0
    frontmatter, body = match.group(1), text[match.end():]

    notes = []
    def take(m):
        inner = m.group(0).strip()
        inner = inner[4:-3].strip()          # drop <!-- and -->
        notes.append(inner)
        return "\n"                          # leave a blank line behind
    body = COMMENT.sub(take, body)

    if not notes:
        return text, 0

    # Keep the frontmatter a valid YAML mapping: append comments after it.
    extra = "\n".join("# " + note.replace("\n", " ") for note in notes)
    new_frontmatter = frontmatter.rstrip("\n") + "\n" + extra
    return "---\n" + new_frontmatter + "\n---\n" + body, len(notes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    files = sorted(root.glob("S*/E*.md"))
    total_notes = 0
    changed = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        new_text, count = convert(text)
        if not count:
            continue
        total_notes += count
        changed += 1
        print(f"{path.relative_to(root)}: {count} note(s)")
        if not args.dry_run:
            path.write_text(new_text, encoding="utf-8")
    print(f"\n{changed} file(s), {total_notes} note(s) moved "
          f"{'(dry run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
