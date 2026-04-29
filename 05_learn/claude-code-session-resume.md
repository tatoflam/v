---
title: Claude Code セッション再開コマンド
category: 05_learn
tags: [topic:claude-code, claude-code, resume, continue, vscode]
sources: [9d35dac4-9c38-4e79-9d15-8df17f6becfe]
updated: 2026-04-29
---

# Claude Code セッション再開コマンド

## Summary

前回の Claude Code セッションを再開する 3 つの導線。CLI の `--continue` / `--resume` と VS Code 拡張のセッションピッカー。VS Code のピッカーは `--resume <sessionId>` 相当。

## Details

### CLI からの再開
- **`claude --continue`（短縮 `claude -c`）** — 直前のセッションを問答無用で再開。最短経路。
- **`claude --resume`（短縮 `claude -r`）** — セッション一覧 UI が出て、過去のセッションから 1 つ選んで再開。

### Claude Code 内からの再開
- **`/resume`** — 既に Claude Code 内にいる場合、別セッションへ切り替える。

### VS Code 拡張のセッションピッカー
- 拡張 UI からセッション履歴を選んで開く動作は **`claude --resume <sessionId>` 相当**。
- 一覧から 1 つ明示的に選ぶ仕様なので、`-c`（直近セッション自動再開）ではなく `--resume` の挙動。
- 選んだセッションが「たまたま直近のもの」だった場合は結果的に `-c` と同じになる。

### 使い分け
- 直近の続きをそのまま → `claude -c`
- 過去セッションから選び直す → `claude -r` または VS Code ピッカー
- すでに別セッションにいる → `/resume`

## see also
- [[05_learn/claude-code-hooks]]
