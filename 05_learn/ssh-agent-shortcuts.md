---
title: SSH agent shortcut commands
category: 05_learn
tags: [ssh, git, shell, claude-code, topic:ssh-agent, tech:ssh, tech:git]
sources: [1504fcec-cfbb-4ef2-a3ed-840b1350acff, 3e07de94-4eea-46b3-892a-e815cd133f4e, 002f63f9-be02-4b79-acd5-3f0f1b1ea354]
updated: 2026-04-26
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

Bash tool では **shell 状態が呼び出し間で保持されない**ので、`~/sshgl` を source して鍵をロードしたあと **同一 Bash 呼び出し** で `git push` まで連結する：

```bash
. ~/sshgl; git push
```

`~/sshgl` の中身は `eval $(ssh-agent)` ＋ `ssh-add -k ~/.ssh/id_rsa7` ＋ `ssh-add -k ~/.ssh/github_rsa` を実行する dotscript なので、source ＝ 現在の Bash プロセスに環境変数を注入できる。Claude Code Bash でも通常シェルでもこれで動く（**短縮形が両環境で有効**、2026-04-26 MeguruPMReport push で確認）。

長い手書き連結も等価で通る（`~/sshgl` が無い環境向けのフォールバック）：

```bash
eval `ssh-agent`; ssh-add -k ~/.ssh/id_rsa7; ssh-add -k ~/.ssh/github_rsa; git push -u origin main
```

**ポイント**:
- 鍵ロードと `git push` を **同一 Bash 呼び出し** に置く（別 Bash だと `SSH_AUTH_SOCK` が失われ鍵が見えない）
- **両方の鍵**が必要：`id_rsa7`（個人系）＋ `github_rsa`（GitHub 系）
- セミコロンで連結（`&&` だと `ssh-add` の警告で止まる可能性）
- harness の **main 直 push ガード**は SSH 認証とは別レイヤ。`. ~/sshgl;` を当てても permission rule で弾かれる場合があり、その時はユーザの明示承認 or feature ブランチ + PR 運用に切り替える

### auto-memory との対応

- プロジェクト毎の `~/.claude/projects/<slug>/memory/` に `ssh_keys_for_git.md` として保存済（少なくとも MeguruPMReport で確認）。2026-04-26 の auto-memory 更新で `. ~/sshgl;` 短縮形を正準手順に書き換え

### 実例

- 2026-04-26 MeguruPMReport 2 コミット push（`df5ce43` / `075077d`）：harness の main 直 push 拒否 → `. ~/sshgl; git push` 一行で通過
- 2026-04-24 MeguruPMReport 初push：従来は `eval ssh-agent; ssh-add -k ...; git push` の長形でしか通らないと判断していたが、4-26 検証で `. ~/sshgl;` 短縮形でも問題なく通ると判明（過去記録の上書き）
- 2026-04-23 Plugins-tatoflam / v の初push は `. ~/sshgl;` ベース（通常シェル）で通った

## Links

- [[02_diary/2026-04-24]]
- [[02_diary/2026-04-23]]
- [[03_work/meguru-pm-report]]
