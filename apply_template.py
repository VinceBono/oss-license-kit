#!/usr/bin/env python3
"""Apply the AGPL + commercial dual-license kit to a repo.

  python apply_template.py --target ../my-repo --project "mcp-opcua" \
      --owner "USTechService Corporation" --contact "licensing@example.com"

Copies template/ into the target, fills in placeholders, and installs the
commitguard pre-commit hook if the target is a git repo. Existing files are
skipped unless --force is given (.gitignore is merged, never replaced).
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template"


def render(text: str, values: dict[str, str]) -> str:
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def merge_gitignore(src: Path, dst: Path) -> None:
    existing = dst.read_text().splitlines() if dst.exists() else []
    have = set(existing)
    new = [l for l in src.read_text().splitlines() if l and not l.startswith("#") and l not in have]
    if new:
        block = ["", "# --- added by license kit ---", *new]
        dst.write_text("\n".join(existing + block).lstrip("\n") + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument("--project", required=True)
    ap.add_argument("--owner", required=True, help='e.g. "USTechService Corporation" or "DarkDataLabs"')
    ap.add_argument("--contact", required=True, help="licensing/security contact email or URL")
    ap.add_argument("--year", default=str(dt.date.today().year))
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--no-hook", action="store_true", help="don't install the git hook")
    args = ap.parse_args()

    target = args.target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    values = {"PROJECT": args.project, "OWNER": args.owner, "CONTACT": args.contact, "YEAR": args.year}

    for src in sorted(TEMPLATE.rglob("*")):
        if src.is_dir() or "__pycache__" in src.parts or src.suffix == ".pyc":
            continue
        rel = src.relative_to(TEMPLATE)
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.name == ".gitignore":
            merge_gitignore(src, dst)
            print(f"merged   {rel}")
            continue
        if dst.exists() and not args.force:
            print(f"skipped  {rel} (exists; use --force)")
            continue
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dst)  # binary: copy verbatim
        else:
            dst.write_text(render(text, values), encoding="utf-8")
            shutil.copymode(src, dst)
        print(f"wrote    {rel}")

    if not args.no_hook and (target / ".git").exists():
        subprocess.run(["sh", str(target / "scripts" / "install-hooks.sh")], cwd=target, check=False)

    print(
        "\nNext: add a README 'License' section, enable the CLA (PR checkbox or cla-assistant.io),"
        "\nand run: python scripts/commitguard.py --all"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
