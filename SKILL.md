---
name: obsidian-chat-archive
description: Archive Codex conversations as Markdown notes in an Obsidian vault. Use when the user asks to save, archive, export, log, record, persist, or sync the current Codex conversation to Obsidian, especially requests involving paths like codex/YYYY-MM-DD/conversation-name.md or the user's default Obsidian vault.
---

# Obsidian Chat Archive

## Overview

Save the current Codex conversation, or a concise reconstruction of it, as a Markdown file in the user's Obsidian vault.

Skills are not background hooks. They cannot guarantee automatic execution for every conversation unless the surrounding Codex client invokes them. When the user wants ongoing capture, explain this boundary briefly and then save the conversation that is available in context.

## Defaults

- Vault root: use the user's requested vault path, the `--vault` argument, or the `OBSIDIAN_VAULT` environment variable.
- Destination pattern: `codex/YYYY-MM-DD/<conversation-title>.md`
- Date source: local current date unless the user gives a date
- Title source: use the user's requested title; otherwise derive a short filesystem-safe Chinese or English title from the conversation topic
- Existing file behavior: append by default; use replacement only when the user explicitly asks to overwrite
- Encoding: write Markdown as UTF-8 with BOM for better Windows and Obsidian compatibility.

## Workflow

1. Determine the note title.
   - Prefer an explicit title from the user.
   - Otherwise generate a concise title of 3-10 words from the conversation's main task.
   - Avoid generic names like `conversation`, `chat`, or `untitled`.
2. Compose the Markdown body.
   - Include YAML frontmatter with `title`, `date`, `source`, and `tags`.
   - Add a short summary section.
   - Add the conversation transcript available in context.
   - If the full earlier transcript is unavailable, state that the note contains the visible/current context and include a faithful summary of missing context instead of inventing verbatim messages.
3. Save with `scripts/save_chat.py`.
   - Pass the title with `--title`.
   - Pass `--vault` unless `OBSIDIAN_VAULT` is already set in the environment.
   - Use `--content-file` for prepared Markdown content.
   - On Windows, avoid piping non-ASCII Markdown through PowerShell stdin because console encoding can replace Chinese text with question marks before Python receives it.
   - Use `--overwrite` only when requested.
4. Report the final note path.

## Script

Use the bundled script from the skill directory:

```powershell
python scripts/save_chat.py --vault '<obsidian-vault-path>' --title '<title>' --content-file '<prepared-md-file>'
```

The script creates missing directories and prints the saved file path. It also sanitizes Windows-invalid filename characters.

## Markdown Shape

Use this structure for the content passed to the script:

```markdown
---
title: "<conversation title>"
date: YYYY-MM-DD
source: "codex"
tags:
  - codex
  - conversation
---

# <conversation title>

## Summary

- ...

## Transcript

### User

...

### Assistant

...
```

Keep tool outputs concise. Summarize long logs instead of pasting noisy command output unless the user explicitly asks for a full transcript.
