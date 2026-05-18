#!/usr/bin/env python3
"""Save a Codex conversation markdown note into an Obsidian vault."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import Optional


DEFAULT_VAULT_ENV = "OBSIDIAN_VAULT"
INVALID_FILENAME_CHARS = r'<>:"/\|?*'


def slugify_title(title: str) -> str:
    cleaned = title.strip()
    for char in INVALID_FILENAME_CHARS:
        cleaned = cleaned.replace(char, " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or "codex-conversation"


def read_content(args: argparse.Namespace) -> str:
    if args.content_file:
        return Path(args.content_file).read_text(encoding="utf-8-sig")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide markdown content with --content-file or stdin.")


def append_or_write(path: Path, content: str, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.rstrip() + "\n"
    if path.exists() and not overwrite:
        existing = path.read_text(encoding="utf-8-sig")
        separator = "\n\n---\n\n"
        path.write_text(existing.rstrip() + separator + normalized, encoding="utf-8-sig")
    else:
        path.write_text(normalized, encoding="utf-8-sig")


def resolve_vault(vault_arg: Optional[str]) -> Path:
    vault = vault_arg or os.environ.get(DEFAULT_VAULT_ENV)
    if not vault:
        raise SystemExit(
            f"Provide --vault or set the {DEFAULT_VAULT_ENV} environment variable."
        )
    return Path(vault)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Save a Codex conversation markdown note into an Obsidian vault."
    )
    parser.add_argument("--title", required=True, help="Conversation title / note filename.")
    parser.add_argument(
        "--vault",
        help=f"Obsidian vault root. Defaults to ${DEFAULT_VAULT_ENV} when set.",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Date folder in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument("--content-file", help="Markdown content file to save.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing note instead of appending a new section.",
    )
    args = parser.parse_args()

    try:
        dt.date.fromisoformat(args.date)
    except ValueError as exc:
        raise SystemExit("--date must use YYYY-MM-DD format.") from exc

    filename = slugify_title(args.title) + ".md"
    destination = resolve_vault(args.vault) / "codex" / args.date / filename
    append_or_write(destination, read_content(args), args.overwrite)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
