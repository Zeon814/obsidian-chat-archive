# Obsidian Chat Archive

A Codex skill for archiving Codex conversations as Markdown notes in an Obsidian vault.

It saves conversation notes to:

```text
codex/YYYY-MM-DD/<conversation-title>.md
```

## What It Does

- Turns the current Codex conversation into an Obsidian-friendly Markdown note.
- Creates dated folders automatically.
- Sanitizes Windows-invalid filename characters.
- Appends to an existing note by default, or overwrites when requested.
- Writes Markdown as UTF-8 with BOM for better Windows and Obsidian compatibility.

## Installation

Clone this repository into your Codex skills directory:

```powershell
git clone https://github.com/Zeon814/obsidian-chat-archive.git "$env:USERPROFILE\.codex\skills\obsidian-chat-archive"
```

Or clone it anywhere and create a junction into the Codex skills directory:

```powershell
git clone https://github.com/Zeon814/obsidian-chat-archive.git F:\projects\obsidian-chat-archive
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.codex\skills\obsidian-chat-archive" `
  -Target "F:\projects\obsidian-chat-archive"
```

Restart Codex after installation so the skill can be discovered.

## Configuration

Set your Obsidian vault path with an environment variable:

```powershell
$env:OBSIDIAN_VAULT = "D:\Documents\Obsidian Vault"
```

For a persistent user-level setting on Windows:

```powershell
[Environment]::SetEnvironmentVariable("OBSIDIAN_VAULT", "D:\Documents\Obsidian Vault", "User")
```

You can also pass the vault path per command with `--vault`.

## Usage

Ask Codex to save or archive the conversation, for example:

```text
Save this conversation to Obsidian.
Archive this Codex chat as an Obsidian note.
保存这次对话到 Obsidian。
```

The skill will prepare Markdown content and run:

```powershell
python scripts/save_chat.py --vault "<obsidian-vault-path>" --title "<title>" --content-file "<prepared-md-file>"
```

## Script

You can also run the bundled script directly:

```powershell
python scripts/save_chat.py `
  --vault "D:\Documents\Obsidian Vault" `
  --date 2026-05-18 `
  --title "Example Conversation" `
  --content-file ".\example.md"
```

If `--vault` is omitted, the script reads `OBSIDIAN_VAULT`.

By default, an existing note is appended. Use `--overwrite` to replace it:

```powershell
python scripts/save_chat.py --title "Example Conversation" --content-file ".\example.md" --overwrite
```

## Windows Encoding Note

For Chinese or other non-ASCII text on Windows, prefer `--content-file` instead of piping Markdown through PowerShell stdin. Some console encodings can replace non-ASCII text with question marks before Python receives it.

The script reads and writes Markdown with `utf-8-sig` to keep Obsidian and Windows tools happy.

## Limitations

Codex skills are not background hooks. This skill cannot automatically capture every conversation unless the surrounding Codex client invokes it. It works when the user asks Codex to save, archive, export, log, or sync the current conversation to Obsidian.

## License

No license has been added yet. Add one before encouraging broad reuse.
