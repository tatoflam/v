---
title: Claude Code hooks behavior
category: 05_learn
tags: [claude-code, hooks, automation]
sources: [8a25326c-5119-438b-bcf3-4c4c7dba4127]
updated: 2026-04-23
---

# Claude Code hooks behavior

## Summary

`SessionEnd` を含む Claude Code フックの実用上の挙動メモ。VS Code 拡張、ヘッドレス起動、再帰防止、permission ガード周り。

## Details

### `SessionEnd` の発火タイミング
- `/exit` を叩いたときだけでなく、**Claude パネルを閉じる／別セッションに切り替える／ウィンドウを閉じる**でも発火する
- VS Code 拡張からでも問題なく走る（`/exit` 相当 UI が無くても OK）

### 設定変更の反映タイミング
- `~/.claude/settings.json` の `hooks` セクションは **セッション開始時に読み込まれる**
- 編集中のセッションには反映されない → 動作確認は「いったん閉じて新セッション開始 → そこから終了」の流れが必要

### 複数 hook の合成
- plugin が登録した SessionEnd hook（例：`plugins-tatoflam` の `enqueue-session.sh`）と、ユーザ設定 `~/.claude/settings.json` 側の SessionEnd hook は **両方走る**
- plugin を改変せずに後段処理を足したい場合、ユーザ側に追加するのが筋

### ヘッドレス（`claude -p`）と permission
- ヘッドレスモードでは Bash/Write の承認プロンプトに人が答えられない
- `--dangerously-skip-permissions` で全 tool 呼び出しを無検査通過させる必要がある
- フラグ範囲は **そのセッション内のすべての tool 呼び出し**。worker 用途で限定して使うのが妥当

### 再帰防止
- SessionEnd で `claude -p ...` を起動すると、その子セッションが終わったときにまた SessionEnd が発火 → 無限ループ
- 環境変数（例 `WIKI_INGEST_WORKER=1`）を export してフック側で `[[ -n "${WIKI_INGEST_WORKER:-}" ]] && exit 0` でガード

### バックグラウンド化
- フックは即座に return しないと UX が固まる
- `( ... ) &` + `disown` で切り離し、ログは `>>` でファイルに送る
- 子プロセスの `stdin` は `</dev/null` で閉じる

## 関連する実装

- `~/.claude/wiki/hooks/auto-ingest-push.sh` — このセオリーをまとめて適用したスクリプト
- ログ：`~/.claude/wiki/state/ingest-worker.log` / `hook-errors.log`

## Links

- [[wiki-automation-pipeline]]
- [[02_diary/2026-04-23]]
