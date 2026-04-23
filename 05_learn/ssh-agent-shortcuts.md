---
title: SSH agent shortcut commands
category: 05_learn
tags: [ssh, git, shell, claude-code]
sources: [1504fcec-cfbb-4ef2-a3ed-840b1350acff, 3e07de94-4eea-46b3-892a-e815cd133f4e]
updated: 2026-04-24
---

# SSH agent shortcut commands

## Summary

GitHub への git 操作を Claude Code 経由で通すには、**ssh-agent の起動 → 鍵ロード → git コマンドを同一 Bash 呼び出しに連結** する必要がある。Bash tool は呼び出し間で shell 状態（環境変数 `SSH_AUTH_SOCK` 等）を保持しないため、別々の Bash 呼び出しで `ssh-add` してから `git push` しても認証に失敗する。

## Details

### 通常シェル運用の dotscript

| コマンド | 用途 |
|---|---|
| `. ~/sshgl;` | **GitHub 用** SSH 鍵 (`github_rsa`) を ssh-agent にロード |
| `. ~/sshl;` | 別系統の鍵ロード（GitHub 用ではない） |

通常ターミナルではこれを流してから `git push` すればよい。`git push origin main` が permission rule で弾かれた場合は SSH 認証ではなく Claude Code 側のポリシーなので、鍵をロードしても解決しない（混同に注意）。

### Claude Code 経由の git push

Bash tool では **shell 状態が呼び出し間で保持されない**ので、一行に連結して実行する：

```bash
eval `ssh-agent`; ssh-add -k ~/.ssh/id_rsa7; ssh-add -k ~/.ssh/github_rsa; git push -u origin main
```

**ポイント**:
- `eval \`ssh-agent\`` で新しい agent を起動して環境変数を現セッションに注入
- **両方の鍵**が必要：`id_rsa7`（個人系）＋ `github_rsa`（GitHub 系）
- セミコロンで連結（`&&` だと `ssh-add` の警告で止まる可能性）
- 分けて実行すると 2回目の Bash で `SSH_AUTH_SOCK` が失われ鍵が見えない

### auto-memory との対応

- プロジェクト毎の `~/.claude/projects/<slug>/memory/` に `ssh_keys_for_git.md` として保存済（少なくとも MeguruPMReport で確認）

### 実例

- 2026-04-24 MeguruPMReport 初push で発見。ハーネスの main 直 push ガードをクリアした直後、SSH 認証で失敗 → この連結で通った。
- 2026-04-23 Plugins-tatoflam / v の初push は `. ~/sshgl;` ベースで通ったが、それは通常シェルで実行したため。

## Links

- [[02_diary/2026-04-24]]
- [[02_diary/2026-04-23]]
- [[03_work/meguru-pm-report]]
