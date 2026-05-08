---
title: PHP ローカル lint — `php -l` + builtin server
category: 05_learn
tags: [topic:php, tech:php, tech:homebrew, topic:claude-code, topic:permissions]
sources: [0a7a9e22-ee7e-4284-a37d-ccf22a9c7cb1]
updated: 2026-05-08
---

# PHP ローカル lint — `php -l` + builtin server

## Summary

mac で PHP スクリプトの構文チェック / 実 HTTP 応答確認をする最小手順。Homebrew で `php` を入れれば `php -l` (lint) と `php -S host:port` (builtin server) が両方揃う。Claude Code セッション内で実 HTTP 検証まで回す場合は **curl が permission ゲートで拒否される** 制約に注意。

## Details

### 1. インストール

```sh
brew install php
php --version   # 確認時点: PHP 8.5.6 (Homebrew)
```

### 2. lint (構文チェックのみ、実行しない)

```sh
php -l /path/to/file.php
# 通れば → No syntax errors detected in /path/to/file.php
```

`php -l` は構文エラーだけ検出。未定義関数・型不整合などは見ない。

### 3. builtin server で実 HTTP 応答を見る

```sh
php -S 127.0.0.1:8765 -t /path/to/docroot
# 別ターミナルで curl -i http://127.0.0.1:8765/health.php
```

ビルトインサーバは単一プロセス・シングルスレッド。本番用途ではなく、開発時の応答確認用途のみ。

### 4. Claude Code 内での gotcha — curl 権限

Claude Code セッション内で `php -S` を起動して別の Bash で `curl` を叩こうとすると、デフォルト設定だと **curl が permission denied で弾かれる** ことがある。

- 回避策: `~/.claude/settings.json` の permissions に `Bash(curl:*)` 系を allow 追加 (`/fewer-permission-prompts` や `/update-config` で設定可)
- もしくはサーバ起動 → ホスト OS のターミナルで curl を実行

→ lint だけで済むなら `php -l` で完結、HTTP 応答まで見る場合は権限設定を先に整える

## Links

- [[02_diary/2026-05-08]] — 初回ラン記録 (session 0a7a9e22)
- [[05_learn/local-first-anthropic-ops]] — ローカル実行優先の運用原則
