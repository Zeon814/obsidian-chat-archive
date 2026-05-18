#!/usr/bin/env python3
"""Continuously sync Codex session JSONL logs into Obsidian Markdown notes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_VAULT_ENV = "OBSIDIAN_VAULT"
INVALID_FILENAME_CHARS = r'<>:"/\|?*'


def default_sessions_dir() -> Path:
    return Path.home() / ".codex" / "sessions"


def resolve_vault(vault_arg: Optional[str]) -> Path:
    vault = vault_arg or os.environ.get(DEFAULT_VAULT_ENV)
    if not vault:
        raise SystemExit(
            f"Provide --vault or set the {DEFAULT_VAULT_ENV} environment variable."
        )
    return Path(vault)


def slugify_title(title: str, max_len: int = 80) -> str:
    cleaned = title.strip()
    for char in INVALID_FILENAME_CHARS:
        cleaned = cleaned.replace(char, " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    cleaned = cleaned[:max_len].strip(" .")
    return cleaned or "codex-conversation"


def iter_session_files(sessions_dir: Path) -> Iterable[Path]:
    if not sessions_dir.exists():
        return []
    return sessions_dir.rglob("*.jsonl")


def latest_session_file(sessions_dir: Path) -> Path:
    files = [path for path in iter_session_files(sessions_dir) if path.is_file()]
    if not files:
        raise SystemExit(f"No .jsonl session files found under {sessions_dir}.")
    return max(files, key=lambda path: path.stat().st_mtime)


def safe_json_lines(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                # The writer may still be flushing the final line.
                continue
            if isinstance(parsed, dict):
                yield parsed


def content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: List[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if text is None:
            text = item.get("output_text")
        if text is None:
            text = item.get("input_text")
        if isinstance(text, str):
            parts.append(text)
    return "\n\n".join(part for part in parts if part.strip()).strip()


def is_context_bootstrap(text: str) -> bool:
    stripped = text.strip()
    return (
        stripped.startswith("# AGENTS.md instructions")
        or stripped.startswith("<environment_context>")
    )


def parse_session(path: Path, include_bootstrap: bool) -> Tuple[str, str, str, List[Tuple[str, str]]]:
    session_id = path.stem
    started_at = ""
    messages: List[Tuple[str, str]] = []

    for record in safe_json_lines(path):
        record_type = record.get("type")
        payload = record.get("payload")
        if record_type == "session_meta" and isinstance(payload, dict):
            session_id = str(payload.get("id") or session_id)
            started_at = str(payload.get("timestamp") or record.get("timestamp") or "")
            continue
        if record_type != "response_item" or not isinstance(payload, dict):
            continue
        if payload.get("type") != "message":
            continue
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = content_text(payload.get("content"))
        if not text:
            continue
        if not include_bootstrap and role == "user" and is_context_bootstrap(text):
            continue
        messages.append((str(role), text))

    title = derive_title(messages, session_id)
    return session_id, started_at, title, messages


def derive_title(messages: List[Tuple[str, str]], session_id: str) -> str:
    for role, text in messages:
        if role != "user":
            continue
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
        if first_line:
            return slugify_title(first_line, max_len=50)
    return f"Codex Session {session_id[:8]}"


def markdown_escape_code_fence(text: str) -> str:
    return text.replace("```", "``\u200b`")


def render_markdown(
    session_file: Path,
    session_id: str,
    started_at: str,
    title: str,
    messages: List[Tuple[str, str]],
) -> str:
    now = dt.datetime.now().isoformat(timespec="seconds")
    date = dt.date.today().isoformat()
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {date}",
        'source: "codex-session-watcher"',
        f'session_id: "{session_id}"',
        f'session_file: "{session_file}"',
        f'started_at: "{started_at}"',
        f'synced_at: "{now}"',
        "tags:",
        "  - codex",
        "  - conversation",
        "  - synced",
        "---",
        "",
        f"# {title}",
        "",
        "## Metadata",
        "",
        f"- Session ID: `{session_id}`",
        f"- Session file: `{session_file}`",
        f"- Synced at: `{now}`",
        "",
        "## Transcript",
        "",
    ]
    if not messages:
        lines.append("_No user or assistant messages parsed yet._")
    for role, text in messages:
        heading = "User" if role == "user" else "Assistant"
        lines.extend(
            [
                f"### {heading}",
                "",
                "```text",
                markdown_escape_code_fence(text.rstrip()),
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def existing_note(day_dir: Path, session_id: str) -> Optional[Path]:
    short_id = session_id[:8]
    matches = sorted(day_dir.glob(f"*{short_id}*.md"))
    return matches[0] if matches else None


def destination_path(vault: Path, session_id: str, title: str, date: str) -> Path:
    day_dir = vault / "codex" / date
    existing = existing_note(day_dir, session_id)
    if existing:
        return existing
    return day_dir / f"{slugify_title(title)} [{session_id[:8]}].md"


def sync_once(session_file: Path, vault: Path, include_bootstrap: bool) -> Path:
    session_id, started_at, title, messages = parse_session(session_file, include_bootstrap)
    sync_date = dt.date.today().isoformat()
    destination = destination_path(vault, session_id, title, sync_date)
    destination.parent.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(session_file, session_id, started_at, title, messages)
    destination.write_text(markdown, encoding="utf-8-sig")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Watch Codex session JSONL files and sync them to Obsidian."
    )
    parser.add_argument("--vault", help=f"Obsidian vault root. Defaults to ${DEFAULT_VAULT_ENV}.")
    parser.add_argument(
        "--sessions-dir",
        default=str(default_sessions_dir()),
        help="Codex sessions directory. Defaults to ~/.codex/sessions.",
    )
    parser.add_argument("--session-file", help="Specific Codex session JSONL file to sync.")
    parser.add_argument("--interval", type=float, default=3.0, help="Polling interval in seconds.")
    parser.add_argument("--once", action="store_true", help="Sync once and exit.")
    parser.add_argument(
        "--include-bootstrap",
        action="store_true",
        help="Include AGENTS/environment bootstrap messages in the transcript.",
    )
    args = parser.parse_args()

    vault = resolve_vault(args.vault)
    sessions_dir = Path(args.sessions_dir)
    session_file = Path(args.session_file) if args.session_file else latest_session_file(sessions_dir)

    last_state: Optional[Tuple[int, int]] = None
    while True:
        stat = session_file.stat()
        state = (stat.st_size, stat.st_mtime_ns)
        if state != last_state:
            destination = sync_once(session_file, vault, args.include_bootstrap)
            print(destination)
            last_state = state
        if args.once:
            break
        time.sleep(args.interval)
        if not args.session_file:
            latest = latest_session_file(sessions_dir)
            if latest != session_file:
                session_file = latest
                last_state = None

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
