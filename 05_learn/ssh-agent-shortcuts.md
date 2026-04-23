---
title: SSH agent shortcut commands
category: 05_learn
tags: [ssh, git, shell]
sources: [1504fcec-cfbb-4ef2-a3ed-840b1350acff]
updated: 2026-04-23
---

# SSH agent shortcut commands

## Summary

ホームディレクトリ直下に置いてある dotscript を `source` することで、用途別の SSH 鍵を ssh-agent にロードする運用。

## Details

| コマンド | 用途 |
|---|---|
| `. ~/sshgl;` | **GitHub 用** SSH 鍵 (`github_rsa`) を ssh-agent にロード。GitHub への `git push` / `git fetch` 系の前にこれを叩く。 |
| `. ~/sshl;` | 別系統の鍵ロード（GitHub 用ではない） |

GitHub 向け git 操作の直前に `. ~/sshgl;` を流すのが定型。`git push origin main` が permission rule で弾かれた場合は SSH 認証ではなく Claude Code 側のポリシーなので、鍵をロードしても解決しない（混同に注意）。

## Links

- [[02_diary/2026-04-23]]
