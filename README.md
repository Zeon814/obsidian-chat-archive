# Obsidian Chat Archive

一个用于把 Codex 对话保存到 Obsidian 的 Codex skill。

默认保存路径结构：

```text
codex/YYYY-MM-DD/<对话标题>.md
```

## 功能

- 将当前 Codex 对话整理为适合 Obsidian 阅读的 Markdown 笔记。
- 自动创建日期目录。
- 自动清理 Windows 文件名中不允许使用的字符。
- 同一段 Codex 对话再次保存时，可以复用同一个 Markdown 文件。
- 默认追加到已有笔记；保存完整对话快照时建议使用覆盖，让一个对话始终对应一个文件。
- 使用 UTF-8 with BOM 写入 Markdown，提升 Windows 和 Obsidian 下的中文兼容性。

## 安装

推荐直接克隆到 Codex skills 目录：

```powershell
git clone https://github.com/Zeon814/obsidian-chat-archive.git "$env:USERPROFILE\.codex\skills\obsidian-chat-archive"
```

也可以克隆到其他目录，再创建 junction 到 Codex skills 目录：

```powershell
git clone https://github.com/Zeon814/obsidian-chat-archive.git F:\projects\obsidian-chat-archive
New-Item -ItemType Junction `
  -Path "$env:USERPROFILE\.codex\skills\obsidian-chat-archive" `
  -Target "F:\projects\obsidian-chat-archive"
```

安装后重启 Codex，让 skill 列表重新加载。

## 配置

建议用环境变量设置 Obsidian vault 路径：

```powershell
$env:OBSIDIAN_VAULT = "D:\Documents\Obsidian Vault"
```

如果希望长期生效，可以写入 Windows 用户级环境变量：

```powershell
[Environment]::SetEnvironmentVariable("OBSIDIAN_VAULT", "D:\Documents\Obsidian Vault", "User")
```

也可以在每次运行脚本时通过 `--vault` 显式传入 vault 路径。

## 使用

在 Codex 对话中直接提出保存需求，例如：

```text
保存这次对话到 Obsidian。
把当前 Codex 对话归档成 Obsidian 笔记。
同步这次聊天到我的 Obsidian。
```

skill 会整理 Markdown 内容，并调用脚本保存：

```powershell
python scripts/save_chat.py --vault "<Obsidian vault 路径>" --title "<对话标题>" --content-file "<准备好的 Markdown 文件>"
```

如果已经设置了 `OBSIDIAN_VAULT`，可以省略 `--vault`。

如果同一段对话之前已经保存过，skill 会优先复用之前的文件路径，并用 `--overwrite` 刷新该文件，避免因为标题变化新建多个 Markdown 文件。

## 脚本用法

也可以直接运行 bundled script：

```powershell
python scripts/save_chat.py `
  --vault "D:\Documents\Obsidian Vault" `
  --date 2026-05-18 `
  --title "示例对话" `
  --content-file ".\example.md"
```

默认行为是追加到已有笔记。若要覆盖已有笔记，使用 `--overwrite`：

```powershell
python scripts/save_chat.py --title "示例对话" --content-file ".\example.md" --overwrite
```

如果要明确复用某个已有文件：

```powershell
python scripts/save_chat.py `
  --title "示例对话" `
  --content-file ".\example.md" `
  --target-file "D:\Documents\Obsidian Vault\codex\2026-05-18\示例对话.md" `
  --overwrite
```

如果在同一天同一段 Codex 对话中再次保存，但当前上下文里没有上次保存路径，可以复用当天最近修改的归档文件：

```powershell
python scripts/save_chat.py --title "示例对话" --content-file ".\example.md" --reuse-latest --overwrite
```

## 中文编码注意事项

在 Windows 上保存中文或其他非 ASCII 内容时，优先使用 `--content-file`，不要把 Markdown 正文通过 PowerShell 管道传给脚本。部分控制台编码会在 Python 收到内容之前把中文替换成问号。

脚本会用 `utf-8-sig` 读取和写入 Markdown，以便兼容 Obsidian 和 Windows 常见工具。

## 限制

Codex skill 不是后台钩子，不能保证每一次对话都自动捕获。它适用于用户明确要求保存、归档、导出、记录或同步当前对话到 Obsidian 的场景。

## 许可证

当前仓库还没有添加许可证。若希望他人明确复用、修改或分发，建议后续添加 MIT 等开源许可证。

